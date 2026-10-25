# TV2 - Game Core (luật chơi cơ bản)

**Chuyên ngành:** Công nghệ tri thức
**Vai trò:** Xây dựng "bộ não" luật chơi. Mọi solver, GUI và API đều dựa vào phần này.

## Bảng tổng quan nhóm

| TV | Chuyên ngành | Vai trò chính |
|----|--------------|---------------|
| 1 (Võ Nhật Liệu)| Khoa học máy tính | Team Lead, UCS, A*, Thực nghiệm |
| 2 (Nguyễn Huy Thành)| Công nghệ tri thức | Game Core (luật cơ bản) |
| 3 (Hồ Văn Lực)| Công nghệ tri thức | Advanced Tiles (ô đặc biệt) |
| 4 (Hồ Trần Anh Kiệt)| Công nghệ thông tin | GUI 3D (Three.js) |
| 5 (Nguyễn Trần Minh Trí)| Mạng máy tính và viễn thông | BFS, DFS/IDS, đo đạc, API backend, Video |

## Mục tiêu

Hoàn thành phần **Core mechanics (10đ)** và đưa cho cả nhóm một giao diện trạng thái ổn định ở **cuối ngày 3**, vì mọi người khác phụ thuộc vào bạn.

## A. Việc cần làm

### A1. Giao diện trạng thái (làm đầu tiên, cùng TV1)
- [ ] File `game/state.py`: lớp `State` bất biến (frozen dataclass hoặc namedtuple), có thể băm (hashable).
- [ ] Trường tối thiểu: ô khối đang chiếm, orientation (STANDING, LYING_H, LYING_V). TV3 sẽ thêm trường cho cầu và split, nên **để sẵn chỗ mở rộng**.
- [ ] File `game/game.py` với 5 hàm: `initial_state`, `actions`, `result`, `is_goal`, `cost`.
- [ ] Cho `cost` tạm trả về 1, TV1 sẽ đổi sau.

### A2. Bảng chuyển orientation (quan trọng nhất)
- [ ] Bảng được định nghĩa riêng ở 1 chỗ, mỗi cặp (orientation, hướng) -> (orientation mới, vị trí mới):
  - Đứng + hướng bất kỳ -> nằm dọc theo hướng đó (chiếm 2 ô kề nhau).
  - Nằm dọc theo hướng lăn -> đứng lên 1 ô.
  - Nằm ngang hướng lăn -> vẫn nằm, xê dịch 1 ô.
- [ ] Viết **unit test cho tất cả 12 cặp** (3 orientation x 4 hướng) trước khi làm tiếp.

### A3. Kiểm tra nước đi
- [ ] Nước đi sai nếu bất kỳ ô nào của khối là void hoặc ngoài bàn.
- [ ] Thắng chỉ khi khối **đứng** trên ô goal. Nằm qua ô goal không thắng.
- [ ] Phân biệt 3 kết quả: `playing`, `won`, `lost` (rơi).

### A4. Nạp màn chơi
- [ ] File `game/level_loader.py` đọc JSON. Đề xuất định dạng:
```
{
  "id": "L01",
  "grid": ["..FF.", ".SFG.", "....."],
  "start": [0, 0],
  "legend": {".": "floor", "#": "void", "G": "goal", "F": "fragile"}
}
```
- [ ] Định dạng phải mở rộng được để TV3 thêm công tắc, cầu, split mà không phá màn cũ.
- [ ] Tạo 3-5 màn đơn giản cho nhóm 1 trong bộ test.

### A5. Kiểm thử
- [ ] Thư mục `tests/test_core.py`: test chuyển orientation, nước sai, thắng, thua.
- [ ] Test `result` không thay đổi trạng thái cũ (vì trạng thái bất biến).

## B. Phần báo cáo của bạn
- Mô tả luật chơi và bảng chuyển orientation.
- Mô tả biểu diễn trạng thái và định dạng JSON màn chơi.

## C. Mốc thời gian

| Tuần | Việc |
|------|------|
| 1 | Trạng thái + 5 hàm giao diện (xong cuối ngày 3), bảng chuyển orientation + test, nạp JSON |
| 2 | Hỗ trợ TV3 gộp ô đặc biệt vào `State`, sửa lỗi khi solver phát hiện sai |
| 3 | Test lại tất cả màn, hỗ trợ viết báo cáo |

## D. Phối hợp
- Với **TV1**: chốt giao diện trạng thái.
- Với **TV3**: thống nhất cách thêm trường cầu/split vào `State`. Làm chung buổi 1 để không xung đột.
- Với **TV4 và TV5**: gửi mẫu JSON trạng thái để họ làm API và GUI song song.

## E. Định nghĩa "xong"
- 12 test chuyển orientation đều qua.
- Có thể chơi hết 1 màn đơn giản bằng cách gọi `result` liên tục đến khi `won`.
- Mọi người khác gọi được 5 hàm mà không cần hỏi.

## F. Câu hỏi phỏng vấn nên chuẩn bị
- Giải thích bảng chuyển orientation.
- Tại sao trạng thái phải bất biến và hashable?
- Khối đứng trên goal thì thắng, nằm trên goal thì sao?
