# TV3 - Advanced Tiles (ô đặc biệt)

**Chuyên ngành:** Công nghệ tri thức
**Vai trò:** Cài đặt ô fragile, cầu, 3 loại công tắc, tách/ghép khối. Đây là phần **Advanced tiles (10đ)** và là phần khó nhất về luật.

## Bảng tổng quan nhóm

| TV | Chuyên ngành | Vai trò chính |
|----|--------------|---------------|
| 1 (Võ Nhật Liệu)| Khoa học máy tính | Team Lead, UCS, A*, Thực nghiệm |
| 2 (Nguyễn Huy Thành)| Công nghệ tri thức | Game Core (luật cơ bản) |
| 3 (Hồ Văn Lực)| Công nghệ tri thức | Advanced Tiles (ô đặc biệt) |
| 4 (Hồ Trần Anh Kiệt)| Công nghệ thông tin | GUI 3D (Three.js) |
| 5 (Nguyễn Trần Minh Trí)| Mạng máy tính và viễn thông | BFS, DFS/IDS, đo đạc, API backend, Video |

## Mục tiêu

Mở rộng `State` và luật của TV2 để hỗ trợ mọi ô đặc biệt **đúng cả khi giải bằng solver**. Trạng thái phải chứa tình trạng đóng/mở của từng cầu.

## A. Việc cần làm

### A1. Ô fragile (cam)
- [ ] Khối **nằm** trên ô fragile: an toàn.
- [ ] Khối **đứng** trên ô fragile: ô vỡ, khối rơi, nước đi bị coi là thua.
- [ ] Thêm loại ô `fragile` vào nạp màn (phối hợp TV2).

### A2. Cầu (bridge)
- [ ] Cầu đóng = như void. Cầu mở = như ô thường.
- [ ] Mỗi công tắc liên kết với 1 hoặc nhiều cầu.
- [ ] Tình trạng cầu là **một phần của trạng thái** (ví dụ tuple bool theo thứ tự cố định). Hai trạng thái cùng vị trí nhưng khác tình trạng cầu là khác nhau.

### A3. Ba loại công tắc
- [ ] **Soft** (tròn): kích hoạt khi bất kỳ phần nào của khối chạm vào, đứng hay nằm đều được.
- [ ] **Heavy** (chữ X): chỉ kích hoạt khi khối **đứng** trên nó.
- [ ] **Split** (dấu ngoặc): chỉ kích hoạt khi khối **đứng** trên nó. Dịch chuyển khối tới các vị trí định sẵn và tách thành 2 cube 1x1x1.

### A4. Hành vi công tắc
- [ ] **Toggle**: mỗi lần kích hoạt đảo trạng thái cầu (mở thành đóng, đóng thành mở).
- [ ] **Permanent**: sau kích hoạt, cầu đặt vào trạng thái cố định.
- [ ] Mỗi công tắc trong JSON khai báo: loại, hành vi, danh sách cầu liên kết.

### A5. Tách và ghép khối
- [ ] Thêm vào `State`: vị trí 2 cube và **cube nào đang được điều khiển**.
- [ ] Thêm hành động **đổi cube điều khiển** (phím cách) vào `actions`. Hành động này cũng phải giải được bởi solver.
- [ ] Mỗi cube lăn như khối 1x1x1: lăn 1 ô theo 4 hướng.
- [ ] Ghép lại thành khối 1x1x2 khi 2 cube ở 2 ô **kề nhau**.
- [ ] Cube đơn kích hoạt được soft switch, **không** kích hoạt được heavy switch, và **không** thắng màn.
- [ ] Cube đứng trên ô fragile thì ô vỡ (cube chiếm 1 ô, giống khối đứng). Ghi quyết định này vào tài liệu và thống nhất với nhóm.

### A6. Kiểm thử
- [ ] `tests/test_tiles.py`: ít nhất 1 test cho mỗi quy tắc trên (fragile, từng loại công tắc, toggle/permanent, tách, ghép, cube không thắng).
- [ ] Test trạng thái: hai trạng thái khác tình trạng cầu phải không bằng nhau và có hash khác.

### A7. Màn chơi cho bộ test
- [ ] Cùng TV1 tạo 3-5 màn **có fragile**, 3-5 màn **có công tắc và cầu**, 3-5 màn **kết hợp có split**. Mỗi màn phải giải được.

## B. Phần báo cáo của bạn
- Mô tả từng loại ô đặc biệt và luật tương ứng.
- Mô tả cách mở rộng trạng thái (cầu, split, cube điều khiển) và vì sao cần.
- Cùng TV5 viết phần mô tả BFS/DFS nếu cần nhắc đến trạng thái mở rộng.

## C. Mốc thời gian

| Tuần | Việc |
|------|------|
| 1 | Đọc luật Mục 2.5 kỹ, thiết kế cách thêm trường vào `State` cùng TV2, làm fragile + cầu + soft/heavy |
| 2 | Làm split, tách/ghép, toggle/permanent, test, tạo màn cho bộ test |
| 3 | Sửa lỗi do solver phát hiện, hỗ trợ quay video, viết báo cáo |

## D. Phối hợp
- **TV2**: sửa chung `State` và JSON. Làm buổi 1 chung để không xung đột.
- **TV4**: báo TV4 danh sách sự kiện cần vẽ (cầu đổi trạng thái, ô vỡ, tách, ghép) trong JSON trả về.
- **TV1 và TV5**: báo khi đổi `actions` (thêm hành động đổi cube) vì solver phải xử lý.

## E. Định nghĩa "xong"
- Mỗi ô đặc biệt có ít nhất 1 màn chạy đúng bằng tay và giải được bằng BFS.
- Test qua toàn bộ.
- Solver không bị vòng lặp vô hạn khi có toggle (tập visited đúng vì tình trạng cầu nằm trong trạng thái).

## F. Câu hỏi phỏng vấn nên chuẩn bị
- Tại sao tình trạng cầu phải nằm trong trạng thái?
- Khác nhau giữa soft, heavy, split?
- Khi khối tách, solver xử lý như thế nào?
