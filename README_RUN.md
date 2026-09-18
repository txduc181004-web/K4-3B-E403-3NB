# 🎓 VLearn — Class Gap Map

> **AI-powered learning gap detection from classroom chatlogs**

VLearn Class Gap Map là prototype hỗ trợ giảng viên phát hiện các **chủ đề học tập có nhiều tín hiệu cần chú ý** từ chatlog của lớp học.

Thay vì phải đọc hàng nghìn câu hỏi rời rạc, hệ thống sử dụng LLM để phân tích câu hỏi, phát hiện learning signals, xác định phạm vi của signal, chuẩn hóa chủ đề và tổng hợp thành một **Class Gap Map**.

Giảng viên có thể xem số lượng tín hiệu, số học viên, mức độ severity, lecture liên quan và evidence gốc từ chatlog để tự quyết định có cần giải thích hoặc ôn tập lại hay không.

## Demo live AI trên giao diện

1. Bật Ollama và bảo đảm model đã có sẵn:

```powershell
ollama serve
ollama pull qwen2.5:3b
```

2. Ở terminal khác, chạy dashboard:

```powershell
streamlit run app/dashboard.py
```

3. Trong khu vực **Live AI analysis**, nhập vài câu hỏi hoặc upload CSV có cột `student_question`, rồi bấm **Send request to AI**. Giao diện sẽ hiển thị trạng thái đang gửi request, phản hồi JSON thật từ Ollama và số lượng kết quả nhận được.

Đây là luồng phù hợp để quay demo 30 giây: nhập dữ liệu → bấm gửi → chờ model xử lý → hiển thị kết quả trực tiếp.

---

## 1. Problem

Trong một lớp học đông, học viên có thể gửi rất nhiều câu hỏi qua hệ thống.

Các câu hỏi thường xuất hiện dưới nhiều dạng khác nhau:

* "Em chưa hiểu phần này."
* "Tại sao agent lại gọi tool?"
* "ReAct khác workflow như thế nào?"
* "Em vẫn chưa hiểu RAG."
* "Có thể giải thích lại phần này không?"

Giảng viên phải tự đọc và tổng hợp các câu hỏi này để nhận ra những chủ đề mà nhiều học viên đang gặp khó khăn.

Điều này tốn thời gian và có thể khiến các vấn đề lặp lại bị bỏ sót.

---

## 2. Solution

VLearn Class Gap Map xây dựng một pipeline AI để biến chatlog thành bản đồ các learning areas.

```text
Classroom Chatlog
       ↓
Candidate Extraction
       ↓
LLM Signal Detection
       ↓
Signal Scope Classification
       ↓
Topic Normalization
       ↓
Gap Aggregation
       ↓
gap_map.json
       ↓
Streamlit Dashboard
       ↓
Instructor Decision
```

Hệ thống không tự kết luận rằng một học viên "yếu" hay tự quyết định nội dung giảng dạy.

AI chỉ:

1. Phát hiện tín hiệu từ câu hỏi.
2. Phân loại loại tín hiệu.
3. Xác định signal có liên quan đến learning gap hay không.
4. Nhóm signal vào learning area.
5. Tổng hợp và cung cấp evidence.

**Quyết định giảng dạy cuối cùng thuộc về giảng viên.**

---

## 3. Current Prototype

Dataset hiện tại chứa khoảng **13,494 chatlog Q&A turns**.

Pipeline prototype lựa chọn **500 candidate questions** để đưa vào bước LLM analysis.

Kết quả hiện tại:

```text
Source results:              500
Learning-gap signals:        408
Non-signals:                  32
signal_type = NONE:           25
Non-learning signals:         35
Canonical learning areas:     17
```

Các learning areas bao gồm:

```text
AI Fundamentals
Prompt Engineering
LLM & Generative AI
Chatbot & AI Agent
ReAct & Tool Calling
RAG & Knowledge Systems
Fine-tuning & Alignment
Data Pipeline Engineering
Data Lakehouse
Machine Learning & Computer Vision
MLOps & AI Evaluation
Observability & Monitoring
Cloud & Infrastructure
AI Safety & Security
AI Product & UX
Memory Systems
Other
```

> Các con số trên là kết quả của prototype hiện tại và có thể thay đổi khi dataset, candidate extraction hoặc classifier được cập nhật.

---

## 4. Project Structure

```text
K4-3B-E403-3NB/
│
├── app/
│   ├── analyzer.py
│   ├── aggregator.py
│   ├── dashboard.py
│   ├── prompts.py
│   ├── retry_missing.py
│   ├── retry_single.py
│   ├── signal_classifier.py
│   └── topic_normalizer.py
│
├── data/
│   ├── sample/
│   │   ├── ai_analysis.json
│   │   ├── candidate_questions.csv
│   │   └── gap_map.json
│   │
│   └── vlearn-pack/
│       ├── chatlog/
│       ├── transcript/
│       └── slides/
│
├── scripts/
│   ├── extract_sample.py
│   ├── fix_analysis_schema.py
│   └── fix_missing_reason.py
│
├── .gitignore
├── README.md
├── README_RUN.md
├── canvas.md
├── requirements.txt
└── spec.md
```

---

# 5. Components

## `scripts/extract_sample.py`

Lọc dữ liệu chatlog để tìm các câu hỏi có khả năng chứa learning signals.

Các bước chính:

```text
Raw chatlog
    ↓
Remove preset questions
    ↓
Remove blank questions
    ↓
Heuristic signal filtering
    ↓
Candidate questions
```

Prototype hiện tại chọn tối đa 500 candidate questions.

---

## `app/analyzer.py`

Đây là thành phần sử dụng LLM để phân tích câu hỏi.

Model hiện tại:

```text
Qwen 2.5 3B
```

LLM xác định:

* `is_signal`
* `signal_type`
* `topic`
* `severity`
* `reason`

Ví dụ output:

```json
{
  "turn_id": "T12235",
  "is_signal": true,
  "signal_type": "CONCEPT_CONFUSION",
  "topic": "Action/Input schema",
  "severity": 4,
  "reason": "The student is asking for clarification about the structure and meaning of action input."
}
```

---

## `app/signal_classifier.py`

Không phải mọi signal do LLM phát hiện đều là learning gap.

Classifier chia chúng thành:

```text
LEARNING_GAP
PRODUCT_ISSUE
CONTENT_ISSUE
OFF_TOPIC
INSUFFICIENT_EVIDENCE
```

Chỉ `LEARNING_GAP` được đưa vào Class Gap Map.

Ví dụ:

```text
"Em chưa hiểu ReAct"
        ↓
LEARNING_GAP
```

Trong khi:

```text
"Slide này bị lỗi"
        ↓
CONTENT_ISSUE
```

hoặc:

```text
"Tôi không hiểu."
        ↓
INSUFFICIENT_EVIDENCE
```

Cách này giúp hệ thống tránh việc ép mọi câu hỏi vào một learning topic.

---

## `app/topic_normalizer.py`

Chuẩn hóa các topic do LLM tạo ra về taxonomy cố định.

Ví dụ:

```text
"tool calling"
"function calling"
"MCP"
"agent gọi tool"
        ↓
ReAct & Tool Calling
```

Điều này giúp Dashboard không xuất hiện quá nhiều nhóm nhỏ có ý nghĩa giống nhau.

---

## `app/aggregator.py`

Đây là bước tạo Class Gap Map.

Input:

```text
data/sample/ai_analysis.json
```

Output:

```text
data/sample/gap_map.json
```

Aggregator:

* Chỉ giữ `LEARNING_GAP`.
* Gom signal theo canonical topic.
* Tính số lượng signals.
* Tính số lượng students.
* Tính average severity.
* Gom signal types.
* Gom lecture context.
* Lưu evidence từ chatlog.

Ví dụ:

```text
ReAct & Tool Calling
├── 60 signals
├── 53 students
├── severity: 3.85 / 5
├── signal types
├── lecture breakdown
└── evidence
```

---

## `app/dashboard.py`

Streamlit Dashboard dành cho giảng viên.

Dashboard hiển thị:

### Overview

```text
Questions analyzed
Learning signals
Learning areas
Average severity
```

### Learning Area Cards

Mỗi card hiển thị:

```text
Topic
Signal count
Student count
Average severity
Evidence preview
```

### Filters

Có thể:

* Search learning area.
* Sort theo signals.
* Sort theo students.
* Sort theo severity.
* Lọc theo severity.

### Evidence Detail

Khi chọn:

```text
View evidence →
```

Dashboard hiển thị:

* Signal types.
* Lecture context.
* Original student questions.
* Severity.
* AI reasoning.

---

# 6. Signal Taxonomy

LLM hiện sử dụng các signal types:

| Signal type                 | Ý nghĩa                                      |
| --------------------------- | -------------------------------------------- |
| `CONCEPT_CONFUSION`         | Có dấu hiệu nhầm lẫn hoặc chưa rõ concept    |
| `REQUEST_REEXPLANATION`     | Yêu cầu giải thích lại                       |
| `WHY_QUESTION`              | Đặt câu hỏi về lý do/cơ chế                  |
| `IMPLEMENTATION_DIFFICULTY` | Gặp khó khăn khi triển khai hoặc thực hành   |
| `REPEATED_UNDERSTANDING`    | Tiếp tục thể hiện vấn đề hiểu sau giải thích |
| `NONE`                      | Không xác định được learning signal          |

Severity được biểu diễn trên thang:

```text
0 → 5
```

Severity là **mức độ của tín hiệu**, không phải điểm đánh giá năng lực của học viên.

---

# 7. Human-in-the-loop

Một nguyên tắc quan trọng của hệ thống:

```text
AI
 ↓
Detect signals
 ↓
Group signals
 ↓
Provide evidence
 ↓
Instructor
 ↓
Teaching decision
```

AI **không**:

* Gắn nhãn học viên là yếu.
* Kết luận một học viên chắc chắn không hiểu bài.
* Tự thay đổi nội dung bài giảng.
* Tự quyết định giảng viên phải dạy lại nội dung nào.

AI cung cấp evidence để giảng viên đưa ra quyết định.

---

# 8. Requirements

Khuyến nghị:

```text
Python 3.10+
Ollama
Qwen 2.5 3B
Streamlit
pandas
python-dotenv
ollama
```

---

# 9. Setup

## 9.1. Clone repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd K4-3B-E403-3NB
```

## 9.2. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

## 9.3. Install dependencies

```bash
pip install pandas python-dotenv ollama streamlit
```

---

# 10. Setup Ollama

Cài Ollama nếu máy chưa có.

Sau đó tải model:

```bash
ollama pull qwen2.5:3b
```

Kiểm tra:

```bash
ollama run qwen2.5:3b
```

Nếu model trả lời được thì Ollama đã hoạt động.

---

# 11. Environment Variables

Tạo file:

```text
.env
```

Nội dung:

```env
LLM_PROVIDER=ollama
OLLAMA_MODEL=qwen2.5:3b
OLLAMA_HOST=http://localhost:11434
```

Không commit API keys hoặc thông tin bí mật lên GitHub.

---

# 12. Run the Pipeline

## Step 1 — Extract candidates

```bash
python3 scripts/extract_sample.py
```

Output:

```text
data/sample/candidate_questions.csv
```

---

## Step 2 — Run LLM analysis

```bash
python3 -m app.analyzer
```

Output:

```text
data/sample/ai_analysis.json
```

Nếu một số batch gặp lỗi trong quá trình chạy, có thể sử dụng các script retry:

```bash
python3 -m app.retry_missing
```

hoặc:

```bash
python3 -m app.retry_single
```

---

## Step 3 — Build Class Gap Map

```bash
python3 -m app.aggregator
```

Output:

```text
data/sample/gap_map.json
```

Ví dụ:

```text
DONE
Canonical learning areas: 17
Output: data/sample/gap_map.json
Source results: 500
Valid learning-gap signals: 408
```

---

# 13. Run Dashboard

Sau khi có:

```text
data/sample/gap_map.json
```

chạy:

```bash
streamlit run app/dashboard.py
```

Streamlit sẽ mở Dashboard trên trình duyệt.

Dashboard **không gọi LLM trực tiếp**.

Nó đọc kết quả đã được tạo bởi pipeline:

```text
gap_map.json
    ↓
dashboard.py
    ↓
Streamlit UI
```

Do đó nếu dữ liệu được cập nhật, có thể chạy lại:

```bash
python3 -m app.aggregator
```

sau đó refresh Dashboard.

---

# 14. Demo Flow

Một flow demo đề xuất:

```text
1. Open VLearn Class Gap Map
        ↓
2. Show overall metrics
        ↓
3. Select "ReAct & Tool Calling"
        ↓
4. Show signal count + student count
        ↓
5. Show signal types
        ↓
6. Show lecture context
        ↓
7. Show original chatlog evidence
        ↓
8. Explain Human-in-the-loop
        ↓
9. Search another topic such as RAG
```

Thông điệp chính:

> **AI biến nhiều câu hỏi rời rạc trong chatlog thành các learning areas có evidence để giảng viên dễ xác định nơi cần chú ý.**

---

# 15. Example User Journey

Giả sử chatlog có các câu hỏi:

```text
"Em chưa hiểu ReAct."

"Tại sao agent lại gọi tool?"

"Tool calling hoạt động như thế nào?"

"Action input là gì?"
```

Pipeline xử lý:

```text
Chatlog
   ↓
LLM
   ↓
Learning signals
   ↓
ReAct & Tool Calling
   ↓
Aggregation
```

Dashboard có thể hiển thị:

```text
ReAct & Tool Calling

60 signals
53 students
3.85 / 5
```

Giảng viên click:

```text
View evidence →
```

và xem các câu hỏi gốc.

Từ evidence đó, giảng viên có thể tự quyết định liệu cần:

* Giải thích lại concept.
* Ôn tập.
* Bổ sung ví dụ.
* Hoặc không cần can thiệp.

---

# 16. Data Flow

```text
                13,494 CHATLOG
                       │
                       ▼
             Candidate Extraction
                       │
                       ▼
                  500 Questions
                       │
                       ▼
                Qwen 2.5 3B
                       │
                       ▼
               Signal Detection
                       │
                       ▼
              Signal Scope Classifier
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
 LEARNING_GAP    PRODUCT_ISSUE    OFF_TOPIC
        │
        ▼
  Topic Normalizer
        │
        ▼
  Canonical Topics
        │
        ▼
    Aggregator
        │
        ▼
   gap_map.json
        │
        ▼
 Streamlit Dashboard
        │
        ▼
    Instructor
```

---

# 17. Limitations

Prototype hiện tại có một số giới hạn:

1. LLM analysis được chạy trên một tập candidate questions thay vì toàn bộ chatlog.
2. Topic normalization sử dụng taxonomy được định nghĩa trước.
3. Severity là tín hiệu do model ước lượng, không phải điểm đo lường khách quan.
4. Một số câu hỏi quá ngắn hoặc thiếu context có thể được đưa vào `INSUFFICIENT_EVIDENCE`.
5. Dashboard hiện tại đọc dữ liệu đã được phân tích và chưa phải hệ thống realtime.
6. Prototype chưa tự động cập nhật Class Gap Map ngay khi có câu hỏi mới.

Do đó, kết quả cần được xem là **decision support cho giảng viên**, không phải kết luận tự động về năng lực học tập.

---

# 18. Safety & Data Handling

Student content được xem là **data**, không phải instruction.

Nếu chatlog chứa prompt injection hoặc nội dung yêu cầu thay đổi hành vi của AI, nội dung đó phải được xem như dữ liệu cần phân tích, không được thực thi như system instruction.

Hệ thống cũng tránh sử dụng ngôn ngữ mang tính đánh giá cá nhân như:

```text
"student yếu"
"student kém"
"student không có năng lực"
```

Thay vào đó sử dụng:

```text
"learning signal"
"evidence"
"topic requiring instructor review"
```

---

# 19. Product Boundary

### AI làm

```text
Detect
→ Classify
→ Normalize
→ Aggregate
→ Provide evidence
```

### AI không làm

```text
Diagnose student ability
→ Automatically decide teaching intervention
→ Automatically modify course content
```

### Human

```text
Review evidence
→ Validate signal
→ Decide intervention
```

---

# 20. Expected Outcome

VLearn Class Gap Map giúp chuyển đổi:

```text
Thousands of fragmented chatlog messages
```

thành:

```text
Structured learning areas
        +
Signal counts
        +
Student counts
        +
Severity
        +
Lecture context
        +
Original evidence
```

Từ đó giảm lượng thông tin mà giảng viên phải tự tổng hợp và giúp họ nhanh chóng xác định những chủ đề đáng xem xét.

---

## 21. Project Status

### Backend

* [x] Chatlog processing
* [x] Candidate extraction
* [x] LLM signal detection
* [x] Signal scope classification
* [x] Topic normalization
* [x] Gap aggregation
* [x] Evidence preservation
* [x] JSON output

### Frontend

* [x] Streamlit Dashboard
* [x] Overview metrics
* [x] Learning area cards
* [x] Search
* [x] Sorting
* [x] Severity filter
* [x] Evidence detail
* [x] Lecture context
* [x] Human-in-the-loop explanation

### Remaining for final submission

* [ ] Final `spec.md`
* [ ] Final end-to-end validation
* [ ] Final demo recording
* [ ] Final README review
* [ ] Final Git commit and push

---

## 23. Core Message

> **VLearn Class Gap Map không cố thay thế giảng viên. Nó giúp giảng viên nhìn thấy những tín hiệu học tập đang bị phân tán trong chatlog, gom chúng thành các learning areas và cung cấp evidence để con người đưa ra quyết định tốt hơn.**

---
