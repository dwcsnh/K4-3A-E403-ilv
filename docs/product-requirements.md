# PRD — Multi-Agent Classroom (Lớp học đa tác tử)

| Thuộc tính      | Giá trị                                                              |
| --------------- | -------------------------------------------------------------------- |
| Trạng thái      | Mô tả **hiện trạng** prototype (Working), không bao gồm kế hoạch mới |
| Track           | D — Học tập thích ứng & tương tác                                    |
| Nhóm            | K4 · 3A · E403                                                       |
| Cập nhật        | 29/10/2026                                                           |
| Tài liệu liên quan | [`spec.md`](../spec.md) · [`architecture.md`](architecture.md) · [`eval/`](../eval/) |

---

## 1. Executive Summary

**Problem Statement.** Học viên tự ôn slide bài giảng ngoài giờ học không biết mình đã hiểu bài đến đâu: đọc tài liệu là hoạt động một chiều, không ai hỏi ngược lại, và nhiều người ngại hỏi giảng viên. Khảo sát n = 27: **77,8%** "không biết mình thực sự hiểu bài đến đâu", **66,7%** ngại hỏi lại.

**Proposed Solution.** Một lớp học mô phỏng chạy trên web, bám theo từng trang slide. Ba AI agent cùng tham gia: trợ giảng (TA) giải thích có trích nguồn, bạn học chủ động đặt câu hỏi Active Recall, và bot sinh quiz/flashcard/mindmap. Một Orchestrator chặn nội dung ngoài lề và điều phối agent.

**Success Criteria** (quality bar chốt tại CP4, xem `spec.md` §7):

| KPI | Ngưỡng đạt | Kết quả hiện tại |
| --- | --- | --- |
| Tỷ lệ PASS trên golden set 20 case | ≥ 80% (16/20) | **16/20** (lượt 2, 18/09/2026) |
| Critical violation (dạy sai kiến thức, làm theo prompt injection, lộ system prompt) | 0 | Lượt 2 không ghi nhận critical violation |
| Câu trả lời giải thích kiến thức có citation tới slide tồn tại trong deck | 100% case groundedness | Lượt 1 có 2 case trích sai nguồn; lượt 2 không còn lỗi này |
| Mỗi lượt chỉ một agent "nói chính", không chào/trả lời trùng | 0 case nói chồng | Lượt 1: 3 case; lượt 2: 0 case |

---

## 2. User Experience & Functionality

### 2.1 User Personas

| Persona | Mô tả | Nhu cầu chính |
| --- | --- | --- |
| **Học viên tự ôn (chính)** | Học viên AI20K khoá K4, ôn slide Day 1/Day 2 một mình sau buổi học để chuẩn bị Lab. Có thể không có nền IT. | Kiểm tra mình hiểu đúng chưa ngay tại slide đang xem, được hỏi ngược lại, có học liệu ôn tập. |
| **Giảng viên / người vận hành (phụ)** | Người cấu hình bài học, persona và prompt. | Kiểm soát agent chỉ dạy theo nội dung slide, xem được log hội thoại. |

### 2.2 Các agent trong lớp học

| Agent | Persona hiển thị | Vai trò |
| --- | --- | --- |
| `orchestrator` | (ẩn, không nói với người học trừ khi từ chối) | Guardrail, tách đa ý định, chọn agent và kênh, duyệt câu hỏi của bạn học |
| `ta_agent` | TS. Minh — trợ giảng | Giải thích kiến thức theo Socratic, chấm/nhận xét câu trả lời, trả lời thay khi người học không phản hồi |
| `student_agent` | Bảo Nam — bạn học | Đặt câu hỏi Active Recall về slide hiện tại, nhận xét câu trả lời của người học |
| `generator_agent` | Nexus Bot | Sinh quiz trắc nghiệm, flashcard, mindmap từ nội dung đã học |

### 2.3 Màn hình

| Route | Chức năng |
| --- | --- |
| `/` (Lesson view) | Xem slide PDF theo bài (Day 1, Day 2), điều hướng trang, sidebar bài học, checkpoint |
| `/classroom` | Slide + khung chat với các agent, chọn người nhận (cả lớp / TA / bạn học / bot), sidebar học liệu, lịch sử hội thoại |
| `/materials` | Thư viện quiz/flashcard/mindmap đã sinh, lọc theo loại |

### 2.4 User Stories & Acceptance Criteria

**US-1 · Hỏi TA về slide đang xem.**
As a học viên, I want to hỏi TA về nội dung slide đang mở so that tôi hiểu đúng bản chất mà không phải copy ngữ cảnh sang chatbot khác.

- Câu hỏi gửi kèm số slide hiện tại; TA chỉ dùng nội dung slide hiện tại và các slide đã học (`covered_content`).
- Phản hồi có trường `citations` chỉ chứa số slide hoặc timestamp có thật trong deck.
- Khi nội dung không có trong bài, TA nói rõ "không tìm thấy trong nguồn" và không gắn citation giả.
- Khi người học chưa thử mà xin đáp án, TA chỉ đưa một gợi ý tối thiểu.

**US-2 · Được bạn học hỏi ngược lại (Active Recall).**
As a học viên, I want to bạn học đặt câu hỏi về slide tôi vừa xem so that tôi biết mình nhớ và hiểu đến đâu.

- Ở chế độ `all` hoặc `student`, sau khi người học dừng ở một slide **5 giây** (`CLASSROOM_STUDENT_DELAY_SECONDS`), `student_agent` đặt một câu hỏi.
- Orchestrator duyệt câu hỏi trước khi hiển thị; nếu không đạt, câu hỏi được thay bằng phiên bản cải tiến (ghi log `orchestrator_student_critique`).
- Câu hỏi trở thành `pendingPrompt`. Câu trả lời tiếp theo của người học được chấm theo câu hỏi đó.
- Nếu người học không trả lời trong **15 giây** (`CLASSROOM_ANSWER_TIMEOUT_SECONDS`), Orchestrator lập kế hoạch timeout và TA trả lời mẫu.
- Chuyển slide hoặc đổi chế độ sẽ huỷ câu hỏi đang chờ và mọi timer.

**US-3 · Sinh học liệu ôn tập.**
As a học viên, I want to yêu cầu tạo quiz/flashcard/mindmap so that tôi có tài liệu tự kiểm tra sau buổi học.

- Một yêu cầu có thể sinh nhiều loại học liệu cùng lúc (ví dụ "tạo quiz và mindmap").
- Học liệu được lưu vào MongoDB (`generated_materials`) kèm `citations`, `slide_number`, `covered_until`.
- Học liệu xuất hiện ở sidebar classroom và trang `/materials`; quiz không hiện đáp án trước khi người học chọn.

**US-4 · Yêu cầu nhiều việc trong một tin nhắn.**
As a học viên, I want to hỏi giải thích và xin quiz trong cùng một câu so that tôi không phải gửi nhiều lần.

- Orchestrator tách thành nhiều `agent_tasks`, mỗi task có agent và kênh riêng.
- UI nhận một snapshot duy nhất chứa các event theo thứ tự task.

**US-5 · Chat riêng hoặc chat chung.**
As a học viên, I want to chọn nói với cả lớp, riêng TA, riêng bạn học hoặc riêng bot so that tôi kiểm soát được ai trả lời.

- 4 kênh hội thoại: `shared`, `private_ta`, `private_student`, `material`; mỗi kênh có lịch sử riêng.
- Người học có thể reply vào một tin cụ thể (`reply_to_id`); agent trả lời gắn với tin đó.

**US-6 · Bị chặn khi hỏi ngoài lề hoặc tấn công prompt.**
As a học viên, I want to được nhắc quay về bài khi hỏi ngoài phạm vi so that phiên học không lạc đề.

- Orchestrator trả `guardrail_status: "rejected"` cho prompt injection/jailbreak, nội dung độc hại, hoặc chủ đề không liên quan (cờ bạc, xổ số, spam).
- Khi bị từ chối: không gọi agent con, trả về một tin từ chối lịch sự bằng tiếng Việt, ghi turn với intent `guardrail_rejected`.
- Agent không giả vờ có quyền truy cập dữ liệu cá nhân (điểm danh, điểm số).

**US-7 · Xem lại lịch sử.**
As a học viên, I want to mở lại các cuộc hội thoại cũ của bài học so that tôi ôn lại những gì đã hỏi.

- Lịch sử được lưu theo `session_id:scope` và liệt kê qua `GET /api/artifacts/{id}/conversations` (tối đa 50).
- Khi bootstrap lại phiên, history và học liệu đã lưu được nạp lại.

### 2.5 Non-Goals

1. Không dùng nguồn ngoài (web search, kiến thức ngoài bài). Agent chỉ trả lời từ slide đã ingest.
2. Không giải bài hộ hoặc đưa đáp án trực tiếp khi người học chưa thử.
3. Không chấm điểm chính thức hay thay giảng viên đánh giá năng lực.
4. Không xử lý yêu cầu hành chính (điểm danh, điểm số, tài khoản).
5. Không có đăng nhập, phân quyền hay quản lý người dùng.
6. Không cho người học tự upload bài giảng mới. Danh mục bài học cố định trong code (`day1`, `day2`).
7. Không có màn hình cho giảng viên duyệt/sửa học liệu do AI sinh.

---

## 3. AI System Requirements

### 3.1 Tool & API Requirements

| Thành phần | Yêu cầu |
| --- | --- |
| LLM provider | Một trong: OpenAI (mặc định), OpenRouter, Anthropic, Gemini. Chọn qua `CLASSROOM_PROVIDER`. |
| Model | Orchestrator, bạn học và generator dùng model mặc định của provider (OpenAI: `gpt-4o-mini`). TA dùng `gpt-4o` khi provider là OpenAI/OpenRouter, ghi đè bằng `CLASSROOM_TA_MODEL`. Orchestrator ghi đè bằng `CLASSROOM_ORCHESTRATOR_MODEL`. |
| Định dạng output | Mọi agent trả JSON có cấu trúc (`intent`, `reply`, `citations`, `active_recall`, …). Orchestrator có heuristic fallback khi JSON lỗi. |
| Function calling | `generator_agent` gọi tool `generate_learning_material` (khai báo trong `artifacts/tools/generate_learning_material.yaml`) để dựng quiz, flashcard, mindmap. |
| Ingest slide | PDF → Markdown bằng `pdftotext`/`pdfinfo` (poppler); fallback sang `docling` (tuỳ chọn). Kết quả cache ở `data/ingested/*.md`. |
| System prompt | Mỗi agent có file riêng trong `codebase/agents/artifacts/system_prompts/`. |

### 3.2 Evaluation Strategy

- **Golden set:** 20 case trong `eval/golden-set.json` (9 thường, 8 khó, 3 hiếm; 18/20 phát triển từ chatlog K4 thật). Mỗi lớp khó (nguồn sự thật, mơ hồ, ngoài phạm vi, đặc thù đa agent) có ít nhất 2 case.
- **Ba chiều chấm:**
  1. *Groundedness*: câu trả lời nằm trong nội dung bài và citation đúng; thiếu nguồn thì nói rõ.
  2. *Role & pedagogy*: route đúng agent và thứ tự, giữ vai, không nói chồng, TA gợi mở hoặc dừng đúng lúc.
  3. *Task contract*: hoàn thành đủ `must_do`, không vi phạm `must_not`.
- **Quy tắc PASS:** case PASS khi đạt cả 3 chiều. Bộ đạt khi ≥ 16/20 và 0 critical violation.
- **Kết quả đã chạy:**

| Lượt | Ngày | Model | Kết quả | Lỗi chính |
| --- | --- | --- | --- | --- |
| 1 | 17/09/2026 | gpt-4o-mini | 14/20 | 3 nói chồng, 2 trích sai nguồn, 1 thiếu `must_do` |
| 2 | 18/09/2026 | gpt-4o-mini + gpt-4o (TA) | 16/20 | 2 trả lời việc ngoài phạm vi, 1 vi phạm Socratic, 1 thiếu `must_do` |

- **Validation với người dùng ngoài nhóm:** file `validation/user_testing_log.md` hiện **chưa có nội dung**.

---

## 4. Technical Specifications

Chi tiết đầy đủ ở [`architecture.md`](architecture.md). Tóm tắt:

### 4.1 Architecture Overview

```
Browser (Next.js 15 / React 19)
   │  HTTP GET  /api/artifacts…        (metadata bài học, PDF, học liệu, lịch sử)
   │  WebSocket /ws/classroom          (bootstrap · sync_slide · message → snapshot)
   ▼
Classroom Gateway (Python, websockets, cổng 8000)
   └─ LiveClassroomSession (1 phiên / 1 kết nối WS)
        ├─ OrchestratorAgent ──► plan: guardrail + agent_tasks
        ├─ ta_agent · student_agent · learning_material_agent
        │        └─ Provider (OpenAI | OpenRouter | Anthropic | Gemini)
        └─ LessonStore ──► MongoDB 7 (artifacts, conversations, materials)
```

### 4.2 Integration Points

| Điểm tích hợp | Chi tiết |
| --- | --- |
| HTTP API | `GET /health`, `GET /api/artifacts`, `GET /api/artifacts/{id}`, `GET /api/artifacts/{id}/file`, `GET /api/artifacts/{id}/materials?type=`, `GET /api/artifacts/{id}/conversations`, `GET /api/materials/{materialId}` |
| WebSocket | `ws://<host>:8000/ws/classroom`; action `bootstrap`, `sync_slide`, `message`; server trả `kind: snapshot` hoặc `kind: error` |
| Database | MongoDB, DB `multi_agent_classroom`; collection `artifacts`, `ingested_artifacts`, `conversation_histories`, `generated_materials` |
| LLM API | Khoá API đọc từ `codebase/agents/.env` (`OPENAI_API_KEY`, `OPENROUTER_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`) |
| Auth | Không có. Mọi endpoint mở, CORS `*`. |

### 4.3 Security & Privacy

- Không thu thập danh tính người học; phiên định danh bằng UUID ngẫu nhiên (`ws-<uuid>`).
- API key chỉ nằm trong `.env` (đã gitignore), không gửi xuống frontend.
- Data pack khoá học (`data/`, `codebase/vlearn-pack/`) bị gitignore theo quy định bảo mật hackathon; repo chỉ chứa trích dẫn ngắn.
- Guardrail ở Orchestrator chặn prompt injection trước khi agent con chạy. Prompt có phân tách rõ "Trusted classroom state" với "User input".
- Log sự kiện ghi ra `codebase/agents/data/logs/classroom_events.jsonl` (gitignore), có chứa nội dung chat.
- Hạn chế: không có auth, không rate limit, CORS mở. Chỉ phù hợp chạy local/demo.

---

## 5. Risks & Roadmap

### 5.1 Trạng thái phát hành

Sản phẩm đang ở mức **MVP — prototype Working** cho hackathon: chạy thật với LLM, 2 bài học (Day 1, Day 2), 3 agent và Orchestrator, lưu trữ MongoDB, chạy bằng Docker Compose. Theo phạm vi đã chốt, tài liệu này không đề ra các phase tiếp theo.

### 5.2 Giới hạn hiện tại

- Danh mục bài học hard-code ở `LESSON_CATALOG` (backend) và `SLIDE_FILES` (frontend).
- Hồ sơ persona agent và checkpoint bài học trên frontend lấy từ `lib/mock-data.ts`.
- Ingest chỉ lấy text; hình ảnh và biểu đồ trong slide không được hiểu (rủi ro R1 trong `spec.md`).
- Các file từ lab trước vẫn còn trong code: `artifacts/tools/tools.yaml`, tool `search_device_info`, `clarify` (helpdesk Day 4). Classroom không dùng chúng.
- `classroom_api.py` (cầu nối stdin/stdout) và route `POST /api/classroom` (trả 410) là đường cũ, đã được WebSocket thay thế.

### 5.3 Technical Risks

| Rủi ro | Tác động | Giảm thiểu hiện có |
| --- | --- | --- |
| **Độ trễ:** một tin nhắn = 1 lời gọi Orchestrator + N lời gọi agent, chạy tuần tự, đồng bộ trong event loop | Phản hồi chậm; trong lúc gọi LLM, gateway không xử lý được message khác | Chưa có. Độ trễ chưa được đo. |
| **Chi phí:** mỗi lượt gửi kèm `covered_content` (toàn bộ slide đã học) | Token tăng theo vị trí slide | Giới hạn history 10 turn gần nhất cho Orchestrator |
| **Hallucination / sai citation** | Học viên học sai kiến thức (critical) | Prompt bắt buộc citation, kiểm tra trên golden set |
| **JSON lỗi từ LLM** | Không route được | `_heuristic_fallback` trong Orchestrator |
| **Phụ thuộc provider** | Hết quota hoặc lỗi API làm lớp học dừng | Đổi provider bằng biến môi trường |
| **Phụ thuộc chưa khai báo:** `websockets` không có trong `requirements.txt`, chỉ có mặt nhờ cài gián tiếp | Build có thể vỡ khi dependency gián tiếp đổi | Chưa có |
| **Bảo mật:** không auth, CORS `*` | Không deploy công khai được | Chỉ chạy local |
