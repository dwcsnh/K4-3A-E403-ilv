# Reflection — Đào Đức Anh (2A202602567)

## Vai trò và phạm vi chịu trách nhiệm

Tôi là **Team Lead** và là người chịu trách nhiệm chính về mặt kỹ thuật cho phần lõi AI của dự án (Classroom Agent). Vai trò của tôi bao gồm thiết kế luồng tương tác (work flow), trực tiếp lập trình (AI pipeline, bot gateway), thực hiện kiểm thử dựa trên bộ dữ liệu do các thành viên chuẩn bị, sau đó thực hiện vá các lỗi trong quá trình kiểm thử., tinh chỉnh câu lệnh (prompt engineering), viết tài liệu đặc tả hệ thống (AI spec) và chuẩn bị kịch bản demo.

Trong vai trò Lead, tôi đã phối hợp với các thành viên để thống nhất giữa thiết kế giao diện và hành vi của agent trong hệ thống, và cùng các thành viên chuẩn bị luồng demo chính của nhóm.

## Phần tôi trực tiếp thực hiện

### 1. Xây dựng Work Flow (Luồng tương tác đa tác tử)

Tôi thiết kế và hiện thực hóa kiến trúc lớp học ảo nhiều vai trò (Multi-Agent). Thay vì dùng một chatbot đa năng, tôi chia hệ thống thành các Agent chuyên biệt:

- **TA Agent (Giảng viên):** Giải đáp thắc mắc chuyên sâu, bám sát tài liệu.
- **Student Agent (Bạn học):** Đặt câu hỏi ôn tập (Active Recall) để kích thích người học tư duy.
- **Generator Agent (Nexus Bot):** Sinh học liệu (Quiz, Flashcard, Mindmap) tự động từ bài giảng.

Tôi xây dựng cơ chế phân luồng trong `classroom_runtime.py` để hệ thống tự biết khi nào gọi Agent nào, và xử lý mượt mà các tình huống người dùng im lặng (timeout) để Agent tự động tiếp lời.

### 2. Lập trình AI Pipeline & Bot Gateway

Tôi trực tiếp thiết kế và lập trình toàn bộ tầng Gateway (`classroom_gateway.py`) và lõi AI Pipeline (`classroom_runtime.py`, `agent.py`, `orchestrator.py`, `lesson_store.py`). Đây là "trục xương sống" kết nối giữa giao diện người dùng và các tác tử AI, đảm bảo việc xử lý luồng diễn ra thời gian thực, đồng bộ và ổn định.

#### a. Kiến trúc Bot Gateway hai giao thức (WebSocket & REST API)

Trong `classroom_gateway.py`, tôi xây dựng một Gateway đa năng phục vụ cả luồng thời gian thực lẫn truy vấn tĩnh:

- **WebSocket Gateway thời gian thực (`/ws/classroom`):** Sử dụng thư viện `websockets.asyncio.server` để thiết lập kênh giao tiếp hai chiều (full-duplex). Gateway xử lý 3 hành động chính từ client: `bootstrap` (khởi tạo phiên học), `sync_slide` (đồng bộ chuyển slide) và `message` (nhận tin nhắn người học). Mỗi phản hồi từ hệ thống được đóng gói thành một `snapshot` toàn diện (gồm trạng thái slide, gợi ý chờ phản hồi `pendingPrompt`, kho học liệu `artifacts` và mảng `events`), giúp Frontend luôn đồng bộ trạng thái một cách nhất quán thay vì phải tự ghép nối các tin nhắn rời rạc.
- **REST API & Tích hợp HTTP:** Xử lý trực tiếp các yêu cầu HTTP với đầy đủ CORS headers (`_cors_headers`), cung cấp các endpoint: `/health` (kiểm tra trạng thái sẵn sàng của dịch vụ và kết nối MongoDB), `/api/artifacts` (danh sách bài giảng), `/api/artifacts/{id}/materials` (tra cứu học liệu đã sinh), `/api/artifacts/{id}/conversations` (lịch sử hội thoại) và stream file PDF slide gốc (`/api/artifacts/{id}/file`).
- **Cơ chế Async Timers & Concurrency Guard:** Để lớp học mô phỏng vận hành tự nhiên, tôi lập trình hai bộ đếm thời gian bất đồng bộ:
  - _Student Delay Timer_ (`STUDENT_DELAY_SECONDS = 5s`): Tự động kích hoạt Student Agent đặt câu hỏi gợi mở (Active Recall) khi người học dừng lại ở một slide mới.
  - _Answer Timeout Timer_ (`ANSWER_TIMEOUT_SECONDS = 15s`): Đếm ngược thời gian chờ người học phản hồi; nếu học viên im lặng, kích hoạt luồng cứu hộ để TA Agent can thiệp giải thích.
  - _Token-based Concurrency Guard:_ Nhằm giải quyết triệt để xung đột race conditions và lỗi "nói chồng chéo" khi người học bấm chuyển slide liên tục hoặc nhắn tin cắt ngang, tôi thiết kế cơ chế `state_token` (`bump_state_token()`). Bất kỳ sự kiện mới nào từ người dùng đều lập tức hủy các tác vụ hẹn giờ cũ (`cancel_scheduled_turns()`) và vô hiệu hóa các callback quá hạn, đảm bảo bot chỉ phản hồi đúng ngữ cảnh hiện tại.

#### b. Lõi AI Pipeline & Điều phối thông minh (`LiveClassroomSession`)

Trong `classroom_runtime.py`, tôi hiện thực hóa lớp quản lý phiên học tập `LiveClassroomSession`:

- **Quản lý ngữ cảnh và phân tầng tài liệu (`LectureDeck`):** Dựa trên slide hiện tại (`current_slide`), hệ thống trích xuất nội dung từ tệp markdown đã ingest và phân tách thành ba phân vùng tri thức: `current_segment` (slide hiện tại), `covered_content` (kiến thức lũy kế từ slide 1 đến slide hiện tại để ngăn bot nói trước kiến thức chưa học) và `full_lecture_content` (toàn bộ bài giảng phục vụ việc tạo học liệu tổng hợp).
- **Phân tách và quản lý 4 kênh hội thoại độc lập (Conversation Scopes):** Hệ thống duy trì 4 ngữ cảnh tách biệt gồm `shared` (lớp học chung), `private_ta` (chat riêng với giảng viên), `private_student` (chat riêng với bạn học) và `material` (kênh sinh học liệu). Mỗi kênh lưu trữ 10 lượt hội thoại gần nhất kèm định danh tin nhắn (`[msg_id] Speaker: message`), hỗ trợ luồng trả lời có trích dẫn chuỗi (`reply_to_id`).
- **Tích hợp bộ điều phối trung tâm (`OrchestratorAgent`):** Thay vì sử dụng if/else định tuyến đơn giản, tôi xây dựng `OrchestratorAgent` trong `orchestrator.py` để:
  - Kiểm duyệt an toàn và ranh giới nghiệp vụ (`guardrail_status`): Từ chối ngay các yêu cầu lạc đề, độc hại hoặc prompt injection trước khi chuyển tới agent chuyên trách.
  - Bóc tách đa ý định (Multi-intent Decomposition): Phân tích câu lệnh phức tạp của người học thành danh sách tác vụ cụ thể (`AgentTask`), phân công đúng vai (`ta_agent`, `student_agent`, `generator_agent`) và đúng kênh đích.
  - Kiểm duyệt sư phạm câu hỏi học viên (`evaluate_student_question`): Đối chiếu câu hỏi do Student Agent đề xuất với các khái niệm cốt lõi (`key_concepts`) của slide; nếu câu hỏi hời hợt hoặc lệch trọng tâm, hệ thống sẽ tự động cải tiến (`improved_question`) trước khi gửi tới lớp.
  - Bộ định tuyến dự phòng (`_heuristic_fallback`): Tự động kích hoạt khi phản hồi của LLM không khớp định dạng JSON, đảm bảo hệ thống không bao giờ bị gián đoạn.
- **Phân tầng mô hình (Model Tiering):** Tách bạch provider thông qua `make_provider` (hỗ trợ OpenAI, OpenRouter, Anthropic, Gemini). Cho phép gán các mô hình suy luận mạnh (`gpt-4o`) cho TA Agent thông qua `_resolve_ta_model`, trong khi Orchestrator và Student Agent có thể sử dụng các mô hình nhẹ hơn (`gpt-4o-mini`) nhằm tối ưu độ trễ và chi phí.

#### c. Vòng lặp ReAct Tool-Calling đa bước (Multi-turn Agent Loop)

Trong `agent.py` và `classroom_cli.py`, tôi xây dựng cơ chế thực thi công cụ nâng cao cho Generator Agent:

- **Vòng lặp ReAct (`Agent.run_loop`):** Khác với các chatbot gọi tool một lần rồi dừng, tôi lập trình vòng lặp phản hồi suy luận (lặp tối đa 6 vòng) theo quy trình: `Thought` -> `Action` (gọi tool) -> `Observation` (nhận kết quả công cụ) -> tiếp tục suy nghĩ và gọi công cụ tiếp theo cho đến khi hoàn thành đầy đủ yêu cầu. Nhờ đó, người học có thể yêu cầu tạo cùng lúc cả Quiz, Flashcard và Mindmap chỉ trong một câu lệnh duy nhất.
- **Bộ phân tích đa định dạng (Multi-format Parser):** Xử lý linh hoạt dữ liệu trả về từ các tool YAML (`generate_quiz`, `generate_flashcard`, `generate_mindmap`). Tôi lập trình bộ parse JSON có khả năng tự sửa lỗi Markdown fence và bộ bóc tách cây phân cấp XML (`ElementTree`) cho Mindmap, chuẩn hóa trích dẫn nguồn (`citations`) gắn liền với từng nhánh kiến thức hoặc câu hỏi trắc nghiệm.

#### d. Lưu trữ bền vững (LessonStore) & Giám sát sự kiện (ClassroomLogger)

- **Cơ sở dữ liệu MongoDB (`lesson_store.py`):** Thiết kế schema cho 4 collection chính: `artifacts` (thông tin bài giảng), `ingested_artifacts` (bản bóc tách nội dung slide), `conversation_histories` (lịch sử hội thoại phân theo session và kênh) và `generated_materials` (kho lưu trữ các bộ câu hỏi, thẻ ghi nhớ và sơ đồ tư duy đã tạo). Các chỉ mục (indexes) được tạo tự động nhằm tối ưu tốc độ truy vấn.
- **Ghi log sự kiện có khóa an toàn (`classroom_logging.py`):** Xây dựng `ClassroomLogger` ghi nhận tuần tự từng bước xử lý của hệ thống ra file `classroom_events.jsonl` (sử dụng `threading.Lock` chống xung đột ghi đa luồng). Ghi vết đầy đủ từ `session_started`, `slide_changed`, `learner_message`, `learner_timeout` cho đến `orchestrator_student_critique`, cung cấp bằng chứng rõ ràng phục vụ quá trình chấm điểm và đánh giá trên bộ Golden Set.

### 3. Prompt Engineering

Đây là phần tôi dành nhiều thời gian để tối ưu. Tôi viết và liên tục tinh chỉnh các System Prompt cho từng Agent:

- Đảm bảo **TA Agent** luôn áp dụng phương pháp Socratic, không mớm câu trả lời trực tiếp mà gợi ý để người học tự tìm ra.
- Thiết lập quy tắc "Response Contract" yêu cầu mọi Agent phải trả lời dưới dạng JSON (với các trường `intent`, `action`, `reply`, `citations`).
- Xây dựng các ranh giới an toàn (Guardrails) ngay trong prompt để ngăn chặn Prompt Injection hoặc Agent bịa đặt kiến thức ngoài tài liệu (Hallucination).

### 4. Viết tài liệu AI Spec & Chuẩn bị Demo

Tôi chịu trách nhiệm chính trong việc hoàn thiện file `spec.md`, định nghĩa rõ:

- Mục tiêu dự án (Goals & Non-goals).
- Phân tích người dùng và Use Cases.
- Kiến trúc hệ thống và Thiết kế kỹ thuật.
- Kế hoạch đánh giá (Evaluation Plan) với Golden Set.

Bên cạnh đó, tôi chuẩn bị dữ liệu mock, kịch bản demo end-to-end đảm bảo thể hiện rõ nhất sức mạnh của mô hình học tập chủ động thông qua Agent.

## Các quyết định kỹ thuật quan trọng của tôi

- **Sử dụng WebSockets thay vì REST API:** Để hỗ trợ luồng chat liên tục và cơ chế "Agent chủ động bắt chuyện" (khi hết thời gian timeout), WebSocket là lựa chọn bắt buộc thay vì polling HTTP.
- **Structured Output (JSON):** Bắt buộc LLM trả về JSON thay vì text thô. Điều này giúp hệ thống tách biệt phần giải thích (`reply`), nguồn trích dẫn (`citations`) và phân loại ý định (`intent`), từ đó Frontend dễ dàng render giao diện đẹp mắt (ví dụ: ghim citation, hiện popup báo sinh tài liệu).
- **Phân tách State và Logic:** Quản lý trạng thái (State) ở Gateway (đếm giờ, đợi tin nhắn) và giao phần quyết định sư phạm (Pedagogy) cho Orchestrator/Runtime và LLM xử lý.

## AI hỗ trợ tôi như thế nào

Tôi sử dụng AI như một trợ lý đắc lực trong quá trình phát triển (AI-assisted coding):

- **Tạo khung code (Skeleton):** Dùng AI để dựng nhanh các boilerplate code cho FastAPI, WebSockets.
- **Review và Refactor Code:** AI giúp tôi phát hiện các lỗi bất đồng bộ (async/await), tối ưu hóa luồng xử lý và gỡ rối (debug) các lỗi xung đột port khi cấu hình Docker.
- **Brainstorming:** Tôi dùng AI để phản biện các thiết kế kiến trúc, ví dụ như cách chuyển đổi từ if/else routing sang mô hình Orchestrator Agent.

Tuy nhiên, các quyết định về luồng dữ liệu, schema, và quy tắc nghiệp vụ cốt lõi đều do tôi làm chủ. AI sinh ra code, tôi review, kiểm thử và tích hợp.

## Bài học từ case fail của chính nhóm

Trong quá trình đánh giá (Eval), hệ thống từng gặp lỗi: **"Các Agent nói chồng lên nhau"** (như đã ghi nhận trong `spec.md`). Do ban đầu tôi không khóa luồng xử lý chặt chẽ, Student Agent hỏi xong, trong khi đợi người dùng trả lời thì TA Agent lại "nhảy vào" giải thích hộ luôn.

Từ failure này, tôi học được rằng trong môi trường Multi-Agent:

1. **Quản lý hội thoại phải có trạng thái rõ ràng (State Machine):** Không thể để các Agent tự do kích hoạt. Phải có một "người điều phối" (như khái niệm Orchestrator) quyết định khi nào Agent nào được lên tiếng.
2. **Cơ chế khóa (Lock) hoặc Timeout rõ ràng:** Phải set cứng `timeout` (ví dụ 10 giây). Chỉ khi hết thời gian mà User không phản hồi, TA Agent mới được phép can thiệp.

## Điều tôi đóng góp lớn nhất và điều cần cải thiện

**Đóng góp lớn nhất:** Xây dựng thành công bộ khung (framework) cho một lớp học ảo đa tác tử thực sự hoạt động được. Tôi đã chuyển hóa ý tưởng lý thuyết về Active Recall và phương pháp Socratic thành mã nguồn, kết nối mượt mà giữa Frontend hiện đại và Backend xử lý AI phức tạp.

**Điều cần cải thiện:** Ban đầu hệ thống được thiết kế hơi cứng nhắc (hard-code if/else để định tuyến). Nếu có thêm thời gian, tôi sẽ triển khai triệt để mô hình Orchestrator Agent (Supervisor) để hệ thống tự động bóc tách đa ý định (multi-intent) thông minh hơn, thay vì phụ thuộc quá nhiều vào các từ khóa fix cứng. Ngoài ra, cần thiết lập hệ thống test tự động (Automated Eval) sớm hơn để phát hiện nhanh các lỗi prompt.
