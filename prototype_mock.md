# Mục tiêu
1 prototype cho 1 tính năng multi agent classroom
1 file html với luồng demo, có thể có mock data

# Tính năng của multi agent classroom

Người dùng có thể enable mode multi-agent classroom từ 1 bài giảng (slide).
Màn hình sẽ hiển thị trang multi agent classroom gồm 3 agent.

Có 3 agent:
- Teaching agent: đóng vai trò giảng cho người dùng các câu hỏi liên quan đến bài giảng.
- Student agent: đóng vai trò bạn học, sẽ hỏi người dùng các câu hỏi liên quan đến bài giảng để người dùng trả lời, qua đó người dùng có thể học thông qua phương pháp active recall
- Learning material generator: agent có thể generate các quiz, flashcard, mindmap, etc liên quan đến bài giảng từ yêu cầu của người dùng

# Các màn hình

## Màn hình bài giảng 

### Component

- Sidebar: bên trái, danh sách các bài giảng trong lớp học
- Main content: bên phải, hiển thị nội dung bài giảng
    - Header: tiêu đề bài giảng
    - Body: nội dung bài giảng
    - Footer: các nút điều hướng bài giảng (next, prev)
- Multi-agent classroom button: Người dùng có thể bật chế độ multi-agent classroom từ nút này

## Màn hình multi agent classroom

### Component

- Sidebar(trái): Hiển thị lịch sử trò chuyện với từng agent
- Main content: Ở giữa, hiển thị nội dung cuộc trò chuyện
- Sidebar(phải): Hiển thị các artifact đã gen

