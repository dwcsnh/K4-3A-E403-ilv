# Reflection — Nguyễn Quốc Tuấn (2A202602910)

## Vai trò và phạm vi chịu trách nhiệm

Trong dự án **Lớp học mô phỏng đa tác tử (Multi-Agent Classroom AI20K)** thuộc Track D (Học tập thích ứng & tương tác), tôi đảm nhiệm vai trò:
**Viết tài liệu AI spec, Code front end**

Phần giao diện Frontend được tôi phối hợp thực hiện cùng thành viên trong nhóm (bạn Nguyễn Mạnh Hải phụ trách phần trình chiếu slide và học liệu), trong đó trách nhiệm của tôi gồm:
1. **Xây dựng tài liệu AI Spec**: Phân tích dữ liệu thực tế (chatlog K4, khảo sát học viên), định nghĩa bài toán không dùng buzzword AI, xây dựng ma trận 4 lớp rủi ro (R1–R11), thiết lập HAX/PAIR guidelines và bộ Golden Set (20 test cases) cùng Quality Bar.
2. **Thiết kế & phát triển bộ khung chat tương tác với các agent**: Chịu trách nhiệm toàn bộ module hội thoại lớp học đa tác tử (hiển thị tin nhắn đa vai, chế độ lớp học chung/chat riêng 1-1, trích dẫn liên kết slide, chỉ báo tư duy và điều phối lượt nói chống xung đột).

---

## Phần tôi trực tiếp thực hiện

### 1. Xây dựng tài liệu AI Spec chuẩn mực
- **Khai thác dữ liệu thực tế (Evidence Mining)**: Trực tiếp phân tích tệp `tutor_turns.csv` với **13,494 lượt hội thoại** (29 bài giảng), bóc tách chính xác **3,097 lượt chat của khóa K4**. Phát hiện **45.1%** là yêu cầu giải thích nhưng bot cũ chỉ lặp lại lý thuyết suông (>90%) và **< 0.2%** có câu hỏi gợi mở. Kết hợp khảo sát n = 27 học viên AI20K (77.8% gặp "ảo tưởng hiểu bài", 66.7% ngại hỏi) để làm căn cứ thực chứng cho bài toán.
- **Định nghĩa bài toán chuẩn phương pháp luận**: Viết Core JTBD và Problem Statement tập trung 100% vào nỗi đau người học, tuyệt đối không chứa từ "AI" hay tên giải pháp công nghệ.
- **Xây dựng 4 lớp rủi ro & Quality Bar**: Cụ thể hóa 11 kịch bản lỗi (R1–R11) trên 4 tầng rủi ro (Mô hình, Đa tác tử, Sư phạm, Dữ liệu). Thiết lập Quality Bar định lượng: **≥ 80% (16/20 test cases)** đạt cả 3 chiều (*Groundedness*, *Role & Pedagogy*, *Task Contract*).

### 2. Thiết kế và phát triển bộ khung chat tương tác với các agent
Thay vì làm dàn trải, tôi phối hợp cùng nhóm và tập trung toàn lực vào module **Khung chat tương tác đa tác tử**:
- **Giao diện hội thoại đa tác tử**: Thiết kế luồng chat trực quan phân định rõ phong thái từng bot (TS. Minh — Trợ giảng Socratic, Bảo Nam — Bạn học đồng trang lứa, Nexus — Tạo học liệu). Hỗ trợ chuyển đổi linh hoạt giữa thảo luận chung cả lớp (Shared Classroom) và nhắn tin riêng 1-1 để người học không bị áp lực tâm lý.
- **Điều phối tương tác & Trạng thái**: Xây dựng chỉ báo tư duy (typing indicator) cho từng agent ("Thầy Minh đang chuẩn bị câu hỏi...", "Bảo Nam đang suy nghĩ..."), tạm khóa input khi bot đang phản hồi để chống spam và tránh việc hai bot nói đè nhau (cross-talk).
- **Clickable Grounding & HAX Guidelines**: Biến trích dẫn nguồn của bot thành huy hiệu tương tác (click vào tự chuyển slide bài giảng tương ứng để người học kiểm chứng); tích hợp công tắc bật/tắt từng bot (HAX G9) để tránh phân tâm; hiển thị gợi ý định hướng lại nội dung khi người học nhập câu hỏi mơ hồ hoặc lạc đề (HAX G10).
- **Prototype dự phòng (Vercel)**: Xây dựng bản mockup tương tác độc lập theo chuẩn Executive Design System và deploy lên Vercel, đảm bảo nhóm luôn có phương án demo mượt mà kể cả khi mạng phòng thi chập chờn.

---

## Các quyết định kỹ thuật quan trọng

1. **Tách biệt Lớp học chung và Chat riêng 1-1 trên giao diện**: Giải tỏa rào cản tâm lý sợ bị phán xét khi hỏi câu cơ bản trước tập thể của 66.7% học viên.
2. **Cơ chế UI Turn Locking**: Chủ động xếp hàng hiển thị trên frontend; khi một bot đang phản hồi, bot khác phải chờ lượt, ngăn chặn triệt để hiện tượng nói chồng chéo gây rối mắt.
3. **Trích dẫn tương tác (Clickable Grounding)**: Kết nối trực tiếp giữa nội dung chat và tài liệu học tập, giúp việc kiểm chứng nguồn chỉ tốn 1 click chuột.

---

## AI hỗ trợ tôi như thế nào

- **AI trợ lực**: Tăng tốc sinh khung giao diện React, hỗ trợ viết các lớp CSS/Tailwind cho bong bóng chat và rà soát các tiêu chí HAX/PAIR trong `spec.md`.
- **Con người kiểm soát**: Tự tay lọc và tính toán số liệu thật từ chatlog (3,097 lượt K4, n=27 khảo sát), kiên quyết không dùng số liệu phỏng đoán từ AI. Trực tiếp debug logic state, luồng cuộn tin nhắn và kiểm thử độ mượt mà trên trình duyệt thực tế.

---

## Bài học từ case fail của chính nhóm

- **Sự cố**: Trong Lượt chạy thử 1 (đạt 14/20 PASS), xuất hiện lỗi 3 lần các agent nói chồng nhau (Cross-talk) khi người học hỏi câu phức tạp, khiến giao diện nhảy giật và thông tin bị phân mảnh.
- **Bài học rút ra**:
  1. *Khung chat là lớp phòng vệ tương tác*: Không thể phó mặc cho prompt backend; frontend phải chủ động quản lý state hiển thị tuần tự.
  2. *Định hướng ngay tại ô nhập (HAX G10)*: Cần có gợi ý nhanh để hỗ trợ người dùng tách nhỏ câu hỏi khi có nhiều ý.
  3. *Kiểm thử phải nhìn trên giao diện thật*: Logic đúng trong terminal chưa chắc đã đem lại trải nghiệm tốt trên màn hình người dùng.

---

## Điều tôi đóng góp lớn nhất và điều cần cải thiện

- **Đóng góp lớn nhất**: Hoàn thiện tài liệu AI Spec có căn cứ dữ liệu thực tế vững chắc và xây dựng bộ khung chat đa tác tử trực quan, an toàn, phối hợp nhịp nhàng với các phần giao diện khác của nhóm.
- **Điều cần cải thiện**: Cần nâng cấp kiến trúc đồng bộ dữ liệu sang WebSocket thời gian thực thay vì cơ chế streaming/polling hiện tại để phản hồi của các tác tử mượt mà hơn.
