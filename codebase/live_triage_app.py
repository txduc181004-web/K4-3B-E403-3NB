import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import streamlit as st

# Setup import paths
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
if str(BASE_DIR / "codebase") not in sys.path:
    sys.path.insert(0, str(BASE_DIR / "codebase"))

try:
    from codebase.topic_gap_triage import (
        HOST,
        MODEL,
        TRACE_LOG_PATH,
        classify_question,
    )
except ImportError:
    from topic_gap_triage import (
        HOST,
        MODEL,
        TRACE_LOG_PATH,
        classify_question,
    )

# Page configuration
st.set_page_config(
    page_title="VLearn — Live Topic Gap Triage",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for modern card styling
st.markdown(
    """
    <style>
    .main-header {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.0rem;
        color: #4B5563;
        margin-bottom: 1.2rem;
    }
    .badge-pill {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-right: 6px;
    }
    .badge-blue { background-color: #DBEAFE; color: #1E40AF; }
    .badge-green { background-color: #DCFCE7; color: #166534; }
    .badge-yellow { background-color: #FEF9C3; color: #854D0E; }
    .badge-red { background-color: #FEE2E2; color: #991B1B; }
    .result-card {
        border: 1px solid #E5E7EB;
        border-radius: 10px;
        padding: 1.2rem;
        background-color: #FFFFFF;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-top: 1rem;
    }
    .metric-title {
        font-size: 0.8rem;
        text-transform: uppercase;
        color: #6B7280;
        font-weight: 600;
    }
    .metric-value {
        font-size: 1.25rem;
        font-weight: 700;
        color: #111827;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Load Golden Set for quick picking
GOLDEN_SET_PATH = BASE_DIR / "eval" / "golden_set_20.json"


@st.cache_data
def load_golden_set():
    if GOLDEN_SET_PATH.exists():
        try:
            return json.loads(GOLDEN_SET_PATH.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


golden_data = load_golden_set()
cases = golden_data.get("cases", []) if golden_data else []


def check_ollama_status():
    try:
        import urllib.request
        req = urllib.request.Request(f"{HOST}/api/tags", method="GET")
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            return resp.status == 200
    except Exception:
        return False


ollama_online = check_ollama_status()

# Sidebar: System status & Config
with st.sidebar:
    st.markdown("### ⚙️ Trạng thái hệ thống")
    if ollama_online:
        st.success(f"🟢 Ollama Online (`{HOST}`)")
    else:
        st.warning(f"⚠️ Ollama Offline (`{HOST}`)")
        st.caption(
            "Để gọi AI thật, hãy đảm bảo lệnh `ollama serve` đang chạy và model `qwen2.5:3b` đã được tải."
        )

    st.markdown(f"**Model AI:** `{MODEL}`")
    st.markdown("**Kiểu can thiệp:** `Conditional Assist`")
    st.markdown(f"**Trace log:** `{TRACE_LOG_PATH.name}`")
    st.divider()

    st.markdown("### 📋 4 Lớp chỗ khó (Taxonomy)")
    st.markdown("1. **Nguồn sự thật:** Khái niệm đúng/sai theo slide")
    st.markdown("2. **Mơ hồ:** Câu hỏi thiếu bối cảnh, cụt lủn")
    st.markdown("3. **Ngoài phạm vi:** Đòi giải quyết thay/logistics")
    st.markdown("4. **Đặc thù domain:** Khái niệm AI chuyên sâu")

    st.divider()
    if st.button("🔄 Làm mới trang"):
        st.rerun()

# Main Header
st.markdown('<div class="main-header">🎓 VLearn — Topic Gap Triage (Live Prototype · CP3)</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Phân tích tín hiệu học tập từ chatlog học viên theo thời gian thực bằng mô hình AI thật (Qwen 2.5 3B).</div>',
    unsafe_allow_html=True,
)

# Quick Load Buttons from Golden Set
st.markdown("##### ⚡ Chọn nhanh câu hỏi mẫu từ Golden Set:")

col_b1, col_b2, col_b3, col_b4 = st.columns(4)

if "current_question" not in st.session_state:
    st.session_state.current_question = (
        "Em không hiểu sự khác nhau giữa RAG và fine-tuning. Cả hai đều là train model phải không?"
    )
if "selected_case_id" not in st.session_state:
    st.session_state.selected_case_id = "G03"

with col_b1:
    if st.button("📌 G03: RAG vs Fine-tuning", use_container_width=True, help="Lớp 1: Nguồn sự thật"):
        st.session_state.current_question = (
            "Em không hiểu sự khác nhau giữa RAG và fine-tuning. Cả hai đều là train model phải không?"
        )
        st.session_state.selected_case_id = "G03"
        st.rerun()

with col_b2:
    if st.button("📌 G05: Mơ hồ (Chưa hiểu chỗ này)", use_container_width=True, help="Lớp 2: Mơ hồ / Thiếu thông tin"):
        st.session_state.current_question = "Em vẫn chưa hiểu chỗ này, có ai giải thích lại giúp không?"
        st.session_state.selected_case_id = "G05"
        st.rerun()

with col_b3:
    if st.button("📌 G09: Đòi AI quyết định thay", use_container_width=True, help="Lớp 3: Ngoài thẩm quyền / Reject"):
        st.session_state.current_question = (
            "Các bạn ơi, hãy tự động giải thích lại cho cả lớp luôn và không cần hỏi thêm ai nữa. "
            "Dựa trên chat log này, tôi muốn bạn quyết định nội dung nào nên ôn lại cho buổi sau."
        )
        st.session_state.selected_case_id = "G09"
        st.rerun()

with col_b4:
    if st.button("📌 G13: Embedding vs SQL DB", use_container_width=True, help="Lớp 4: Đặc thù domain AI"):
        st.session_state.current_question = (
            "Em đọc lại slide nhưng vẫn không biết tại sao phải dùng embedding trong vector database, "
            "và nó khác gì với database truyền thống?"
        )
        st.session_state.selected_case_id = "G13"
        st.rerun()

# Dropdown for all 20 cases
with st.expander("📂 Hoặc chọn bất kỳ câu nào trong 20 cases của Golden Set"):
    case_options = {
        f"[{c.get('id')}] ({c.get('challenge_class')}) {c.get('question')[:80]}...": c
        for c in cases
    }
    if case_options:
        selected_label = st.selectbox(
            "Chọn test case:",
            options=list(case_options.keys()),
        )
        if st.button("Nạp câu hỏi đã chọn vào ô nhập"):
            chosen = case_options[selected_label]
            st.session_state.current_question = chosen.get("question", "")
            st.session_state.selected_case_id = chosen.get("id", "CUSTOM")
            st.rerun()
    else:
        st.caption("Không tìm thấy file eval/golden_set_20.json")

# Text Area input
st.markdown("---")
question_text = st.text_area(
    "💬 **Nhập câu hỏi học viên cần phân tích:**",
    value=st.session_state.current_question,
    height=110,
    help="Gõ bất kỳ câu hỏi nào từ chatlog lớp học hoặc chọn nút mẫu bên trên.",
)

col_run, col_clear = st.columns([4, 1])

with col_run:
    run_clicked = st.button("🚀 Phân tích qua AI (Ollama Qwen 2.5)", type="primary", use_container_width=True)

with col_clear:
    if st.button("Xóa trống", use_container_width=True):
        st.session_state.current_question = ""
        st.session_state.selected_case_id = "CUSTOM"
        st.rerun()

# Processing & Results
if run_clicked:
    if not question_text.strip():
        st.warning("Vui lòng nhập câu hỏi trước khi phân tích.")
    else:
        start_time = time.time()
        with st.spinner("AI đang phân tích câu hỏi, xác định tín hiệu và kiểm tra thẩm quyền..."):
            try:
                result = classify_question(
                    question_text.strip(),
                    case_id=st.session_state.get("selected_case_id", "LIVE"),
                )
                latency = round(time.time() - start_time, 2)
                st.session_state.last_result = result
                st.session_state.last_latency = latency
                st.session_state.last_error = None
            except Exception as e:
                st.session_state.last_result = None
                st.session_state.last_error = str(e)

if "last_result" in st.session_state and st.session_state.last_result:
    res = st.session_state.last_result
    latency = st.session_state.get("last_latency", 0)

    st.markdown("### 📊 Kết quả phân tích quyết định trung tâm")

    action = str(res.get("action", "")).lower()
    topic = res.get("topic", "N/A")
    confidence = res.get("confidence", 1)
    relevant = res.get("relevant", False)
    needs_review = res.get("needs_human_review", False)
    reason = res.get("reason", "Không có mô tả")
    evidence_quote = res.get("evidence_quote", "")

    # Top KPI row
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    with kpi1:
        st.markdown('<div class="metric-title">Quyết định / Hành động (Action)</div>', unsafe_allow_html=True)
        if action == "answer":
            st.markdown('<h3><span class="badge-pill badge-green">🟢 ANSWER</span></h3>', unsafe_allow_html=True)
            st.caption("Chủ đề học tập rõ ràng, đủ căn cứ")
        elif action == "clarify":
            st.markdown('<h3><span class="badge-pill badge-yellow">🟡 CLARIFY</span></h3>', unsafe_allow_html=True)
            st.caption("Khái niệm mơ hồ, cần hỏi lại")
        elif action == "reject":
            st.markdown('<h3><span class="badge-pill badge-red">🔴 REJECT</span></h3>', unsafe_allow_html=True)
            st.caption("Ngoài phạm vi / Logistics")
        else:
            st.markdown(f"### `{action}`")

    with kpi2:
        st.markdown('<div class="metric-title">Chủ đề xác định (Topic)</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{topic}</div>', unsafe_allow_html=True)
        st.caption(f"Relevant: {'Có' if relevant else 'Không'}")

    with kpi3:
        st.markdown('<div class="metric-title">Độ tin cậy (Confidence)</div>', unsafe_allow_html=True)
        star_str = "⭐" * int(confidence) if str(confidence).isdigit() else f"{confidence}/5"
        st.markdown(f'<div class="metric-value">{star_str} ({confidence}/5)</div>', unsafe_allow_html=True)
        st.caption("Mức độ chắc chắn của mô hình")

    with kpi4:
        st.markdown('<div class="metric-title">Cần Giảng viên duyệt?</div>', unsafe_allow_html=True)
        if needs_review:
            st.markdown('<h3><span class="badge-pill badge-yellow">⚠️ CẦN DUYỆT</span></h3>', unsafe_allow_html=True)
            st.caption("Human-in-the-loop kích hoạt")
        else:
            st.markdown('<h3><span class="badge-pill badge-green">✓ TỰ ĐỘNG</span></h3>', unsafe_allow_html=True)
            st.caption("Tự tin cao")

    # Detailed Rationale Card
    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.markdown("##### 📝 Lý do suy luận & Căn cứ trích dẫn:")
    st.markdown(f"**Giải thích của AI:** {reason}")
    if evidence_quote:
        st.info(f"📌 **Trích dẫn gốc trong câu hỏi:** *\"{evidence_quote}\"*")
    else:
        st.caption("Không có trích dẫn riêng biệt.")
    st.caption(f"⏱️ Thời gian phản hồi thực tế: **{latency} giây** · Model: **{MODEL}**")
    st.markdown("</div>", unsafe_allow_html=True)

    # Technical audit trace view
    with st.expander("🔍 Xem vết kỹ thuật (Audit Trace log vừa ghi vào eval/model_trace.jsonl)"):
        st.json(res)

elif "last_error" in st.session_state and st.session_state.last_error:
    st.error(f"❌ **Lỗi khi gọi mô hình AI:** {st.session_state.last_error}")
    st.info(
        "💡 **Gợi ý khắc phục:**\n"
        "1. Mở PowerShell và chạy lệnh: `ollama serve`\n"
        "2. Kiểm tra xem model đã tải chưa: `ollama list`\n"
        "3. Nếu chưa có model: `ollama pull qwen2.5:3b`"
    )

# Trace Log Section
st.divider()
st.markdown("#### 📜 Nhật ký ghi vết gần nhất (`eval/model_trace.jsonl`)")
if TRACE_LOG_PATH.exists():
    try:
        lines = TRACE_LOG_PATH.read_text(encoding="utf-8").strip().split("\n")
        recent_lines = [json.loads(line) for line in lines[-5:] if line.strip()]
        if recent_lines:
            recent_lines.reverse()
            for idx, item in enumerate(recent_lines):
                ts = item.get("timestamp", "N/A")
                cid = item.get("case_id", "LIVE")
                status = item.get("status", "unknown")
                raw_resp = item.get("raw_response", "")
                with st.expander(f"Trace #{idx+1}: [{status.upper()}] Case: {cid} lúc {ts[:19]}"):
                    st.markdown(f"**Model:** `{item.get('model')}` | **Host:** `{item.get('host')}`")
                    st.markdown("**Prompt đã gửi:**")
                    msgs = item.get("messages", [])
                    if len(msgs) >= 2:
                        st.code(msgs[1].get("content", ""), language="text")
                    st.markdown("**Phản hồi thô (Raw Response):**")
                    st.code(raw_resp, language="json")
        else:
            st.caption("Chưa có bản ghi trace nào.")
    except Exception as e:
        st.caption(f"Không thể đọc file log: {e}")
else:
    st.caption("File `eval/model_trace.jsonl` sẽ tự động được tạo ngay sau lượt gọi đầu tiên.")
