# Reflection cá nhân — Nguyễn Mạnh Hải (2A202602988)

**Vai trò** Viết tài liệu AI spec, Code front end

---

## Phần tôi thực hiện

### Khảo sát người dùng bằng google form để tìm pain point khi sử dụng nền tảng học tương tự như Vlearn.

### Front end 
Tôi dựng toàn bộ lớp giao diện của prototype bằng Next.js + TypeScript, từ màn hình trắng đến bản demo chạy thật.

- Tạo giao diện ba khối màn hình: lớp học, bài học, học liệu 
- Lớp mock để front end chạy được trước khi pipeline agent sẵn sàng 
- Cố gắng tạo giao diện base theo VLearn
- Nối dữ liệu bài giảng từ vlearn-pack thật vào UI: parser transcript, đọc slide PDF

## AI hỗ trợ thế nào
- **Dựng khung UI nhanh.** Toàn bộ scaffold Next.js, các component chat/quiz/flashcard và CSS theme được sinh bằng AI rồi tôi sửa lại. Nếu gõ tay thì 47,5 giờ không đủ để vừa có front end vừa có spec vừa có eval.
- **Việc lặp và việc dịch định dạng.** Parser transcript, đọc PDF slide, chuyển `mock-data` sang dữ liệu bài giảng thật — đây là loại việc AI làm tốt vì có input/output rõ ràng, tôi kiểm tra bằng cách mở app xem có đúng nội dung không.
- **Runner eval.** Tôi mô tả yêu cầu (chạy từng case, tách expected khỏi prompt, ghi ra file có thể đọc bằng mắt), AI viết bản đầu, tôi sửa phần tách `expected_behavior` — vì bản đầu nhét cả expected vào context gửi model, tức là tự chấm điểm cho chính mình.

### Chỗ tôi phải tự làm

- **Quyết định sản phẩm.** Chọn augment thay automation, chọn 4 non-goals, quyết định không dùng nguồn ngoài — AI đưa được lựa chọn nhưng không chịu trách nhiệm cho cost-of-error. Phần này tôi viết tay.
- **Đọc kết quả eval.** AI chạy được 20 case, nhưng nhìn 6 case FAIL để nói ra "đây là lỗi điều phối, không phải lỗi prompt" là việc của người.

### Bài học về cách dùng AI

- Dùng AI có cấu trúc và kế hoạch, không dùng auto trong quá trình code; kiểm tra lại các option của AI sinh ra.
- Tự nghĩ ra workflow cũng như các pain point, các statement. 
- Tự test trên tập có sẵn.

---

## Bài học từ case fail của nhóm

### 1. Case fail: run-01 không qua quality bar

Quality bar nhóm chốt ở CP4: **16/20 case PASS, không có critical violation** . Lượt chạy 1 ngày 17/09 trên `gpt-4o-mini` được **14/20 — trượt**. Sáu case FAIL, ghi trong `eval/run_result.md`:

| Kiểu lỗi | Số case |
|---|---|
| Các agent nói chồng nhau | 3 |
| Trích nội dung kiến thức sai nguồn | 2 |
| Không hoàn thành đủ `must_do` khi query có nhiều yêu cầu | 1 |

Lượt 2 ngày 18/09 (thêm `gpt-4o` cho các bước điều phối) lên **16/20 — vừa đủ qua**, nhưng lộ ra kiểu lỗi mới: 2 case agent vẫn trả lời dù task nằm ngoài phạm vi, 1 case vi phạm nguyên tắc Socratic.

### 2. Bốn điều tôi rút ra

**a. Lỗi nặng nhất không nằm ở từng agent, mà ở chỗ nối giữa chúng.** 3/6 FAIL là "agent nói chồng nhau" — không agent nào trả lời sai, nhưng hệ thống vẫn hỏng. Nhóm tôi đã bỏ nhiều công viết prompt cho từng agent và gần như không viết gì cho luật điều phối. Lần sau, với hệ đa tác tử, tôi sẽ coi **giao thức "ai được nói, khi nào, nói xong thì nhường ai"** là artifact phải viết trước, ngang hàng với system prompt.

**b. Quality bar phải chốt trước khi chạy, và trượt thì phải nói là trượt.** Bar 16/20 được chốt ở CP4 rồi mới chạy, nên con số 14/20 không thể tự bào chữa được. Cảm giác lúc đó rất muốn hạ bar xuống 13/20 cho qua. Không hạ là quyết định đúng — vì nếu hạ thì lượt 2 đã không ai buồn đổi model cho bước điều phối, và 3 lỗi nói chồng vẫn còn nguyên.

**c. Trượt sớm rẻ hơn trượt muộn.** Thầy nói ở buổi 3: thà biết mình làm không được, biết vì sao, rồi dừng — còn hơn cứ làm đến khi hết tiền. Run-01 đóng đúng vai đó. Nó tốn nửa ngày và đổi lại một danh sách lỗi cụ thể. Nếu nhóm bỏ qua eval và đi thẳng tới demo, ba lỗi nói chồng sẽ xuất hiện trước mặt giám khảo, ở tình huống không sửa được.

**d. 16/20 là vừa đủ qua, không phải là xong.** Lượt 2 qua bar nhưng đẻ ra kiểu lỗi mới — agent trả lời cả việc ngoài phạm vi, tức là đúng thứ mà non-goal số 4 trong §4 cấm. Bar là sàn chứ không phải đích. Việc cần làm tiếp là siết luật từ chối ở tầng gateway thay vì trông vào prompt, và đó là thứ tôi sẽ đề xuất cho vòng validation CP5.


