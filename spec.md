# AI SPEC — Bản đồ lỗ hổng của lớp · Nhóm 3NB · Zone E403

> Mốc chốt: CP4, trước 21:00 ngày 18/09/2026. Quality bar bên dưới được khóa tại thời điểm nộp spec và không hạ sau khi xem các lượt chạy.

**Hướng:** [x] A — VLearn  [ ] B — Trợ lý Học viên  [ ] C — Làn mở  
**Loại:** [ ] Tối ưu tính năng có sẵn  [x] Tính năng mới  
**Đội trưởng:** Trần Xuân Đức · **Lớp/phòng:** 3B / E403

## §1. User & Job

- **Job executor + workflow:** Giảng viên hoặc TA của một lớp: (1) nạp chatlog, (2) xem các learning signal, (3) xem topic được chuẩn hóa và xếp hạng, (4) mở quote/evidence gốc, (5) tự quyết định có giảng lại hay không.
- **Core JTBD:** Khi chuẩn bị hoặc điều chỉnh buổi học, giảng viên muốn biết chủ đề nào trong lớp đang có nhiều dấu hiệu chưa hiểu để ưu tiên giải thích hoặc ôn tập đúng chỗ.
- **Problem statement:** Trong lớp đông, giảng viên phải đọc và tổng hợp nhiều câu hỏi rời rạc để nhận ra vấn đề lặp lại. Việc này tốn thời gian, dễ nhầm câu hỏi logistics với câu hỏi kiến thức và có thể bỏ sót lỗ hổng cần xử lý.
- **Evidence chuẩn A:** Mining từ chatlog VLearn đã ẩn danh: 13.494 lượt hỏi-đáp, khoảng thời gian 22/07 18:00–15/09 17:57 (giờ Việt Nam), nguồn được mô tả trong `canvas.md`; prototype lấy tối đa 500 candidate questions. Đây là bằng chứng hành vi, không phải suy đoán nhu cầu.
- **Evidence chuẩn B:** Nhóm ghi nhận feedback thăm dò từ 10 người, 7/10 xác nhận từng mất thời gian tìm lại câu hỏi/nội dung chưa hiểu. Raw survey không được commit vì dữ liệu lớp học; đây là số liệu tự khai và chưa đủ để tuyên bố đại diện cho toàn khóa.
- **Quote nguyên văn + nguồn:**
  - “Em vẫn chưa hiểu sự khác nhau giữa RAG và fine-tuning.” — Thu, `CHAT-014`.
  - “Em đọc lại slide nhưng vẫn không biết tại sao phải dùng embedding.” — Bình, `CHAT-027`.
  - “Có ai giải thích lại giúp em đoạn retrieval được không?” — Kiên, `CHAT-035`.
  - “Em làm theo ví dụ nhưng kết quả không giống trong bài giảng.” — Thu, `CHAT-041`.
  - “Em không chắc là mình hiểu đúng cách hoạt động của vector database.” — Bình, `CHAT-056`.

## §2. Impact & quyết định chọn

| Ứng viên/pain | Bao nhiêu người | Tần suất | Tốn gì mỗi lần | Khả thi |
|---|---:|---:|---:|---|
| Tìm chủ đề kiến thức lặp lại để biết lớp cần ôn gì | 8/10 lượt phản hồi liên quan | 1–3 lần/tuần | 10–15 phút đọc lại chatlog, slide, câu hỏi cũ | Cao; dữ liệu đã có trong chatlog |
| Tự tìm lại câu hỏi/nội dung cá nhân | 1/10 | khoảng 1 lần/tuần | 5 phút tìm kiếm | Trung bình; cần search cá nhân, không tạo giá trị lớp học |
| Tìm tài liệu hoặc link bài giảng | 1/10 | khoảng 1 lần/tuần | 5–10 phút | Thấp cho lát cắt này; là vấn đề logistics |
| Giải thích lại từng câu hỏi cho từng học viên | 3/10 có nhu cầu | 1–2 lần/tuần | 10–15 phút mỗi câu trả lời | Không chọn; cần tutor workflow và người duyệt |

- **Ứng viên đã loại:**
  - Search cá nhân: chỉ 1/10, tần suất thấp và không giúp giảng viên nhìn vấn đề chung của lớp.
  - Tìm link/tài liệu: chỉ 1/10, thuộc logistics/product issue; classifier phải loại khỏi learning-gap map.
  - Tự động trả lời từng học viên: cost-of-error cao, vượt vai trò triage và có thể thay thế phán đoán của TA.
- **Ứng viên chọn:** Bản đồ các topic có learning signal lặp lại. Lý do định lượng: 8/10 phản hồi gắn với việc xác định phần chưa hiểu; mỗi lần mất 10–15 phút; cùng dữ liệu có thể tái sử dụng cho nhiều giảng viên và có evidence để kiểm tra.

## §3. Giải pháp tương tự đã nghiên cứu

| Sản phẩm | Flow của họ | Đáng học | Đáng né | Mình khác gì |
|---|---|---|---|---|
| NotebookLM / research assistant | Nạp tài liệu → hỏi → nhận câu trả lời kèm nguồn | Luôn hiển thị nguồn/đoạn trích để kiểm chứng | Ép chatlog rời rạc thành một kết luận rộng; dễ sinh topic giả | Không trả lời câu hỏi; phát hiện topic khó lặp lại của cả lớp từ chatlog |
| ChatGPT/Claude study mode | Học viên hỏi → hệ thống giải thích theo ngữ cảnh → hỏi tiếp | Điều chỉnh giải thích và nhận biết lúc người học mất mạch | Dài dòng, không cho biết vấn đề nào lặp lại ở cấp lớp | Phục vụ giảng viên triage và ưu tiên, không làm tutor cá nhân |
| Khanmigo / class tutor | Hỗ trợ từng học viên → theo dõi tiến độ → gợi ý can thiệp | Tách câu hỏi hiện tại khỏi tín hiệu khó kéo dài; giữ human oversight | Để hệ thống chốt thay người dạy hoặc suy luận năng lực cá nhân | Chỉ tổng hợp tín hiệu có căn cứ; quyết định dạy lại thuộc giảng viên |

## §4. Thiết kế

- **Lát cắt một câu:** Một giảng viên xem chatlog của một lớp; hệ thống nhóm các câu hỏi có dấu hiệu lỗ hổng thành topic có evidence; giảng viên quyết định topic nào cần ôn lại.
- **Non-goals:**
  1. Không trả lời thay TA từng câu hỏi của học viên.
  2. Không chấm điểm, gắn nhãn “yếu”, hay suy luận tâm lý/năng lực cá nhân.
  3. Không tự quyết định nội dung giảng dạy hoặc tự gửi phản hồi cho cả lớp.
  4. Không dự đoán hành vi ngoài chatlog và ngữ cảnh bài học được cung cấp.
  5. Không dùng dữ liệu cá nhân ngoài phạm vi lớp học.
- **Mức prototype:** [ ] Sketch  [ ] Mock  [x] Working. Thật: candidate extraction, LLM analysis bằng Ollama `qwen2.5:3b`, scope classification, topic normalization, aggregation và dashboard evidence. Chưa hoàn thiện: chỉnh/gộp topic trực tiếp trên dashboard và luồng xác nhận bắt buộc trước khi xuất bản kết luận.
- **Automation:** [ ] augment  [x] conditional  [ ] automate. Hệ thống tự phát hiện, phân loại và gom nhóm khi có căn cứ; chuyển sang `clarify`, `INSUFFICIENT_EVIDENCE` hoặc human review khi câu hỏi mơ hồ. Cost-of-error của gán sai topic là giảng viên ôn sai; cost-of-error của bỏ qua một câu mơ hồ thấp hơn, nên ưu tiên không đoán.

### §4b. Nguyên tắc HAX/PAIR đã áp dụng

| Nguyên tắc | Áp dụng cụ thể |
|---|---|
| HAX G1 — Capabilities & limitations | Dashboard nói rõ đây là tín hiệu từ chatlog, không phải kết luận năng lực hay quyết định dạy học. |
| HAX G2 — Confidence | Lưu severity/reason và yêu cầu human review cho case thiếu căn cứ; không biến câu hỏi mơ hồ thành topic chắc chắn. |
| HAX G9 — Easy correction | Thiết kế mục tiêu cho phép bỏ topic, đổi nhãn, gộp topic và chạy lại subset; UI correction chưa kịp hoàn thiện ở CP4. |
| HAX G10 — Narrow scope under uncertainty | Classifier tách `INSUFFICIENT_EVIDENCE`, logistics, product/content issue khỏi `LEARNING_GAP`. |
| HAX G11 — Explain why | Mỗi topic hiển thị signal count, student count, severity, lecture context và tối đa 5 evidence questions. |
| PAIR — Feedback and control | Người dùng giữ quyền xác nhận topic và quyết định ôn lại; hệ thống không tự publish hành động sư phạm. |
| PAIR — Graceful failure | Ngoài phạm vi hoặc không đủ dữ liệu thì reject/clarify, không bịa topic hay câu trả lời. |

## §5. Kiểu lỗi — 4 lớp chỗ khó + kịch bản

Mỗi dòng theo mẫu `tình huống | lớp | hành vi mong muốn | nguyên tắc áp`.

| Tình huống | Lớp | Hành vi mong muốn | Nguyên tắc áp |
|---|---|---|---|
| “Embedding” và “vector database” bị gộp dù người học hỏi hai khái niệm khác nhau | ① Nguồn sự thật | Hiển thị hai nhãn khả dĩ và quote; không gộp chắc chắn | G11, Explainability |
| “Không hiểu đoạn này ở slide 6” không có nội dung được trích | ① Nguồn sự thật | Đưa vào nhóm mơ hồ hoặc yêu cầu thêm context | G10, Graceful failure |
| Có từ “RAG” nhưng không rõ hỏi retrieval, fine-tuning hay evaluation | ② Mơ hồ | `clarify`, confidence thấp, chỉ ra context còn thiếu | G2, G10 |
| “Vẫn chưa hiểu chỗ này” không có topic | ② Mơ hồ | Không gán topic; yêu cầu người dùng bổ sung | G1, Feedback |
| Yêu cầu AI tự quyết định buổi sau phải dạy gì | ③ Ngoài phạm vi | Giới hạn thành gợi ý có evidence; người dạy quyết định | G1, Human control |
| Yêu cầu AI trả lời thay mọi học viên trên Discord | ③ Ngoài phạm vi | `reject` và nêu rõ hệ thống chỉ triage topic | Scope control |
| “Link bài giảng đâu?” bị tính như lỗ hổng kiến thức | ③ Ngoài phạm vi | Loại thành logistics/product issue | G10, Graceful failure |
| AI nhầm vector database với database truyền thống | ④ Đặc thù domain | Hiển thị evidence/context, yêu cầu giảng viên duyệt | G2, G11 |
| Topic fine-tuning chứa cả câu hỏi về training/validation split | ④ Đặc thù domain | Tách topic hoặc đưa hai nhãn khả dĩ, không tự gộp | G9, Explainability |
| Cùng prompt cho output embedding khác nhau, model bỏ qua cue “randomness” | ④ Đặc thù domain | Nhận diện nondeterminism; nếu chưa chắc thì `clarify` nhưng giữ cue làm evidence | G11, G17 |

**Case demo đáng sợ nhất:** gộp sai hai khái niệm kỹ thuật cốt lõi rồi khiến giảng viên ôn sai, và biến yêu cầu ngoài phạm vi thành quyết định tự động. Hai case này có thể gây hại trực tiếp dù UI vẫn trông “đúng”.

## §6. Bốn đường đi của trải nghiệm

- **Happy path:** Giảng viên nạp CSV → hệ thống phân tích → chỉ giữ learning gaps → chuẩn hóa topic → xếp hạng theo signal/student/severity → mở evidence → giảng viên tự chọn hành động.
- **Low-confidence (②):** Câu hỏi ít context hoặc topic mâu thuẫn → hiển thị `clarify`/human review, lý do và phần context cần bổ sung; không đưa vào kết luận chắc chắn.
- **Failure/không căn cứ (①):** Không có câu hỏi đủ rõ → hiển thị “chưa đủ dữ liệu”, giữ turn ở nhóm `INSUFFICIENT_EVIDENCE`, không tạo topic giả.
- **Correction (user sửa):** Mục tiêu sản phẩm là cho phép sửa label, gộp/tách topic, bỏ evidence sai và chạy lại subset; tại CP4 dashboard mới hiển thị evidence/filter, chưa hoàn tất các control này.
- **Ngoài phạm vi (③):** Yêu cầu trả lời thay học viên, tự quyết định bài dạy hoặc bịa nội dung → `reject`/giới hạn scope, không thực hiện hành động đó.
- **Đặc thù domain (④):** Với RAG, embedding, vector DB, fine-tuning, transformer/RNN → chỉ dùng cue và context có trong input; thiếu căn cứ thì không chốt.

## §7. Kiểm thử

- **Chiều chất lượng và định nghĩa kiểm chứng được:**
  - **Behavior/action:** action `answer`, `clarify`, `reject` đúng expected behavior của từng case.
  - **Evidence/factuality:** topic hoặc action phải trace được về `source`, `turn_id`/câu hỏi; không suy diễn khi evidence thiếu.
  - **Scope precision:** logistics, out-of-scope, product/content issue không được đưa vào learning-gap map.
  - **Domain distinction:** các cặp khái niệm dễ nhầm phải được tách hoặc yêu cầu làm rõ.
  - **Coverage:** báo cáo đủ 20 case và breakdown theo 4 lớp, không chỉ báo một phần trăm tổng.
- **Golden set:** [eval/golden_set_20.json](eval/golden_set_20.json), 20 case: 5 source-truth, 5 ambiguity, 5 scope, 5 domain; có input grid 4 chiều và ghi rõ 3 ô chưa phủ. Bộ gồm case từ chatlog/biến thể và case synthetic để kiểm tra từ chối.
- **Công thức pass một case:** `pass = action đúng AND scope đúng AND không vi phạm điều kiện evidence`. Với case `answer`, phải có evidence traceable; với `clarify`, phải chỉ ra thiếu/mâu thuẫn context; với `reject`, phải từ chối đúng phạm vi.
- **Quality bar đã khóa:** **“Đạt khi ≥80% case qua bộ 20 case, và 100% case ngoài phạm vi/logistics bị reject hoặc loại khỏi learning-gap map, 100% case thiếu evidence không được trả lời chắc chắn; mọi topic được xuất ra phải trace được về ít nhất một `turn_id` hoặc câu hỏi nguồn.”**
- **Khai báo chưa hoàn thiện:** chưa có đo user validation; 3 ô input-grid chưa phủ là `ambiguous|logistics|generic|missing`, `ambiguous|out_of_scope|generic|missing`, `clear|learning|generic|missing`; chưa có regression test riêng cho correction UI. Run 02/03 đã chạy trên cùng golden set nhưng chưa thay thế quality bar.

### Kết quả các lượt chạy

| Lượt chạy | Kết quả | Đối chiếu quality bar | File / ghi chú |
|---|---:|---|---|
| Run 01 / CP3 | 18/20 = 90.0% | Vượt ngưỡng 80%; 5/5 ambiguity và 5/5 domain; 5/5 scope có action đúng, nhưng G10 trượt do evaluator lệch nhãn topic | [eval/run_01_results.json](eval/run_01_results.json) |
| Run 02 / sau prompt fix | 20/20 = 100.0% | Đạt quality bar; 5/5 ở cả 4 lớp; G17 đã nhận diện `model stochasticity / nondeterminism` | [eval/run_02_results.json](eval/run_02_results.json); trace: `eval/model_trace_run02.jsonl` |
| Run 03 / pre-demo | 20/20 = 100.0% | Tái lập đạt quality bar; không có failure analysis | [eval/run_03_results.json](eval/run_03_results.json); trace: `eval/model_trace_run03.jsonl` |

**Failure analysis:** Run 01 có hai lỗi artifact: G10 `reject` đúng nhưng evaluator cũ yêu cầu topic label hẹp hơn; G17 chưa giữ cue “model randomness”. Run 02 sửa evaluator để chấm scope theo `relevant=false` + `action=reject` và bổ sung rule nondeterminism; Run 03 xác nhận lại cùng prompt/model với 20/20 case đạt. Quality bar không thay đổi.

## §8. Phân công & kế hoạch

| Đầu việc | Người phụ trách | Deliverable/tiêu chí |
|---|---|---|
| Spec, product framing, tích hợp prototype | Trần Xuân Đức | `spec.md`, dashboard, pipeline chạy được |
| Evidence mining, chatlog và impact | Nguyễn Thành Nam | Số liệu mining, quote có mã nguồn, candidate data |
| Prompt, taxonomy, golden set và eval | Nguyễn Lê Phước Tiến | prompt, classifier logic, `eval/golden_set_20.json`, phân tích fail |
| Demo và validation | Nguyễn Thành Nam + Nguyễn Lê Phước Tiến | Kịch bản demo, log task, feedback người dùng |

- **Willing users:** Thu, Kiên, Bình đã đồng ý thử; tối thiểu hai người sẽ tham gia vòng validation.
- **Kế hoạch validation:** mỗi người dùng 10 phút; task là “tìm topic lớp cần ôn lại và mở evidence”; ghi thời gian hoàn thành, topic họ chọn, lúc họ nghi ngờ kết quả và quote feedback. Tiêu chí phụ: người dùng có phân biệt được `learning gap` với logistics/out-of-scope và có biết quyết định cuối thuộc về mình hay không. `validation/dogfood_cp5.md` đã ghi một lượt mô phỏng nội bộ; R6 với người ngoài nhóm vẫn chưa được claim hoàn tất vì chưa có phiên trực tiếp được ghi nhận.
- **Multi-prototype:** A tự nhóm topic tự động nhanh hơn nhưng rủi ro chốt sai; B đề xuất topic nhánh và yêu cầu xác nhận an toàn hơn nhưng tốn thao tác. Chọn B/conditional về mặt sản phẩm vì cost-of-error của ôn sai cao hơn chi phí xác nhận 1–2 topic.

## §9. Changelog

| Thời điểm | Đổi gì | Vì sao / case liên quan |
|---|---|---|
| 17/9 — CP1 | Chốt user là giảng viên/TA và lát cắt class gap map | Canvas CP1, pain từ chatlog và willing users Thu/Bình/Kiên |
| 18/9 — CP2 | Chốt pipeline candidate → signal → scope → topic → aggregate → dashboard | Cần một workflow từ chatlog đến evidence có thể demo |
| 18/9 — CP3 | Thêm golden set 20 case và breakdown 4 lớp | Run 01 cho thấy lỗi ở source-truth và scope label; G10, G17 |
| 18/9 — trước CP4 | Đổi mô tả từ mock sang working prototype; khai báo correction UI chưa xong | README_RUN và code hiện có LLM/Ollama, classifier, aggregator, dashboard; chưa có control sửa/gộp |
| 18/9 — Run 02 | Bổ sung rule nhận diện model stochasticity/nondeterminism và sửa evaluator scope theo hành vi | G17 cần giữ cue `model randomness`; G10 đã reject đúng nhưng evaluator cũ lệch nhãn |
| 18/9 — Run 03 | Chạy xác nhận độc lập trên cùng golden set, model và temperature | Tái lập Run 02: 20/20 = 100.0%, đủ 4 lớp |
| 18/9 — CP4 | Khóa quality bar theo action, evidence và scope; giữ nguyên ngưỡng sau Run 02/03 | Ngăn hạ chuẩn sau khi thấy 90%; bảo vệ các case reject/clarify và traceability |
| 18/9 — CP5 dogfood | Mô phỏng ba persona Kiên/Thu/Bình; thêm control `Instructor decision` dưới evidence | Friction lặp lại: thấy evidence nhưng không biết bước quyết định tiếp theo; log tại `validation/dogfood_cp5.md` |
| 18/9 — CP5 | Giữ nguyên ranking, evidence, scope và quality bar; đưa R6 thật, persistence, correction UI và mobile vào backlog | Dogfood không thay thế phiên người dùng thật; các phần lõi đã có số đo Run 02/03 |

### CP5 tổng hợp validation

- **Chủ đề lặp nhiều nhất:** người dùng tìm được evidence nhưng thiếu điểm kết thúc để ghi quyết định của giảng viên.
- **Thay đổi đã làm:** thêm `Instructor decision` với bốn lựa chọn ngay dưới evidence; AI không tự chọn.
- **Phần giữ nguyên có lý do:** ranking, evidence, scope note và quality bar giữ nguyên vì Run 02/03 đạt 20/20 và dogfood không cho thấy lỗi ở các phần này.
- **Đưa vào backlog:** hai phiên R6 thật với người ngoài nhóm, lưu quote có xin phép, lưu quyết định lâu dài, correction UI và kiểm thử mobile.
