import json
import os
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
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def severity_label(value):
    value = safe_float(value)

    if value >= 4:
        return "High"

    if value >= 3:
        return "Medium"

    return "Low"


def severity_color(value):
    value = safe_float(value)

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
            safe_float(
                x.get("severity")
            )
            for x in signals
            if isinstance(
                x.get("severity"),
                (int, float),
            )
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
                safe_float(
                    x.get("severity")
                )
                for x in lecture_signals
                if isinstance(
                    x.get("severity"),
                    (int, float),
                )
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

    severities = [
        safe_float(
            topic.get("average_severity")
        )
        for topic in topics
    ]

    if not severities:
        return 0

    return sum(severities) / len(severities)


def render_topic_detail(
    selected,
    title="Learning area",
):

    st.markdown(
        f"""
        <div class="detail-header">
            {selected.get("topic", "Unknown topic")}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption(
        f"{title}. AI chỉ cung cấp tín hiệu và bằng chứng; "
        "giảng viên xác nhận và quyết định có cần can thiệp."
    )

    signal_count = selected.get(
        "signal_count",
        0,
    )

    student_count = selected.get(
        "student_count",
        0,
    )

    severity = selected.get(
        "average_severity",
        0,
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "Learning signals",
            format_number(
                signal_count
            ),
        )

    with c2:
        st.metric(
            "Students",
            format_number(
                student_count
            ),
        )

    with c3:
        st.metric(
            "Avg. severity",
            f"{safe_float(severity):.2f} / 5",
        )

    st.divider()

    # ========================================================
    # SIGNAL TYPES
    # ========================================================

    st.subheader("Signal types")

    signal_types = selected.get(
        "signal_types",
        {},
    )

    if signal_types:

        signal_cols = st.columns(
            min(
                4,
                len(signal_types),
            )
        )

        for index, (
            signal_type,
            count,
        ) in enumerate(
            signal_types.items()
        ):

            with signal_cols[
                index % len(signal_cols)
            ]:

                st.metric(
                    signal_type.replace(
                        "_",
                        " ",
                    ).title(),
                    format_number(
                        count
                    ),
                )

    else:

        st.info(
            "Không có thông tin signal type."
        )

    # ========================================================
    # LECTURE CONTEXT
    # ========================================================

    st.subheader("Lecture context")

    lectures = selected.get(
        "lectures",
        [],
    )

    if lectures:

        for lecture in lectures:

            lecture_name = get_lecture_name(
                lecture
            )

            lecture_signals = lecture.get(
                "signal_count",
                lecture.get(
                    "signals",
                    0,
                ),
            )

            lecture_students = lecture.get(
                "student_count",
                lecture.get(
                    "students",
                    0,
                ),
            )

            lecture_severity = lecture.get(
                "average_severity",
                0,
            )

            st.markdown(
                f"""
                **{lecture_name}**

                {format_number(lecture_signals)}
                signals ·
                {format_number(lecture_students)}
                students ·
                avg. severity
                {safe_float(lecture_severity):.2f}/5
                """
            )

    else:

        st.info(
            "Không có lecture breakdown."
        )

    # ========================================================
    # EVIDENCE
    # ========================================================

    st.subheader(
        "Evidence from chatlog"
    )

    evidence = get_evidence(
        selected
    )

    if not evidence:

        st.info(
            "Chưa có evidence."
        )

    else:

        for index, item in enumerate(
            evidence,
            start=1,
        ):

            if isinstance(
                item,
                dict,
            ):

                question = item.get(
                    "student_question",
                    item.get(
                        "question",
                        "",
                    ),
                )

                reason = item.get(
                    "reason",
                    "",
                )

                student = item.get(
                    "student",
                    "",
                )

                lecture = item.get(
                    "lecture_title",
                    "",
                )

                item_severity = item.get(
                    "severity",
                    "",
                )

                signal_type = item.get(
                    "signal_type",
                    "",
                )

                st.markdown(
                    f"**Evidence {index}** "
                    f"{severity_color(item_severity)}"
                )

                if question:

                    st.markdown(
                        f"""
                        <div class="evidence-box">
                            "{question}"
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                meta = []

                if student:
                    meta.append(
                        f"Student: {student}"
                    )

                if lecture:
                    meta.append(
                        f"Lecture: {lecture}"
                    )

                if signal_type:
                    meta.append(
                        "Signal: "
                        + signal_type.replace(
                            "_",
                            " ",
                        ).title()
                    )

                if item_severity != "":
                    meta.append(
                        f"Severity: "
                        f"{item_severity}/5"
                    )

                if meta:
                    st.caption(
                        " · ".join(meta)
                    )

                if reason:

                    st.write(
                        "**AI reasoning:** "
                        f"{reason}"
                    )

            else:

                st.markdown(
                    f"""
                    <div class="evidence-box">
                        "{item}"
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.divider()

    st.info(
        "💡 Instructor decision: Evidence trên là tín hiệu "
        "từ chatlog, không phải kết luận rằng một sinh viên "
        "hay cả lớp chắc chắn bị hổng kiến thức."
    )


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


def render_topic_cards(
    topics,
    prefix,
):

    if not topics:

        st.info(
            "Không tìm thấy learning area phù hợp."
        )

        return

    for row_start in range(
        0,
        len(topics),
        2,
    ):

        row_topics = topics[
            row_start:row_start + 2
        ]

        columns = st.columns(2)

        for column, topic in zip(
            columns,
            row_topics,
        ):

            with column:

                name = topic.get(
                    "topic",
                    "Unknown",
                )

                signals = topic.get(
                    "signal_count",
                    0,
                )

                students = topic.get(
                    "student_count",
                    0,
                )

                severity = topic.get(
                    "average_severity",
                    0,
                )

                severity_value = safe_float(
                    severity
                )

                evidence = get_evidence(
                    topic
                )

                st.markdown(
                    f"""
                    <div class="topic-card">

                        <div class="topic-name">
                            {name}
                        </div>

                        <div class="topic-meta">

                            {format_number(signals)}
                            signals

                            ·

                            {format_number(students)}
                            students

                            ·

                            {severity_color(severity_value)}

                            {severity_value:.2f}/5

                            ·

                            {severity_label(severity_value)}

                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if evidence:

                    first = evidence[0]

                    if isinstance(
                        first,
                        dict,
                    ):

                        preview = first.get(
                            "student_question",
                            first.get(
                                "question",
                                "",
                            ),
                        )

                    else:

                        preview = str(
                            first
                        )

                    if len(preview) > 150:

                        preview = (
                            preview[:150]
                            + "..."
                        )

                    st.caption(
                        f'“{preview}”'
                    )

                if st.button(
                    "View evidence →",
                    key=(
                        f"{prefix}_view_"
                        f"{name}"
                    ),
                    use_container_width=True,
                ):

                    if prefix == "live":

                        st.session_state[
                            "live_selected_topic"
                        ] = name

                    else:

                        st.session_state[
                            "selected_topic"
                        ] = name

                    st.rerun()


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 2.25rem;
        font-weight: 750;
        margin-bottom: 0.1rem;
    }

    .subtitle {
        color: #6b7280;
        font-size: 1rem;
        margin-bottom: 1.4rem;
    }

    .topic-card {
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 14px;
        background: #ffffff;
        min-height: 150px;
    }

    .topic-name {
        font-size: 1.15rem;
        font-weight: 700;
        margin-bottom: 8px;
    }

    .topic-meta {
        color: #6b7280;
        font-size: 0.9rem;
        margin-bottom: 12px;
    }

    .evidence-box {
        border-left: 3px solid #9ca3af;
        padding: 8px 12px;
        margin: 8px 0;
        background: #f9fafb;
        border-radius: 0 8px 8px 0;
        font-size: 0.9rem;
    }

    .scope-note {
        background: #f9fafb;
        border-radius: 10px;
        padding: 12px 15px;
        color: #4b5563;
        font-size: 0.9rem;
        margin: 12px 0 20px 0;
    }

    .live-note {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-radius: 10px;
        padding: 12px 15px;
        color: #166534;
        font-size: 0.9rem;
        margin: 12px 0 20px 0;
    }

    .detail-header {
        font-size: 1.7rem;
        font-weight: 750;
        margin-bottom: 0.4rem;
    }

    div[data-testid="stMetric"] {
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 10px;
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

    st.info(
        "Chưa nạp Class Gap Map riêng. "
        "Bạn có thể dùng Live AI analysis hoặc "
        "đặt VLEARN_GAP_MAP_PATH tới file cục bộ."
    )


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

    if st.button(
        "← Back to Class Gap Map"
    ):

        st.session_state.selected_topic = None

        st.rerun()

    render_topic_detail(
        selected,
        title=(
            "Class Gap Map từ "
            "chatlog đã phân tích"
        ),
    )

    st.stop()


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="main-title">
        🎓 VLearn — Class Gap Map
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="subtitle">
        Bản đồ các chủ đề có tín hiệu cần được
        giảng viên xem xét từ chatlog lớp học
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="scope-note">

        🤖 <b>AI làm:</b>
        phát hiện, nhóm và tổng hợp các tín hiệu
        trong chatlog.

        <b>AI không làm:</b>
        tự kết luận học viên yếu hoặc tự quyết định
        nội dung giảng dạy.

        <b>Giảng viên</b>
        là người xác nhận và quyết định can thiệp.

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# LIVE AI ANALYSIS
# ============================================================

st.subheader(
    "⚡ Live AI analysis"
)

st.caption(
    "Nhập hoặc tải câu hỏi để gửi trực tiếp tới Ollama. "
    "Sau khi AI trả kết quả, hệ thống sẽ chạy tiếp "
    "signal classifier → topic normalizer → live aggregation "
    "và hiển thị thành Class Gap Map."
)


uploaded_file = st.file_uploader(
    "Upload chatlog CSV",
    type=["csv"],
    help=(
        "CSV cần có cột student_question. "
        "Các cột turn_id, student, lecture_code "
        "và lecture_title là tùy chọn."
    ),
)


question_text = st.text_area(
    "Hoặc nhập câu hỏi học viên",
    value=(
        "Em chưa hiểu retrieval khác generation "
        "như thế nào?\n"
        "Tại sao phải dùng embedding trong "
        "vector database?\n"
        "RAG có giống fine-tuning không?"
    ),
    height=120,
)


analyze_clicked = st.button(
    f"Send request to AI ({MODEL})",
    type="primary",
    use_container_width=True,
)


# ============================================================
# SEND REQUEST
# ============================================================

if analyze_clicked:

    try:

        # ----------------------------------------------------
        # BUILD INPUT
        # ----------------------------------------------------

        if uploaded_file is not None:

            input_rows = pd.read_csv(
                uploaded_file
            )

            if (
                "student_question"
                not in input_rows.columns
            ):

                raise ValueError(
                    "CSV phải có cột "
                    "student_question."
                )

            input_rows = input_rows.copy()

        else:

            questions = [
                line.strip()
                for line in question_text.splitlines()
                if line.strip()
            ]

            input_rows = pd.DataFrame(
                [
                    {
                        "turn_id": (
                            f"LIVE-{index:03d}"
                        ),
                        "student": (
                            f"Demo Student {index}"
                        ),
                        "lecture_code": "LIVE",
                        "lecture_title": (
                            "Live demo input"
                        ),
                        "student_question": question,
                    }
                    for index, question in enumerate(
                        questions,
                        start=1,
                    )
                ]
            )

        if input_rows.empty:

            raise ValueError(
                "Hãy nhập ít nhất một câu hỏi "
                "hoặc tải lên CSV hợp lệ."
            )

        # ----------------------------------------------------
        # LIMIT LIVE REQUEST
        # ----------------------------------------------------

        input_rows = input_rows.head(
            10
        ).copy()

        # ----------------------------------------------------
        # DEFAULT METADATA
        # ----------------------------------------------------

        if "turn_id" not in input_rows.columns:

            input_rows["turn_id"] = [
                f"LIVE-{index:03d}"
                for index in range(
                    1,
                    len(input_rows) + 1,
                )
            ]

        if "student" not in input_rows.columns:

            input_rows["student"] = [
                f"Demo Student {index}"
                for index in range(
                    1,
                    len(input_rows) + 1,
                )
            ]

        if (
            "lecture_code"
            not in input_rows.columns
        ):

            input_rows["lecture_code"] = "LIVE"

        if (
            "lecture_title"
            not in input_rows.columns
        ):

            input_rows["lecture_title"] = (
                "Live demo input"
            )

        input_rows[
            "student_question"
        ] = (
            input_rows[
                "student_question"
            ]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        input_rows = input_rows[
            input_rows[
                "student_question"
            ] != ""
        ]

        input_rows = input_rows[
            [
                "turn_id",
                "student",
                "lecture_code",
                "lecture_title",
                "student_question",
            ]
        ]

        if input_rows.empty:

            raise ValueError(
                "Không có student_question "
                "hợp lệ."
            )

        # ====================================================
        # 1. CALL LLM
        # ====================================================

        with st.spinner(
            f"Sending request to {MODEL}..."
        ):

            response = analyze_batch(
                input_rows
            )

        if not isinstance(
            response,
            dict,
        ):

            raise ValueError(
                "AI response không có "
                "dạng JSON object."
            )

        raw_results = response.get(
            "results",
            [],
        )

        if not isinstance(
            raw_results,
            list,
        ):

            raise ValueError(
                "AI response không có "
                "trường results dạng list."
            )

        # ====================================================
        # 2. ATTACH METADATA
        # ====================================================

        live_results = attach_live_metadata(
            raw_results,
            input_rows,
        )

        response["results"] = (
            live_results
        )

        # ====================================================
        # 3. CLASSIFIER + NORMALIZER + AGGREGATOR
        # ====================================================

        live_gap_map = (
            build_gap_map_from_results(
                live_results
            )
        )

        # ====================================================
        # 4. SAVE SESSION STATE
        # ====================================================

        st.session_state.live_analysis = (
            response
        )

        st.session_state.live_gap_map = (
            live_gap_map
        )

        st.session_state.live_selected_topic = (
            None
        )

        st.success(
            "AI response received → "
            "classifier → "
            "topic normalizer → "
            "live aggregation hoàn tất."
        )

    except Exception as error:

        st.session_state.live_analysis = None

        st.session_state.live_gap_map = None

        st.session_state.live_selected_topic = None

        st.error(
            f"Không thể xử lý live analysis: "
            f"{error}"
        )


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

            if st.button(
                "← Back to Live Gap Map"
            ):

                st.session_state[
                    "live_selected_topic"
                ] = None

                st.rerun()

            render_topic_detail(
                live_selected,
                title=(
                    "Live Gap Map từ "
                    "request vừa gửi"
                ),
            )

            st.stop()

        st.session_state[
            "live_selected_topic"
        ] = None

        st.rerun()

    # ========================================================
    # LIVE MAP
    # ========================================================

    st.divider()

    st.markdown(
        """
        <div class="live-note">

            ✅ <b>Live Gap Map đã được tạo.</b>

            Kết quả này nằm trong session hiện tại
            và <b>không ghi đè</b> gap_map.json.

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader(
        "📊 Live Class Gap Map"
    )

    live_topics = get_topics(
        live_gap_map
    )

    live_source = live_gap_map.get(
        "source_results",
        0,
    )

    live_signals = live_gap_map.get(
        "valid_learning_gap_signals",
        live_gap_map.get(
            "valid_signal_results",
            0,
        ),
    )

    live_excluded = live_gap_map.get(
        "skipped_non_learning",
        0,
    )

    live_severity = (
        calculate_overall_severity(
            live_topics
        )
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(
            "Questions received",
            format_number(
                live_source
            ),
        )

    with c2:

        st.metric(
            "Learning signals",
            format_number(
                live_signals
            ),
        )

    with c3:

        st.metric(
            "Learning areas",
            format_number(
                len(live_topics)
            ),
        )

    with c4:

        st.metric(
            "Avg. severity",
            f"{live_severity:.2f} / 5",
        )

    st.caption(
        "Excluded from learning map: "
        f"{format_number(live_excluded)}"
    )

    if not live_topics:

        st.warning(
            "AI không tạo được learning-gap "
            "signal đủ rõ để đưa vào Class Gap Map. "
            "Hãy thử câu hỏi có chủ đề học tập cụ thể."
        )

    else:

        render_topic_cards(
            live_topics,
            prefix="live",
        )

    # ========================================================
    # RAW JSON DEBUG
    # ========================================================

    with st.expander(
        "🔧 Debug: Raw AI JSON"
    ):

        st.json(
            st.session_state.live_analysis
        )


st.divider()


# ============================================================
# STATIC CLASS GAP MAP
# ============================================================

st.subheader(
    "Class Gap Map — analyzed chatlog"
)


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Questions analyzed",
        format_number(
            source_results
        ),
    )


with col2:

    st.metric(
        "Learning signals",
        format_number(
            valid_signals
        ),
    )


with col3:

    st.metric(
        "Learning areas",
        format_number(
            len(topics)
        ),
    )


with col4:

    st.metric(
        "Avg. severity",
        f"{overall_severity:.2f} / 5",
    )


# ============================================================
# FILTERS
# ============================================================

st.divider()

left, middle, right = st.columns(
    [2, 1, 1]
)


with left:

    search = st.text_input(
        "Search learning area",
        placeholder=(
            "Ví dụ: RAG, ReAct, Prompt..."
        ),
    )


with middle:

    sort_mode = st.selectbox(
        "Sort by",
        [
            "Most signals",
            "Most students",
            "Highest severity",
            "Alphabetical",
        ],
    )


with right:

    severity_filter = st.selectbox(
        "Severity",
        [
            "All",
            "High (≥ 4)",
            "Medium (3–3.99)",
            "Low (< 3)",
        ],
    )


# ============================================================
# FILTER
# ============================================================

filtered_topics = filter_topics(
    topics,
    search,
    sort_mode,
    severity_filter,
)


st.caption(
    f"Showing {len(filtered_topics)} / "
    f"{len(topics)} learning areas"
)


# ============================================================
# STATIC TOPIC CARDS
# ============================================================

render_topic_cards(
    filtered_topics,
    prefix="static",
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    f"Source: "
    f"{format_number(source_results)} "
    f"chatlog questions · "
    f"{format_number(valid_signals)} "
    f"learning-gap signals · "
    f"{format_number(skipped_non_learning_total)} "
    f"signals excluded from the learning map."
)

st.caption(
    "VLearn Class Gap Map — "
    "AI-assisted analysis for instructors."
)