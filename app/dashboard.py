import json
import os
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Streamlit executes this file with `app/` as the script path. Add the
# repository root so imports using the `app` package work in that mode.
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.analyzer import MODEL, analyze_batch


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
# HELPERS
# ============================================================

@st.cache_data
def load_gap_map():
    if not DATA_PATH.exists():
        return None

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def format_number(value):
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return "0"


def severity_label(value):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return "—"

    if value >= 4:
        return "High"
    if value >= 3:
        return "Medium"
    return "Low"


def severity_color(value):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return ""

    if value >= 4:
        return "🔴"
    if value >= 3:
        return "🟡"
    return "🟢"


def get_topics(data):
    topics = data.get("topics", [])

    # Keep "Other" at the bottom. Do not delete it.
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

    code = str(lecture.get("lecture_code", "")).strip()
    title = str(lecture.get("lecture_title", "")).strip()

    if code and title and code != title:
        return f"{code} — {title}"
    return code or title or "Unknown lecture"


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
        min-height: 190px;
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
# LOAD DATA
# ============================================================

data = load_gap_map()

if data is None:
    # Private data is optional; the live AI demo can run without a bundled map.
    data = {
        "topics": [],
        "source_results": 0,
        "valid_learning_gap_signals": 0,
        "skipped_non_signals": 0,
        "skipped_none_signals": 0,
        "skipped_non_learning": 0,
    }
    st.info(
        "Chưa nạp Class Gap Map riêng. Dữ liệu lớp học không được public; "
        "bạn có thể dùng Live AI analysis hoặc đặt VLEARN_GAP_MAP_PATH tới "
        "file cục bộ trên máy."
    )


topics = get_topics(data)

source_results = data.get("source_results", 0)
valid_signals = data.get("valid_learning_gap_signals", data.get("valid_signals", 0))
skipped_non_signals = data.get("skipped_non_signals", 0)
skipped_none_signals = data.get("skipped_none_signals", 0)
skipped_non_learning = data.get("skipped_non_learning", 0)

if isinstance(skipped_non_learning, dict):
    skipped_non_learning_total = sum(skipped_non_learning.values())
else:
    skipped_non_learning_total = int(skipped_non_learning or 0)

all_severities = []
for topic in topics:
    severity = topic.get("average_severity")
    if isinstance(severity, (int, float)):
        all_severities.append(float(severity))

overall_severity = (
    sum(all_severities) / len(all_severities)
    if all_severities
    else 0
)


# ============================================================
# SESSION STATE
# ============================================================

if "selected_topic" not in st.session_state:
    st.session_state.selected_topic = None


# ============================================================
# DETAIL VIEW
# ============================================================

selected_topic_name = st.session_state.selected_topic

if selected_topic_name:
    selected = next(
        (t for t in topics if t.get("topic") == selected_topic_name),
        None,
    )

    if selected is None:
        st.session_state.selected_topic = None
        st.rerun()

    if st.button("← Back to Class Gap Map"):
        st.session_state.selected_topic = None
        st.rerun()

    st.markdown(
        f'<div class="detail-header">{selected.get("topic", "Unknown topic")}</div>',
        unsafe_allow_html=True,
    )

    st.caption(
        "AI tổng hợp các tín hiệu từ chatlog. Giảng viên xác nhận "
        "có cần can thiệp giảng dạy hay không."
    )

    signal_count = selected.get("signal_count", 0)
    student_count = selected.get("student_count", 0)
    severity = selected.get("average_severity", 0)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Learning signals", format_number(signal_count))

    with c2:
        st.metric("Students", format_number(student_count))

    with c3:
        st.metric(
            "Avg. severity",
            f"{float(severity):.2f} / 5" if isinstance(severity, (int, float)) else "—",
        )

    st.divider()

    # Signal types
    st.subheader("Signal types")

    signal_types = selected.get("signal_types", {})
    if signal_types:
        signal_cols = st.columns(min(4, len(signal_types)))

        for index, (signal_type, count) in enumerate(signal_types.items()):
            with signal_cols[index % len(signal_cols)]:
                st.metric(
                    signal_type.replace("_", " ").title(),
                    format_number(count),
                )
    else:
        st.info("Không có thông tin signal type.")

    # Lecture breakdown
    st.subheader("Lecture context")

    lectures = selected.get("lectures", [])
    if lectures:
        for lecture in lectures:
            lecture_name = get_lecture_name(lecture)
            lecture_signals = lecture.get(
                "signal_count",
                lecture.get("signals", 0),
            )
            lecture_students = lecture.get(
                "student_count",
                lecture.get("students", 0),
            )

            st.markdown(
                f"**{lecture_name}**  \n"
                f"{format_number(lecture_signals)} signals · "
                f"{format_number(lecture_students)} students"
            )
    else:
        st.info("Không có lecture breakdown.")

    # Evidence
    st.subheader("Evidence from chatlog")

    evidence = get_evidence(selected)

    if not evidence:
        st.info("Chưa có evidence.")
    else:
        for index, item in enumerate(evidence, start=1):
            if isinstance(item, dict):
                question = item.get(
                    "student_question",
                    item.get("question", ""),
                )
                reason = item.get("reason", "")
                student = item.get("student", "")
                lecture = item.get("lecture_title", "")
                item_severity = item.get("severity", "")

                st.markdown(
                    f"**Evidence {index}** "
                    f"{severity_color(item_severity)}"
                )

                if question:
                    st.markdown(
                        f'<div class="evidence-box">"{question}"</div>',
                        unsafe_allow_html=True,
                    )

                meta = []
                if student:
                    meta.append(f"Student: {student}")
                if lecture:
                    meta.append(f"Lecture: {lecture}")
                if item_severity != "":
                    meta.append(f"Severity: {item_severity}/5")

                if meta:
                    st.caption(" · ".join(meta))

                if reason:
                    st.write(f"**AI reasoning:** {reason}")

            else:
                st.markdown(
                    f'<div class="evidence-box">"{item}"</div>',
                    unsafe_allow_html=True,
                )

    st.divider()

    st.info(
        "💡 Instructor decision: Evidence trên chỉ là tín hiệu từ chatlog, "
        "không phải kết luận rằng một sinh viên hay cả lớp chắc chắn bị "
        "hổng kiến thức."
    )

    st.stop()


# ============================================================
# MAIN HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🎓 VLearn — Class Gap Map</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    "Bản đồ các chủ đề có tín hiệu cần được giảng viên xem xét từ chatlog lớp học"
    "</div>",
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="scope-note">'
    "🤖 <b>AI làm:</b> phát hiện, nhóm và tổng hợp các tín hiệu trong chatlog. "
    "<b>AI không làm:</b> tự kết luận học viên yếu hoặc tự quyết định nội dung "
    "giảng dạy. <b>Giảng viên</b> là người xác nhận và quyết định can thiệp."
    "</div>",
    unsafe_allow_html=True,
)


# ============================================================
# LIVE AI ANALYSIS
# ============================================================

st.subheader("Live AI analysis")
st.caption(
    "Nhập hoặc tải câu hỏi để gửi trực tiếp tới Ollama và nhận kết quả AI thật."
)

uploaded_file = st.file_uploader(
    "Upload chatlog CSV",
    type=["csv"],
    help="CSV cần có cột student_question; các cột turn_id, lecture_code và lecture_title là tùy chọn.",
)

question_text = st.text_area(
    "Hoặc nhập câu hỏi học viên",
    value=(
        "Em chưa hiểu retrieval khác generation như thế nào?\n"
        "Tại sao phải dùng embedding trong vector database?\n"
        "RAG có giống fine-tuning không?"
    ),
    height=110,
)

if "live_analysis" not in st.session_state:
    st.session_state.live_analysis = None

analyze_clicked = st.button(
    f"Send request to AI ({MODEL})",
    type="primary",
    use_container_width=True,
)

if analyze_clicked:
    try:
        if uploaded_file is not None:
            input_rows = pd.read_csv(uploaded_file)
            if "student_question" not in input_rows.columns:
                raise ValueError("CSV phải có cột student_question.")
            else:
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
                        "turn_id": f"LIVE-{index:03d}",
                        "lecture_code": "LIVE",
                        "lecture_title": "Live demo input",
                        "student_question": question,
                    }
                    for index, question in enumerate(questions, start=1)
                ]
            )

        required_columns = {
            "turn_id": [f"LIVE-{index:03d}" for index in range(1, len(input_rows) + 1)],
            "lecture_code": ["LIVE"] * len(input_rows),
            "lecture_title": ["Live demo input"] * len(input_rows),
        }
        for column, default_values in required_columns.items():
            if column not in input_rows.columns:
                input_rows[column] = default_values

        input_rows = input_rows[
            ["turn_id", "lecture_code", "lecture_title", "student_question"]
        ].head(10)

        if input_rows.empty:
            st.warning("Hãy nhập ít nhất một câu hỏi hoặc tải lên một CSV hợp lệ.")
        else:
            with st.spinner(f"Sending request to {MODEL}..."):
                response = analyze_batch(input_rows)
            st.session_state.live_analysis = response
            st.success("AI response received from Ollama.")
    except Exception as error:
        st.session_state.live_analysis = None
        st.error(f"Không thể gọi model: {error}")

if st.session_state.live_analysis is not None:
    live_results = st.session_state.live_analysis.get("results", [])
    st.markdown("**Live response**")
    st.json(st.session_state.live_analysis)
    st.caption(
        f"Received {len(live_results)} AI results. "
        "Giảng viên dùng các tín hiệu này để xem xét tiếp."
    )

st.divider()


# ============================================================
# TOP METRICS
# ============================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Questions analyzed",
        format_number(source_results),
    )

with col2:
    st.metric(
        "Learning signals",
        format_number(valid_signals),
    )

with col3:
    st.metric(
        "Learning areas",
        format_number(len(topics)),
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

left, middle, right = st.columns([2, 1, 1])

with left:
    search = st.text_input(
        "Search learning area",
        placeholder="Ví dụ: RAG, ReAct, Prompt...",
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
# FILTER TOPICS
# ============================================================

filtered_topics = []

for topic in topics:
    topic_name = str(topic.get("topic", ""))

    if search:
        if search.lower() not in topic_name.lower():
            continue

    severity = topic.get("average_severity", 0)

    try:
        severity = float(severity)
    except (TypeError, ValueError):
        severity = 0

    if severity_filter == "High (≥ 4)" and severity < 4:
        continue

    if severity_filter == "Medium (3–3.99)" and not (3 <= severity < 4):
        continue

    if severity_filter == "Low (< 3)" and severity >= 3:
        continue

    filtered_topics.append(topic)


if sort_mode == "Most signals":
    filtered_topics.sort(
        key=lambda x: x.get("signal_count", 0),
        reverse=True,
    )
elif sort_mode == "Most students":
    filtered_topics.sort(
        key=lambda x: x.get("student_count", 0),
        reverse=True,
    )
elif sort_mode == "Highest severity":
    filtered_topics.sort(
        key=lambda x: x.get("average_severity", 0),
        reverse=True,
    )
else:
    filtered_topics.sort(
        key=lambda x: str(x.get("topic", "")).lower()
    )

# Always keep Other at the bottom.
other_topics = [
    t for t in filtered_topics
    if t.get("topic") == "Other"
]
filtered_topics = [
    t for t in filtered_topics
    if t.get("topic") != "Other"
]
filtered_topics.extend(other_topics)


st.caption(
    f"Showing {len(filtered_topics)} / {len(topics)} learning areas"
)


# ============================================================
# TOPIC CARDS
# ============================================================

if not filtered_topics:
    st.info("Không tìm thấy learning area phù hợp.")
else:
    for row_start in range(0, len(filtered_topics), 2):
        row_topics = filtered_topics[row_start:row_start + 2]
        columns = st.columns(2)

        for column, topic in zip(columns, row_topics):
            with column:
                name = topic.get("topic", "Unknown")
                signals = topic.get("signal_count", 0)
                students = topic.get("student_count", 0)
                severity = topic.get("average_severity", 0)

                try:
                    severity_value = float(severity)
                except (TypeError, ValueError):
                    severity_value = 0

                evidence = get_evidence(topic)

                st.markdown(
                    f"""
                    <div class="topic-card">
                        <div class="topic-name">{name}</div>
                        <div class="topic-meta">
                            {format_number(signals)} signals
                            · {format_number(students)} students
                            · {severity_color(severity_value)}
                            {severity_value:.2f}/5
                            · {severity_label(severity_value)}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if evidence:
                    first = evidence[0]

                    if isinstance(first, dict):
                        preview = first.get(
                            "student_question",
                            first.get("question", ""),
                        )
                    else:
                        preview = str(first)

                    if len(preview) > 150:
                        preview = preview[:150] + "..."

                    st.caption(f'“{preview}”')

                if st.button(
                    "View evidence →",
                    key=f"view_{name}",
                    use_container_width=True,
                ):
                    st.session_state.selected_topic = name
                    st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    f"Source: {format_number(source_results)} chatlog questions · "
    f"{format_number(valid_signals)} learning-gap signals · "
    f"{format_number(skipped_non_learning_total)} signals excluded from "
    f"the learning map."
)

st.caption(
    "VLearn Class Gap Map — AI-assisted analysis for instructors."
)
