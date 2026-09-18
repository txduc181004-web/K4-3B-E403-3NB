import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd
import streamlit as st


# ============================================================
# PROJECT PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


from app.analyzer import MODEL, analyze_batch
from app.signal_classifier import classify_signal
from app.topic_normalizer import normalize_topic


# ============================================================
# CONFIG
# ============================================================

DATA_PATH = Path(
    os.getenv(
        "VLEARN_GAP_MAP_PATH",
        str(BASE_DIR / "data" / "sample" / "gap_map.json"),
    )
)

st.set_page_config(
    page_title="VLearn — Class Gap Map",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# DATA HELPERS
# ============================================================

@st.cache_data
def load_gap_map():
    if not DATA_PATH.exists():
        return None

    with DATA_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def format_number(value):
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return "0"


def safe_float(value, default=0.0):
    """Return a valid severity score on the 0–5 scale.

    Ollama usually returns an integer, but a model can also return strings such
    as ``"4"`` or ``"4/5"``.  Treating those strings as 0 was causing high
    severity questions in uploaded CSV files to be rendered as low severity.
    """
    if isinstance(value, bool):
        return default

    if isinstance(value, (int, float)):
        score = float(value)
    elif isinstance(value, str):
        match = re.search(r"-?\d+(?:\.\d+)?", value.strip().replace(",", "."))
        if not match:
            return default
        score = float(match.group())
    else:
        return default

    if score < 0:
        return 0.0
    if score > 5:
        return 5.0
    return score


def has_severity(value):
    """Whether the AI actually supplied a severity value."""
    if isinstance(value, bool) or value is None:
        return False
    if isinstance(value, (int, float)):
        return True
    return isinstance(value, str) and bool(
        re.search(r"-?\d+(?:\.\d+)?", value)
    )


def severity_text(value, include_score=True):
    """Format the score and its human-readable level consistently."""
    score = safe_float(value)
    label = severity_label(score)

    if not include_score:
        return label

    score_text = str(int(score)) if score.is_integer() else f"{score:.1f}"
    return f"{score_text}/5 — {label}"


def severity_label(value):
    value = safe_float(value)

    if value == 0:
        return "Chưa xác định"

    if value >= 4:
        return "Cao"

    if value >= 3:
        return "Trung bình"

    return "Thấp"


def severity_color(value):
    value = safe_float(value)

    if value == 0:
        return "⚪"

    if value >= 4:
        return "🔴"

    if value >= 3:
        return "🟡"

    return "🟢"


def get_topics(data):
    if not isinstance(data, dict):
        return []

    topics = data.get("topics", [])

    return sorted(
        topics,
        key=lambda x: (
            x.get("topic") == "Other",
            -int(x.get("signal_count", 0)),
        ),
    )


def get_evidence(topic):
    evidence = topic.get("evidence", [])

    if isinstance(evidence, list):
        return evidence

    return []


def get_lecture_name(lecture):
    if not isinstance(lecture, dict):
        return "Unknown lecture"

    code = str(
        lecture.get("lecture_code", "")
    ).strip()

    title = str(
        lecture.get("lecture_title", "")
    ).strip()

    if code and title and code != title:
        return f"{code} — {title}"

    return code or title or "Unknown lecture"


# ============================================================
# LIVE METADATA
# ============================================================

def attach_live_metadata(results, input_rows):
    """
    Attach metadata from the input CSV/dataframe to the
    corresponding AI result.

    This is needed because the live Streamlit path calls
    analyze_batch() directly.
    """

    metadata = {}

    for _, row in input_rows.iterrows():

        turn_id = str(
            row.get("turn_id", "")
        ).strip()

        metadata[turn_id] = {
            "turn_id": turn_id,
            "student": str(
                row.get("student", "")
            ).strip(),
            "lecture_code": str(
                row.get("lecture_code", "")
            ).strip(),
            "lecture_title": str(
                row.get("lecture_title", "")
            ).strip(),
            "student_question": str(
                row.get("student_question", "")
            ).strip(),
        }

    enriched = []

    for item in results:

        if not isinstance(item, dict):
            continue

        item = dict(item)

        turn_id = str(
            item.get("turn_id", "")
        ).strip()

        if turn_id in metadata:

            for key, value in metadata[turn_id].items():

                if not item.get(key):
                    item[key] = value

        enriched.append(item)

    return enriched


# ============================================================
# LIVE AGGREGATOR
# ============================================================

def build_gap_map_from_results(results):
    """
    Temporary in-memory version of aggregator.py.

    Important:
    - Does NOT overwrite gap_map.json.
    - Uses the same classifier as the offline pipeline.
    - Uses the same topic normalizer as the offline pipeline.
    - Produces the same general structure as gap_map.json.
    """

    skipped_non_signals = 0
    skipped_none_signals = 0

    skipped_non_learning = Counter()

    grouped = defaultdict(list)

    # --------------------------------------------------------
    # PROCESS EACH AI RESULT
    # --------------------------------------------------------

    for item in results:

        if not isinstance(item, dict):
            continue

        # ----------------------------------------------------
        # 1. AI says this is not a signal
        # ----------------------------------------------------

        if not item.get("is_signal", False):

            skipped_non_signals += 1

            continue

        # ----------------------------------------------------
        # 2. Signal type NONE
        # ----------------------------------------------------

        signal_type = str(
            item.get("signal_type", "")
        ).strip()

        if signal_type == "NONE":

            skipped_none_signals += 1

            continue

        # ----------------------------------------------------
        # 3. CLASSIFY SIGNAL SCOPE
        # ----------------------------------------------------

        signal_scope = classify_signal(item)

        if signal_scope != "LEARNING_GAP":

            skipped_non_learning[
                signal_scope
            ] += 1

            continue

        # ----------------------------------------------------
        # 4. EXTRACT METADATA
        # ----------------------------------------------------

        lecture_code = str(
            item.get("lecture_code", "")
        ).strip()

        lecture_title = str(
            item.get("lecture_title", "")
        ).strip()

        raw_topic = str(
            item.get("topic", "")
        ).strip()

        question = str(
            item.get("student_question", "")
        ).strip()

        # ----------------------------------------------------
        # 5. NORMALIZE TOPIC
        # ----------------------------------------------------

        canonical_topic = normalize_topic(
            raw_topic,
            lecture_title,
            question,
        )

        # ----------------------------------------------------
        # 6. SAVE LEARNING SIGNAL
        # ----------------------------------------------------

        grouped[canonical_topic].append(
            {
                "turn_id": item.get("turn_id"),
                "student": item.get("student"),
                "lecture_code": lecture_code,
                "lecture_title": lecture_title,
                "question": question,
                "signal_type": signal_type,
                "signal_scope": signal_scope,
                "severity": item.get(
                    "severity",
                    0,
                ),
                "reason": item.get(
                    "reason",
                    "",
                ),
                "raw_topic": raw_topic,
            }
        )

    # ========================================================
    # BUILD TOPICS
    # ========================================================

    topics = []

    for canonical_topic, signals in grouped.items():

        # ----------------------------------------------------
        # UNIQUE STUDENTS
        # ----------------------------------------------------

        students = {
            str(x["student"])
            for x in signals
            if x.get("student")
        }

        # ----------------------------------------------------
        # SIGNAL TYPES
        # ----------------------------------------------------

        signal_types = Counter(
            x["signal_type"]
            for x in signals
            if x.get("signal_type")
        )

        # ----------------------------------------------------
        # SEVERITY
        # ----------------------------------------------------

        severities = [
            safe_float(x.get("severity"))
            for x in signals
            if has_severity(x.get("severity"))
        ]

        average_severity = (
            sum(severities) / len(severities)
            if severities
            else 0
        )

        # ----------------------------------------------------
        # LECTURE BREAKDOWN
        # ----------------------------------------------------

        lecture_groups = defaultdict(list)

        for signal in signals:

            key = (
                signal["lecture_code"],
                signal["lecture_title"],
            )

            lecture_groups[key].append(signal)

        lectures = []

        for (
            lecture_code,
            lecture_title,
        ), lecture_signals in lecture_groups.items():

            lecture_students = {
                str(x["student"])
                for x in lecture_signals
                if x.get("student")
            }

            lecture_severities = [
                safe_float(x.get("severity"))
                for x in lecture_signals
                if has_severity(x.get("severity"))
            ]

            lecture_average = (
                sum(lecture_severities)
                / len(lecture_severities)
                if lecture_severities
                else 0
            )

            lectures.append(
                {
                    "lecture_code": lecture_code,
                    "lecture_title": lecture_title,
                    "signal_count": len(
                        lecture_signals
                    ),
                    "student_count": len(
                        lecture_students
                    ),
                    "average_severity": round(
                        lecture_average,
                        2,
                    ),
                }
            )

        lectures.sort(
            key=lambda x: (
                -x["signal_count"],
                -x["student_count"],
                -x["average_severity"],
            )
        )

        # ----------------------------------------------------
        # EVIDENCE
        # ----------------------------------------------------

        evidence = sorted(
            signals,
            key=lambda x: -safe_float(
                x.get("severity")
            ),
        )[:5]

        clean_evidence = []

        for item in evidence:

            clean_evidence.append(
                {
                    "turn_id": item["turn_id"],
                    "student": item["student"],
                    "lecture_code": item["lecture_code"],
                    "lecture_title": item["lecture_title"],
                    "question": item["question"],
                    "student_question": item["question"],
                    "signal_type": item["signal_type"],
                    "signal_scope": item["signal_scope"],
                    "severity": item["severity"],
                    "reason": item["reason"],
                }
            )

        # ----------------------------------------------------
        # TOPIC RECORD
        # ----------------------------------------------------

        topics.append(
            {
                "topic": canonical_topic,
                "signal_count": len(signals),
                "student_count": len(students),
                "average_severity": round(
                    average_severity,
                    2,
                ),
                "signal_types": dict(
                    signal_types
                ),
                "lectures": lectures,
                "evidence": clean_evidence,
            }
        )

    # ========================================================
    # SORT TOPICS
    # ========================================================

    topics.sort(
        key=lambda x: (
            -x["signal_count"],
            -x["student_count"],
            -x["average_severity"],
        )
    )

    # ========================================================
    # FINAL LIVE MAP
    # ========================================================

    valid_signals = sum(
        len(x)
        for x in grouped.values()
    )

    total_non_learning = sum(
        skipped_non_learning.values()
    )

    return {
        "model": MODEL,
        "source_results": len(results),
        "valid_learning_gap_signals": valid_signals,
        "valid_signal_results": valid_signals,
        "skipped_non_signals": skipped_non_signals,
        "skipped_none_signals": skipped_none_signals,
        "skipped_non_learning": total_non_learning,
        "non_learning_breakdown": dict(
            skipped_non_learning
        ),
        "total_topics": len(topics),
        "topics": topics,
    }


# ============================================================
# UI HELPERS
# ============================================================

def calculate_overall_severity(topics):
    """Calculate the average for questions, not an unweighted topic average."""
    weighted_total = 0.0
    signal_total = 0

    for topic in topics:
        try:
            signal_count = max(0, int(topic.get("signal_count", 0)))
        except (TypeError, ValueError):
            signal_count = 0
        if signal_count == 0:
            continue
        weighted_total += safe_float(topic.get("average_severity")) * signal_count
        signal_total += signal_count

    if signal_total == 0:
        return 0

    return weighted_total / signal_total


def render_topic_detail(selected, title="Chủ đề"):

    topic_name = selected.get("topic", "Chủ đề không xác định")
    signal_count = selected.get("signal_count", 0)
    student_count = selected.get("student_count", 0)
    severity = safe_float(selected.get("average_severity", 0))
    sev_icon = severity_color(severity)

    # ── Header ──────────────────────────────────────────────
    st.markdown(
        f'<div class="detail-header">{topic_name}</div>',
        unsafe_allow_html=True,
    )
    st.caption(title)

    # ── 3 metrics chính ─────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Số sinh viên có thắc mắc", format_number(student_count))
    with c2:
        st.metric("Số câu hỏi liên quan", format_number(signal_count))
    with c3:
        st.metric(
            "Mức độ nghiêm trọng",
            f"{sev_icon} {severity_text(severity)}",
            help="Thấp: 1–2 · Trung bình: 3 · Cao: 4–5",
        )

    st.divider()

    # ── Bài giảng liên quan ─────────────────────────────────
    lectures = selected.get("lectures", [])
    if lectures:
        st.markdown('<div class="section-label">📚 Bài giảng liên quan</div>', unsafe_allow_html=True)
        for lecture in lectures:
            lname = get_lecture_name(lecture)
            lsig  = lecture.get("signal_count", lecture.get("signals", 0))
            lstud = lecture.get("student_count", lecture.get("students", 0))
            lsev  = safe_float(lecture.get("average_severity", 0))
            lcls  = severity_class(lsev)
            st.markdown(
                f"""
                <div class="lecture-row">
                    <span class="lecture-name">📖 {lname}</span>
                    <span class="lecture-meta">
                        👤 {format_number(lstud)} sinh viên &nbsp;·&nbsp;
                        💬 {format_number(lsig)} câu hỏi &nbsp;·&nbsp;
                        <span class="stat-pill {lcls}" style="padding:2px 8px">
                            {severity_color(lsev)} {severity_text(lsev)}
                        </span>
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ── Loại thắc mắc ───────────────────────────────────────
    signal_types = selected.get("signal_types", {})
    if signal_types:
        st.markdown('<div class="section-label">🔍 Sinh viên đang gặp khó khăn gì?</div>', unsafe_allow_html=True)
        type_cols = st.columns(min(4, len(signal_types)))
        labels_vi = {
            "CONCEPTUAL_GAP":  "Chưa hiểu khái niệm",
            "PROCEDURAL_GAP":  "Chưa biết cách làm",
            "APPLICATION_GAP": "Chưa biết áp dụng",
            "METACOGNITIVE":   "Phương pháp học",
        }
        for idx, (stype, cnt) in enumerate(signal_types.items()):
            label = labels_vi.get(stype, stype.replace("_", " ").title())
            with type_cols[idx % len(type_cols)]:
                st.metric(label, format_number(cnt))

    st.divider()

    # ── Câu hỏi thực tế từ sinh viên ────────────────────────
    evidence = get_evidence(selected)
    st.markdown(
        f'<div class="section-label">💬 Câu hỏi thực tế từ sinh viên ({len(evidence)} ví dụ tiêu biểu)</div>',
        unsafe_allow_html=True,
    )

    if not evidence:
        st.info("Chưa có câu hỏi nào được ghi nhận.")
    else:
        for idx, item in enumerate(evidence, start=1):
            if not isinstance(item, dict):
                st.markdown(
                    f'<div class="evidence-card low"><div class="evidence-question">"{item}"</div></div>',
                    unsafe_allow_html=True,
                )
                continue

            question     = item.get("student_question", item.get("question", ""))
            reason       = item.get("reason", "")
            student      = item.get("student", "")
            lecture_title = item.get("lecture_title", "")
            item_sev     = item.get("severity", "")
            item_sev_f   = safe_float(item_sev)
            item_cls     = severity_class(item_sev_f)
            item_icon    = severity_color(item_sev_f)
            stype        = item.get("signal_type", "")
            stype_vi     = {
                "CONCEPTUAL_GAP":  "Chưa hiểu khái niệm",
                "PROCEDURAL_GAP":  "Chưa biết cách làm",
                "APPLICATION_GAP": "Chưa biết áp dụng",
                "METACOGNITIVE":   "Phương pháp học",
            }.get(stype, stype.replace("_", " ").title() if stype else "")

            # Meta line
            meta_parts = []
            if student:
                meta_parts.append(f"👤 {student}")
            if lecture_title:
                meta_parts.append(f"📖 {lecture_title}")
            if stype_vi:
                meta_parts.append(f"🏷 {stype_vi}")
            if has_severity(item_sev):
                meta_parts.append(
                    f"{item_icon} Mức độ: {severity_text(item_sev_f)}"
                )
            meta_line = " &nbsp;·&nbsp; ".join(meta_parts)

            # Reasoning box
            reason_html = (
                f'<div class="evidence-reasoning">💡 <strong>Nhận xét của AI:</strong> {reason}</div>'
                if reason else ""
            )

            q_display = question if question else "(Không có nội dung câu hỏi)"

            st.markdown(
                f"""
                <div class="evidence-card {item_cls}">
                    <div class="evidence-question">"{q_display}"</div>
                    <div class="evidence-meta">{meta_line}</div>
                    {reason_html}
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.divider()


def filter_topics(
    topics,
    search,
    sort_mode,
    severity_filter,
):

    filtered = []

    for topic in topics:

        topic_name = str(
            topic.get(
                "topic",
                "",
            )
        )

        if search:

            if (
                search.lower()
                not in topic_name.lower()
            ):
                continue

        severity = safe_float(
            topic.get(
                "average_severity",
                0,
            )
        )

        if (
            severity_filter == "High (≥ 4)"
            and severity < 4
        ):
            continue

        if (
            severity_filter
            == "Medium (3–3.99)"
            and not (
                3 <= severity < 4
            )
        ):
            continue

        if (
            severity_filter == "Low (< 3)"
            and severity >= 3
        ):
            continue

        filtered.append(
            topic
        )

    # --------------------------------------------------------
    # SORT
    # --------------------------------------------------------

    if sort_mode == "Most signals":

        filtered.sort(
            key=lambda x: x.get(
                "signal_count",
                0,
            ),
            reverse=True,
        )

    elif sort_mode == "Most students":

        filtered.sort(
            key=lambda x: x.get(
                "student_count",
                0,
            ),
            reverse=True,
        )

    elif sort_mode == "Highest severity":

        filtered.sort(
            key=lambda x: safe_float(
                x.get(
                    "average_severity",
                    0,
                )
            ),
            reverse=True,
        )

    else:

        filtered.sort(
            key=lambda x: str(
                x.get(
                    "topic",
                    "",
                )
            ).lower()
        )

    # --------------------------------------------------------
    # OTHER AT BOTTOM
    # --------------------------------------------------------

    other_topics = [
        t
        for t in filtered
        if t.get("topic") == "Other"
    ]

    filtered = [
        t
        for t in filtered
        if t.get("topic") != "Other"
    ]

    filtered.extend(
        other_topics
    )

    return filtered


def severity_class(value):
    """Return CSS class name matching severity level."""
    value = safe_float(value)
    if value == 0:
        return "unknown"
    if value >= 4:
        return "high"
    if value >= 3:
        return "medium"
    return "low"


def render_topic_cards(topics, prefix):

    if not topics:
        st.info("Không tìm thấy chủ đề nào phù hợp.")
        return

    for row_start in range(0, len(topics), 2):
        row_topics = topics[row_start : row_start + 2]
        columns = st.columns(2)

        for column, topic in zip(columns, row_topics):
            with column:
                name = topic.get("topic", "Unknown")
                signals = topic.get("signal_count", 0)
                students = topic.get("student_count", 0)
                severity = safe_float(topic.get("average_severity", 0))
                sev_cls = severity_class(severity)
                sev_icon = severity_color(severity)
                evidence = get_evidence(topic)

                preview = ""
                if evidence:
                    first = evidence[0]
                    if isinstance(first, dict):
                        preview = first.get(
                            "student_question",
                            first.get("question", ""),
                        )
                    else:
                        preview = str(first)
                    if len(preview) > 120:
                        preview = preview[:120] + "..."

                preview_html = (
                    f'<div class="topic-preview">"{preview}"</div>'
                    if preview
                    else ""
                )

                st.markdown(
                    f"""
                    <div class="topic-card">
                        <div class="topic-name">{name}</div>
                        <div class="topic-stats">
                            <span class="stat-pill">
                                \U0001f465 {format_number(students)} sinh viên
                            </span>
                            <span class="stat-pill">
                                \U0001f4ac {format_number(signals)} câu hỏi
                            </span>
                            <span class="stat-pill {sev_cls}">
                                {sev_icon} Mức độ: {severity_text(severity)}
                            </span>
                        </div>
                        {preview_html}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if st.button(
                    "Xem chi tiết →",
                    key=f"{prefix}_view_{name}",
                    use_container_width=True,
                ):
                    if prefix == "live":
                        st.session_state["live_selected_topic"] = name
                    else:
                        st.session_state["selected_topic"] = name
                    st.rerun()



# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ---- Typography ---- */
    .main-title {
        font-size: 2rem;
        font-weight: 800;
        color: #1e3a5f;
        margin-bottom: 0.15rem;
    }

    .subtitle {
        color: #6b7280;
        font-size: 1rem;
        margin-bottom: 1.2rem;
    }

    /* ---- Topic card (list view) ---- */
    .topic-card {
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 18px 20px 14px 20px;
        margin-bottom: 12px;
        background: #ffffff;
        transition: box-shadow 0.15s;
    }

    .topic-card:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
    }

    .topic-name {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1e3a5f;
        margin-bottom: 6px;
    }

    .topic-stats {
        display: flex;
        gap: 16px;
        flex-wrap: wrap;
        margin-bottom: 10px;
    }

    .stat-pill {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        font-size: 0.85rem;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 20px;
        background: #f3f4f6;
        color: #374151;
    }

    .stat-pill.high   { background: #fee2e2; color: #991b1b; }
    .stat-pill.medium { background: #fef9c3; color: #854d0e; }
    .stat-pill.low    { background: #dcfce7; color: #166534; }
    .stat-pill.unknown { background: #f3f4f6; color: #6b7280; }

    .topic-preview {
        font-size: 0.88rem;
        color: #6b7280;
        font-style: italic;
        margin-top: 6px;
        line-height: 1.5;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    /* ---- Detail view ---- */
    .detail-header {
        font-size: 1.6rem;
        font-weight: 800;
        color: #1e3a5f;
        margin-bottom: 0.3rem;
    }

    .section-label {
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #9ca3af;
        margin-bottom: 10px;
        margin-top: 20px;
    }

    /* ---- Evidence card ---- */
    .evidence-card {
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 16px 18px;
        margin-bottom: 12px;
        background: #fafafa;
    }

    .evidence-card.high   { border-left: 4px solid #ef4444; }
    .evidence-card.medium { border-left: 4px solid #f59e0b; }
    .evidence-card.low    { border-left: 4px solid #22c55e; }
    .evidence-card.unknown { border-left: 4px solid #9ca3af; }

    .evidence-question {
        font-size: 1rem;
        font-weight: 600;
        color: #111827;
        margin-bottom: 8px;
        line-height: 1.5;
    }

    .evidence-meta {
        font-size: 0.82rem;
        color: #6b7280;
        margin-bottom: 8px;
    }

    .evidence-reasoning {
        font-size: 0.88rem;
        color: #374151;
        background: #f0f9ff;
        border-radius: 8px;
        padding: 8px 12px;
        margin-top: 6px;
        border-left: 3px solid #38bdf8;
        line-height: 1.55;
    }

    /* ---- Lecture row ---- */
    .lecture-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 14px;
        border-radius: 10px;
        background: #f9fafb;
        margin-bottom: 8px;
        font-size: 0.9rem;
    }

    .lecture-name { font-weight: 600; color: #1e3a5f; }
    .lecture-meta { color: #6b7280; font-size: 0.82rem; }

    /* ---- Metric boxes ---- */
    div[data-testid="stMetric"] {
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 10px 14px;
        background: #ffffff;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# LOAD STATIC GAP MAP
# ============================================================

data = load_gap_map()

if data is None:

    data = {
        "topics": [],
        "source_results": 0,
        "valid_learning_gap_signals": 0,
        "skipped_non_signals": 0,
        "skipped_none_signals": 0,
        "skipped_non_learning": 0,
    }

    # st.info(
    #     "Chưa nạp Class Gap Map riêng. "
    #     "Bạn có thể dùng Live AI analysis hoặc "
    #     "đặt VLEARN_GAP_MAP_PATH tới file cục bộ."
    # )


topics = get_topics(data)

source_results = data.get(
    "source_results",
    0,
)

valid_signals = data.get(
    "valid_learning_gap_signals",
    data.get(
        "valid_signal_results",
        data.get(
            "valid_signals",
            0,
        ),
    ),
)

skipped_non_learning = data.get(
    "skipped_non_learning",
    0,
)

if isinstance(
    skipped_non_learning,
    dict,
):

    skipped_non_learning_total = sum(
        skipped_non_learning.values()
    )

else:

    skipped_non_learning_total = int(
        skipped_non_learning or 0
    )

overall_severity = calculate_overall_severity(
    topics
)


# ============================================================
# SESSION STATE
# ============================================================

if "selected_topic" not in st.session_state:

    st.session_state.selected_topic = None


if "live_analysis" not in st.session_state:

    st.session_state.live_analysis = None


if "live_gap_map" not in st.session_state:

    st.session_state.live_gap_map = None


if "live_selected_topic" not in st.session_state:

    st.session_state.live_selected_topic = None


# ============================================================
# STATIC DETAIL VIEW
# ============================================================

selected_topic_name = (
    st.session_state.selected_topic
)

if selected_topic_name:

    selected = next(
        (
            topic
            for topic in topics
            if topic.get("topic")
            == selected_topic_name
        ),
        None,
    )

    if selected is None:

        st.session_state.selected_topic = None

        st.rerun()

    if st.button("← Quay lại danh sách chủ đề"):

        st.session_state.selected_topic = None

        st.rerun()

    render_topic_detail(
        selected,
        title="Chatlog đã phân tích",
    )

    st.stop()


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="main-title">🎓 Bản đồ Học tập Lớp học</div>
    <div class="subtitle">
        Tổng hợp các chủ đề sinh viên đang gặp khó khăn
        — dựa trên phân tích chatlog bởi AI
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# LIVE AI ANALYSIS
# ============================================================

st.subheader("⚡ Phân tích trực tiếp")

# ── Khu nhập liệu ──────────────────────────────────────────
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.markdown("**📂 Tải lên file chatlog**")
    uploaded_file = st.file_uploader(
        "upload",
        type=["csv"],
        help="File CSV cần có cột student_question. Các cột turn_id, student, lecture_code, lecture_title là tuỳ chọn.",
        label_visibility="collapsed",
    )
    if uploaded_file:
        st.success(f"✅ Đã tải lên: **{uploaded_file.name}**")

with col_right:
    st.markdown("**✏️ Hoặc nhập câu hỏi sinh viên**")
    question_text = st.text_area(
        "questions",
        value=(
            "Em chưa hiểu retrieval khác generation như thế nào?\n"
            "Tại sao phải dùng embedding trong vector database?\n"
            "RAG có giống fine-tuning không?"
        ),
        height=130,
        placeholder="Mỗi dòng là một câu hỏi của sinh viên...",
        label_visibility="collapsed",
    )

analyze_clicked = st.button(
    "🔍 Bắt đầu phân tích",
    type="primary",
    use_container_width=True,
    help="AI sẽ đọc câu hỏi và tổng hợp các chủ đề sinh viên đang gặp khó khăn",
)


# ============================================================
# SEND REQUEST
# ============================================================

if analyze_clicked:

    try:

        # ── Xây dựng input DataFrame ──────────────────────
        if uploaded_file is not None:
            input_rows = pd.read_csv(uploaded_file)
            if "student_question" not in input_rows.columns:
                raise ValueError(
                    "File CSV phải có cột student_question."
                )
            input_rows = input_rows.copy()

        else:
            questions = [
                line.strip()
                for line in question_text.splitlines()
                if line.strip()
            ]
            if not questions:
                raise ValueError(
                    "Hãy nhập ít nhất một câu hỏi hoặc tải lên file CSV."
                )
            input_rows = pd.DataFrame([
                {
                    "turn_id":          f"LIVE-{i:03d}",
                    "student":          f"Sinh viên {i}",
                    "lecture_code":     "LIVE",
                    "lecture_title":    "Demo",
                    "student_question": q,
                }
                for i, q in enumerate(questions, start=1)
            ])

        if input_rows.empty:
            raise ValueError("Không có câu hỏi hợp lệ để phân tích.")

        # ── Chuẩn hoá cột ─────────────────────────────────
        input_rows = input_rows.head(20).copy()

        # Xử lý theo batch nhỏ để AI giữ chất lượng phân tích
        LIVE_BATCH_SIZE = 5

        for col, default_fn in [
            ("turn_id",       lambda i: f"LIVE-{i:03d}"),
            ("student",       lambda i: f"Sinh viên {i}"),
            ("lecture_code",  lambda i: "LIVE"),
            ("lecture_title", lambda i: "Demo"),
        ]:
            if col not in input_rows.columns:
                input_rows[col] = [
                    default_fn(i)
                    for i in range(1, len(input_rows) + 1)
                ]

        input_rows["student_question"] = (
            input_rows["student_question"]
            .fillna("").astype(str).str.strip()
        )
        input_rows = input_rows[input_rows["student_question"] != ""]
        input_rows = input_rows[
            ["turn_id", "student", "lecture_code", "lecture_title", "student_question"]
        ]

        if input_rows.empty:
            raise ValueError("Không có câu hỏi hợp lệ sau khi lọc.")

        # ── Gọi AI (theo batch nhỏ để giữ chất lượng) ───
        with st.spinner("⏳ AI đang phân tích câu hỏi của sinh viên..."):
            all_raw_results = []
            total_batches = (len(input_rows) + LIVE_BATCH_SIZE - 1) // LIVE_BATCH_SIZE
            for batch_i in range(total_batches):
                chunk = input_rows.iloc[batch_i * LIVE_BATCH_SIZE : (batch_i + 1) * LIVE_BATCH_SIZE]
                batch_response = analyze_batch(chunk)
                batch_results = batch_response.get("results", [])
                if isinstance(batch_results, list):
                    all_raw_results.extend(batch_results)
            response = {"results": all_raw_results}

        raw_results = response.get("results", [])
        if not isinstance(raw_results, list):
            raise ValueError("Phản hồi từ AI không có danh sách kết quả.")

        # ── Gắn metadata + tổng hợp ───────────────────────
        live_results = attach_live_metadata(raw_results, input_rows)
        response["results"] = live_results

        live_gap_map = build_gap_map_from_results(live_results)

        st.session_state.live_analysis      = response
        st.session_state.live_gap_map       = live_gap_map
        st.session_state.live_selected_topic = None

        st.success("✅ Phân tích hoàn tất!")

    except Exception as error:
        st.session_state.live_analysis       = None
        st.session_state.live_gap_map        = None
        st.session_state.live_selected_topic = None
        st.error(f"❌ Không thể phân tích: {error}")



# ============================================================
# LIVE GAP MAP
# ============================================================

live_gap_map = (
    st.session_state.live_gap_map
)


if live_gap_map is not None:

    live_selected_name = (
        st.session_state.live_selected_topic
    )

    # ========================================================
    # LIVE DETAIL
    # ========================================================

    if live_selected_name:

        live_selected = next(
            (
                topic
                for topic
                in live_gap_map.get(
                    "topics",
                    [],
                )
                if topic.get(
                    "topic"
                )
                == live_selected_name
            ),
            None,
        )

        if live_selected is not None:

            if st.button("← Quay lại danh sách chủ đề"):

                st.session_state[
                    "live_selected_topic"
                ] = None

                st.rerun()

            render_topic_detail(
                live_selected,
                title="Kết quả phân tích trực tiếp",
            )

            st.stop()

        st.session_state[
            "live_selected_topic"
        ] = None

        st.rerun()

st.divider()


# ============================================================
# ACTIVE CLASS GAP MAP
# ============================================================

st.subheader("📋 Bản đồ học tập — Chatlog đã phân tích")

# When a CSV has just been analyzed, that result becomes the active map.  The
# search/sort/filter controls below must always receive the same topic list
# that is rendered in the cards; previously they still targeted `topics` from
# the static gap_map.json, so they appeared to do nothing after an upload.
showing_live_results = live_gap_map is not None
active_map = live_gap_map if showing_live_results else data
active_topics = get_topics(active_map)
active_source = active_map.get("source_results", 0)
active_severity = calculate_overall_severity(active_topics)
active_prefix = "live" if showing_live_results else "static"

if showing_live_results:
    st.caption("Đang hiển thị kết quả từ file CSV/câu hỏi vừa phân tích.")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Câu hỏi đã phân tích", format_number(active_source))

with col2:
    st.metric("Chủ đề phát hiện", format_number(len(active_topics)))

with col3:
    sev_icon = severity_color(active_severity)
    st.metric(
        "Mức độ trung bình",
        f"{sev_icon} {severity_text(active_severity)}",
    )


# ============================================================
# FILTERS
# ============================================================

st.divider()

left, middle, right = st.columns([2, 1, 1])

with left:
    search = st.text_input(
        "🔎 Tìm chủ đề",
        placeholder="Ví dụ: RAG, Embedding, Prompt...",
    )

with middle:
    sort_mode = st.selectbox(
        "Sắp xếp theo",
        [
            "Most signals",
            "Most students",
            "Highest severity",
            "Alphabetical",
        ],
        format_func=lambda x: {
            "Most signals":     "Nhiều câu hỏi nhất",
            "Most students":    "Nhiều sinh viên nhất",
            "Highest severity": "Mức độ cao nhất",
            "Alphabetical":     "A → Z",
        }.get(x, x),
    )

with right:
    severity_filter = st.selectbox(
        "Lọc mức độ",
        [
            "All",
            "High (≥ 4)",
            "Medium (3–3.99)",
            "Low (< 3)",
        ],
        format_func=lambda x: {
            "All":            "Tất cả",
            "High (≥ 4)":     "🔴 Cao",
            "Medium (3–3.99)":"🟡 Trung bình",
            "Low (< 3)":      "🟢 Thấp",
        }.get(x, x),
    )


# ============================================================
# FILTER
# ============================================================

filtered_topics = filter_topics(
    active_topics,
    search,
    sort_mode,
    severity_filter,
)


st.caption(f"Hiển thị {len(filtered_topics)} / {len(active_topics)} chủ đề")


# ============================================================
# STATIC TOPIC CARDS
# ============================================================

render_topic_cards(
    filtered_topics,
    prefix=active_prefix,
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption("VLearn — Bản đồ Học tập Lớp học · Hỗ trợ bởi AI")
