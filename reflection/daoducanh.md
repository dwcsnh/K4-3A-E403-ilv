# Reflection — Đào Đức Anh (2A202602567)

## Vai trò và phạm vi chịu trách nhiệm

Tôi là **Team Lead** và là người chịu trách nhiệm chính về mặt kỹ thuật cho phần lõi AI của dự án (Classroom Agent). Vai trò của tôi bao gồm thiết kế luồng tương tác (work flow), trực tiếp lập trình (AI pipeline, bot gateway), tinh chỉnh câu lệnh (prompt engineering), viết tài liệu đặc tả hệ thống (AI spec) và chuẩn bị kịch bản demo.

Trong vai trò Lead, tôi phối hợp với các thành viên để thống nhất giữa thiết kế giao diện (Frontend) và logic xử lý của Backend, đảm bảo toàn bộ hệ thống hoạt động xuyên suốt từ lúc người dùng nhập tin nhắn đến khi các Agent trả về phản hồi.

## Phần tôi trực tiếp thực hiện

### 1. Xây dựng Work Flow (Luồng tương tác đa tác tử)

Tôi thiết kế và hiện thực hóa kiến trúc lớp học ảo nhiều vai trò (Multi-Agent). Thay vì dùng một chatbot đa năng, tôi chia hệ thống thành các Agent chuyên biệt:
- **TA Agent (Giảng viên):** Giải đáp thắc mắc chuyên sâu, bám sát tài liệu.
- **Student Agent (Bạn học):** Đặt câu hỏi ôn tập (Active Recall) để kích thích người học tư duy.
- **Generator Agent (Nexus Bot):** Sinh học liệu (Quiz, Flashcard, Mindmap) tự động từ bài giảng.

Tôi xây dựng cơ chế phân luồng trong `classroom_runtime.py` để hệ thống tự biết khi nào gọi Agent nào, và xử lý mượt mà các tình huống người dùng im lặng (timeout) để Agent tự động tiếp lời.

### 2. Lập trình AI Pipeline & Bot Gateway

Tôi viết `classroom_gateway.py` sử dụng WebSockets để giao tiếp real-time với Frontend. Gateway này không chỉ nhận/gửi tin nhắn mà còn quản lý bộ đếm thời gian (timers) cho luồng hội thoại. 

Trong phần AI Pipeline, tôi xây dựng lớp `LiveClassroomSession` để:
- Trích xuất nội dung bài giảng tương ứng với slide hiện tại (`current_slide`).
- Gọi LLM API thông qua các Provider (OpenAI, OpenRouter).
- Parse kết quả JSON trả về từ Agent và đẩy (push) dạng `snapshot` về cho client.
- Tích hợp MongoDB (thông qua `LessonStore`) để lưu trữ lịch sử hội thoại và các học liệu được sinh ra.

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
