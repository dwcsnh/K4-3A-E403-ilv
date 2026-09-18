# Reflection — Nguyễn Tấn Hoàng (2A202601198)

## Vai trò và phạm vi chịu trách nhiệm

Tôi là **Team Lead / AI Engineer** và là người trực tiếp viết **toàn bộ AI Agent core** của Vlearn Agent. Phần việc của tôi không chỉ là kết nối các module có sẵn, mà bao gồm thiết kế kiến trúc, hiện thực vòng lặp suy luận–tool-calling, xây dựng hệ thống tool, RAG, memory, skills, cá nhân hoá, tích hợp đa kênh, guardrail và xử lý lỗi để agent chạy được end-to-end.

Tôi cũng chịu trách nhiệm chốt phạm vi prototype, phối hợp dữ liệu và bộ test do các thành viên khác chuẩn bị, sửa các lỗi phát hiện trong quá trình thử nghiệm và chuẩn bị luồng demo chính của nhóm.

## Phần tôi trực tiếp thực hiện

### 1. Thiết kế và viết vòng lặp AI Agent core

Tôi viết lớp `TutorAgent` và luồng xử lý chính trong [agent/core.py](../../learning-agent/src/learning_agent/agent/core.py). Khi nhận một tin nhắn, core thực hiện các bước:

1. Xác định danh tính học viên và hợp nhất hồ sơ nếu cùng một người dùng nhiều kênh khác nhau.
2. Nạp system prompt, tính cách trong `SOUL.md`, bộ nhớ dài hạn, hồ sơ học viên và mức độ nắm vững từng chủ đề vào context.
3. Gửi lịch sử hội thoại cùng danh sách tool phù hợp cho LLM.
4. Nhận quyết định gọi tool từ model, thực thi tool thật rồi đưa kết quả trở lại context.
5. Lặp cho tới khi model đủ thông tin để trả lời hoặc đạt giới hạn số vòng.
6. Trả câu trả lời cho gateway, lưu session và tạo trace để có thể kiểm tra model đã gọi tool nào.

Tôi bổ sung giới hạn số vòng tool, chống gọi lặp cùng một tool với cùng tham số, giới hạn số lần ghi concept và một lượt tổng hợp cuối khi hết vòng. Những cơ chế này giúp agent không rơi vào vòng lặp vô hạn, không spam thao tác ghi dữ liệu và vẫn có phản hồi khi một tool gặp lỗi.

Core được viết theo chuẩn OpenAI-compatible và tách model khỏi logic agent. Nhờ đó hệ thống có thể đổi giữa OpenAI, OpenRouter, Gemini qua gateway tương thích hoặc Ollama local bằng cấu hình, thay vì sửa lại luồng nghiệp vụ.

### 2. Xây dựng RAG và nguyên tắc trả lời có căn cứ

Tôi xây dựng nhóm tool học liệu trong [agent/tools.py](../../learning-agent/src/learning_agent/agent/tools.py), gồm `search_lessons`, `list_lessons`, `get_lesson`, `get_concept` và `save_concept`, rồi nối chúng với vault và vector index.

Quy tắc cốt lõi tôi đưa vào agent là: câu hỏi về nội dung học phải tìm trong giáo trình trước; nếu đoạn retrieval chưa đủ chi tiết thì đọc toàn bài liên quan; nếu vẫn không có căn cứ thì nói rõ tài liệu chưa đề cập. Câu trả lời phải chỉ ra bài, slide/phần hoặc timestamp để học viên có thể tự kiểm chứng.

Tôi chọn thiết kế này vì quyết định AI trung tâm của sản phẩm không phải “viết một câu trả lời nghe hợp lý”, mà là **xác định thông tin nào có đủ căn cứ trong kho học liệu để được phép trả lời**. Đây cũng là lý do nhóm chọn mức automation là **augment**: agent tìm, giải thích và trích nguồn, còn học viên giữ quyền kiểm tra kết quả.

### 3. Xây dựng hệ thống skills học tập

Tôi viết cơ chế khám phá và nạp skill trong [agent/skills.py](../../learning-agent/src/learning_agent/agent/skills.py). Agent đọc catalog của 16 skill từ các file `SKILL.md`; khi yêu cầu khớp với quiz, flashcard, Feynman, active recall, mock test, lộ trình ôn tập hoặc các kỹ thuật khác, model phải gọi `load_skill` rồi thực hiện đúng workflow của skill.

Cách thiết kế này tách quy trình sư phạm khỏi core. Có thể thêm hoặc sửa một phương pháp học bằng file skill mà không phải viết lại vòng lặp agent. Ngoài việc gọi skill, tôi còn nối flashcard bền vững và spaced repetition vào core để kết quả học không mất sau một phiên chat.

### 4. Xây dựng memory và cá nhân hoá học viên

Tôi triển khai nhiều tầng bộ nhớ:

- Lịch sử ngắn hạn từ các lượt chat gần nhất.
- Bộ nhớ chung trong `MEMORY.md` cho thông tin bền vững của khoá học.
- Hồ sơ riêng từng học viên qua [agent/memory.py](../../learning-agent/src/learning_agent/agent/memory.py).
- Session log trong SQLite để tìm lại câu hỏi cũ khi học viên nhắc “hôm trước” hoặc “lần trước”.
- Mastery tracking để ghi nhận chủ đề học viên đang yếu hoặc đã nắm vững từ kết quả quiz/vấn đáp.

Tôi cũng xử lý việc hợp nhất định danh giữa Telegram, Discord và dashboard để một học viên không bị tạo ba hồ sơ riêng. Memory sau đó được dùng để ưu tiên ôn chủ đề yếu, điều chỉnh độ khó và xây lộ trình học phù hợp thay vì trả lời mọi người giống nhau.

### 5. Xây dựng tool ecosystem và tích hợp đa kênh

Tôi nối agent core với các nhóm hành động thật: scheduler, Google Calendar/Meet, Discord event và invite, research web/Reddit/GitHub/X, knowledge pack, addon, CLI integration, tạo audio/ảnh và nạp kiến thức từ URL ngoài.

Mỗi request mang theo `origin` để core biết tin nhắn đến từ Telegram, Discord hay web. Vì vậy agent chỉ đưa Discord tools vào context khi đang ở Discord, chỉ lên lịch khi có nơi gửi kết quả trở lại và có thể trả file audio/ảnh qua attachment phù hợp từng gateway.

Với nguồn ngoài, tôi thiết kế flow `fetch → preview → confirm/discard`: agent không tự ý đưa URL vào knowledge base ngay. Việc này giữ quyền kiểm soát cho người dùng và giảm nguy cơ một trang độc hại làm bẩn kho kiến thức.

### 6. Thiết kế bảo mật và khả năng phục hồi

Tôi đưa các guardrail vào cả prompt lẫn code:

- Xem nội dung từ tài liệu, web và tool là **dữ liệu**, không phải chỉ dẫn; nhờ đó hạn chế prompt injection nằm trong file được upload.
- Ẩn và chặn lần hai các tool ghi dữ liệu/tự động hoá đối với người dùng web công khai.
- Không cho agent tự sửa `MEMORY.md` hoặc `SOUL.md` nếu admin chưa bật quyền; backup bản cũ trước khi ghi.
- Audit các hành động nhạy cảm như lên lịch, gọi addon, cài pack và nạp URL ngoài.
- Rate-limit riêng các tool tốn tài nguyên như tạo ảnh và âm thanh.
- Trả lỗi tool về cho model dưới dạng dữ liệu để agent giải thích rõ, thay vì crash toàn bộ phiên chat.

Tôi đặc biệt quy định agent chỉ được nói “đã tạo” khi tool trả về trạng thái thành công. Đây là ranh giới quan trọng giữa một chatbot mô tả hành động và một agent thực sự thực thi hành động.

## Các quyết định kỹ thuật quan trọng của tôi

- **Tool-first cho câu hỏi học thuật:** model phải truy xuất tài liệu trước khi trả lời.
- **Augment thay vì automate hoàn toàn:** kiến thức sai có thể làm học viên hiểu sai và khó sửa, nên luôn cung cấp nguồn để kiểm chứng.
- **Model-agnostic:** logic nghiệp vụ không phụ thuộc một nhà cung cấp LLM, đặc biệt hữu ích khi quota của model ban đầu hết trong hackathon.
- **Skills thay cho hard-code workflow:** quy trình học tập được khai báo thành module độc lập, dễ mở rộng và kiểm tra.
- **Memory có phạm vi rõ:** tách bộ nhớ chung, hồ sơ học viên, lịch sử phiên và mastery để tránh trộn dữ liệu.
- **Kiểm soát ở cả prompt và code:** không đặt toàn bộ niềm tin vào việc model sẽ luôn tuân thủ system prompt.

Những quyết định về lát cắt, automation, HAX/PAIR, bốn lớp rủi ro và quality bar được ghi trong [AI Spec](../spec.md) §4–§7.

## AI hỗ trợ tôi như thế nào

Tôi sử dụng AI như một trợ lý coding trong quá trình phát triển core. AI hỗ trợ tạo nhanh skeleton cho một số module, gợi ý cách khai báo tool schema, rà các nhánh exception, giải thích lỗi tích hợp giữa các provider và đề xuất tình huống biên cần kiểm tra. Khi refactor, AI cũng giúp đối chiếu xem việc thay đổi một tool có ảnh hưởng đến gateway, memory hoặc scheduler hay không.

Tuy nhiên, các phần quan trọng vẫn do tôi tự quyết định và xác minh: kiến trúc vòng lặp, ranh giới quyền hạn của tool, dữ liệu nào được đưa vào context, lúc nào được phép ghi memory, điều kiện báo thành công và hành vi khi không có căn cứ. Tôi đọc lại code được sinh/gợi ý, chạy thử end-to-end và đối chiếu output với tài liệu thật. Tôi không coi code chạy được một lần hoặc câu trả lời nghe hợp lý là bằng chứng hệ thống đúng.

Qua quá trình này, tôi hiểu AI coding hiệu quả nhất khi yêu cầu được chia theo interface và invariant cụ thể. Nếu chỉ yêu cầu “viết một learning agent”, AI có thể sinh nhiều code nhưng không bảo đảm các module thống nhất về quyền hạn, trạng thái và xử lý lỗi.

## Bài học từ case fail của chính nhóm

Failure có ảnh hưởng lớn nhất với tôi là **case 26** trong phiên Discord ngày 30/07: học viên hỏi *“tóm tắt bài học lý thuyết hôm nay”* khi không có bài nào đang được xác định. Agent đã tự tạo ra các ý như “Khái niệm đầu tiên” và “Nguyên lý cơ bản” thay vì hỏi lại hoặc nói không biết hôm nay học bài nào.

Case này làm lộ ra một giả định sai trong thiết kế ban đầu: có RAG không đồng nghĩa model sẽ luôn chủ động dùng RAG. Khi input nghe giống một yêu cầu tóm tắt nhưng thiếu đối tượng, LLM vẫn có xu hướng hoàn thành câu trả lời bằng mẫu ngôn ngữ quen thuộc. Vì output trôi chảy, lỗi này còn nguy hiểm hơn một exception kỹ thuật: học viên có thể tin nội dung bịa mà không biết hệ thống chưa hề tìm thấy bài học.

Từ failure đó, tôi rút ra ba bài học:

1. **Guardrail phải tồn tại trước bước generation.** Với câu hỏi học thuật, agent phải search; nếu không xác định được bài hoặc session thì phải hỏi lại, không được để model tự chọn giữa search và đoán.
2. **Quality bar phải có điều kiện cứng.** Kết quả 8/10 nhìn qua đạt 80%, nhưng chỉ một lần bịa đã khiến hệ thống không đạt cam kết “không bịa trích nguồn dù một lần”.
3. **Phải test hành vi thiếu thông tin, không chỉ test kiến thức.** Happy path chứng minh retrieval hoạt động; case mơ hồ mới chứng minh agent biết giới hạn của mình.

Nếu làm lại, tôi sẽ viết eval cho các invariant của core ngay từ đầu: câu hỏi học thuật phải có trace `search_lessons/get_lesson`; câu trả lời có kiến thức phải có citation hợp lệ; tool lỗi thì không được báo thành công; input thiếu đối tượng phải hỏi lại. Tôi cũng sẽ chạy toàn bộ golden set sau mỗi thay đổi prompt hoặc tool schema để tránh sửa một case nhưng làm hỏng case khác. Kết quả và mô tả failure được lưu trong [golden set](../eval/test_cases.md).

## Điều tôi đóng góp lớn nhất và điều cần cải thiện

Đóng góp lớn nhất của tôi là biến ý tưởng “chatbot hỏi đáp giáo trình” thành một agent có vòng lặp hành động thật, có nguồn kiến thức, memory, skill, công cụ, trạng thái người dùng và các lớp kiểm soát đủ để chạy trên nhiều kênh. Tôi có thể giải thích luồng từ lúc nhận tin nhắn, cách model chọn tool, cách tool được kiểm quyền và thực thi, cho đến lúc kết quả được lưu và trả lại học viên.

Điểm tôi cần cải thiện là ưu tiên eval sớm hơn. Trong hackathon, tôi tập trung nhiều vào mở rộng core và tích hợp tính năng, trong khi những invariant quan trọng như “không bịa khi thiếu context” đáng lẽ phải được biến thành test tự động ngay khi vòng RAG đầu tiên hoạt động. Bài học này giúp tôi hiểu rằng chất lượng agent đến từ sự kết hợp giữa kiến trúc, guardrail và eval liên tục — không phải từ số lượng tool hay độ lớn của codebase.