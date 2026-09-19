# Reflection — Trần Thu Phương (2A202602366)

## Vai trò

Documentation — viết tài liệu test case, dựng video mô phỏng và làm survey phục vụ việc đo chất lượng và xác nhận vấn đề người dùng.

## Phần tôi thực hiện

- Xây dựng và tổ chức bộ golden set gồm 20 tình huống: câu hỏi ngoài tài liệu, input mơ hồ, yêu cầu vượt phạm vi, câu có hậu quả nếu trả lời sai và các tình huống thực tế từ Discord.
- Viết expected behaviour cho từng case để việc chấm không chỉ dựa trên cảm nhận: khi nào phải hỏi lại, từ chối, trả lời có citation hoặc không được khẳng định hành động tool đã thành công.
- Hỗ trợ chuẩn bị khảo sát về trở ngại khi tự học và đưa kết quả vào phần evidence/impact của nhóm.
- Ghi nhận các case pass, fail và partial để nhóm nhìn được cả failure thay vì chỉ demo luồng happy path.
- Hỗ trợ nhóm tạo video demo từ tài liệu sẵn có từ bài giảng
- Dựng video mô phỏng tài liệu classroom theo kiểu active recall
Phần việc này thể hiện trong [golden set](../eval/test_cases.md), [AI Spec](../spec.md) §7.

## AI hỗ trợ thế nào

Tôi dùng AI để gợi ý biến thể câu hỏi và rà xem bộ case đã phủ bốn lớp chỗ khó chưa. Mỗi expected output, nguồn case và tiêu chí pass/fail vẫn được tôi kiểm tra, vì nếu AI tự viết cả câu hỏi lẫn đáp án mong đợi thì bộ eval rất dễ thiên lệch hoặc bỏ sót hành vi nguy hiểm.

## Bài học từ case fail của nhóm

Ở case 19, agent lần đầu nói như đã tạo sự kiện Discord nhưng kết quả tool chưa rõ ràng; sau đó mới tạo thành công ở lần thử khác nên case được ghi **PARTIAL**. Tôi nhận ra test cho agent có tool không thể chỉ kiểm tra câu trả lời nghe hợp lý: expected behaviour phải yêu cầu đối chiếu trạng thái thực tế của tool trước khi xác nhận thành công. Lần sau tôi sẽ bổ sung rõ hơn các case về tool timeout, thiếu quyền và retry để tránh việc agent “báo đã xong” khi hành động chưa xảy ra.