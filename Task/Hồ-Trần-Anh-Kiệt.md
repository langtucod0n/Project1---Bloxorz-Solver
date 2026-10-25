# TV4 - GUI 3D (Three.js)

**Chuyên ngành:** Công nghệ thông tin
**Vai trò:** Giao diện 3D. Thầy yêu cầu tiêu chí GUI là 3D nên đây là phần quyết định điểm GUI và hình ảnh video.

## Bảng tổng quan nhóm

| TV | Chuyên ngành | Vai trò chính |
|----|--------------|---------------|
| 1 (Võ Nhật Liệu)| Khoa học máy tính | Team Lead, UCS, A*, Thực nghiệm |
| 2 (Nguyễn Huy Thành)| Công nghệ tri thức | Game Core (luật cơ bản) |
| 3 (Hồ Văn Lực)| Công nghệ tri thức | Advanced Tiles (ô đặc biệt) |
| 4 (Hồ Trần Anh Kiệt)| Công nghệ thông tin | GUI 3D (Three.js) |
| 5 (Nguyễn Trần Minh Trí)| Mạng máy tính và viễn thông | BFS, DFS/IDS, đo đạc, API backend, Video |

## Mục tiêu

Làm giao diện 3D trên trình duyệt bằng Three.js. **Nguyên tắc quan trọng: JavaScript chỉ vẽ, không chứa luật chơi.** Mọi luật nằm ở Python (TV2, TV3), giao diện chỉ gửi yêu cầu và vẽ lại trạng thái nhận được.

## A. Việc cần làm

### A1. Thiết lập (tuần 1)
- [x] Thư mục `web/` gồm `index.html`, `main.js`, `style.css`, `lib/three.min.js` (chép sẵn file Three.js vào repo, **không** phụ thuộc mạng, **không** dùng npm/build).
- [x] Vẽ được lưới các ô từ dữ liệu JSON giả (hardcode trước khi có API).
- [x] Camera nghiêng kiểu isometric, xoay được bằng chuột, có ánh sáng và đổ bóng.

### A2. Vẽ các loại ô
Mỗi loại một màu/hình khác nhau, để nhìn ra ngay:
- [ ] Ô thường (xám), void (không vẽ), ô goal (lỗ tối), ô fragile (cam).
- [ ] Cầu đóng và cầu mở (cầu mở thành ô thường, có hoạt ảnh trượt lên/xuống).
- [ ] 3 loại công tắc (soft tròn, heavy chữ X, split ngoặc), vẽ dấu trên mặt ô.

### A3. Khối và hoạt ảnh
- [x] Vẽ khối 1x1x2 với 3 orientation.
- [x] **Hoạt ảnh lăn thật**: đặt khối vào 1 nhóm (group) có điểm xoay ở cạnh, quay nhóm 90 độ quanh cạnh đó, rồi cập nhật vị trí khối theo trạng thái mới.
- [ ] Hoạt ảnh thua: khối rơi xuống. Hoạt ảnh thắng: khối chìm vào lỗ goal.
- [ ] Ô fragile vỡ khi khối đứng lên.
- [ ] Khối tách thành 2 cube, viền sáng cho cube đang điều khiển, hoạt ảnh ghép khi kề nhau.

### A4. Điều khiển và nút
- [ ] Phím mũi tên hoặc WASD để lăn khối, phím cách để đổi cube.
- [ ] Nút: **New Game, Restart, Solve BFS, Solve DFS, Solve UCS, Solve A***, chọn màn chơi.
- [ ] Bảng hiện số liệu của lần giải gần nhất: thời gian, bộ nhớ, số node mở rộng, độ dài lời giải.
- [ ] Nút **Phát lại lời giải**: lấy danh sách nước đi, chạy từng nước với hoạt ảnh (có thanh tốc độ).
- [ ] Hiện số nước đi, trạng thái (đang chơi/thắng/thua).

### A5. Nối với backend (tuần 2, cùng TV5)
- [ ] Dùng `fetch()` gọi API của TV5: tải màn, gửi nước đi, xin lời giải.
- [ ] Không tự tính luật trong JS. Nếu nước đi sai thì backend trả lời, JS chỉ vẽ kết quả.
- [ ] Hiện thông báo lỗi dễ nhìn (ví dụ khi máy chủ chưa chạy).

## B. Phần báo cáo của bạn
- Mô tả kiến trúc giao diện (Three.js + backend Python), các thành phần và luồng dữ liệu.
- Ảnh chụp màn hình từng loại ô và khối.
- Cùng TV5 làm phần hướng dẫn chạy (README).

## C. Mốc thời gian

| Tuần | Việc |
|------|------|
| 1 | Dựng khung, vẽ lưới, vẽ khối, hoạt ảnh lăn, dùng JSON giả |
| 2 | Vẽ ô đặc biệt, cầu, tách/ghép, nối API thật, nút Solve, phát lại lời giải |
| 3 | Chỉnh đẹp (ánh sáng, màu), sửa lỗi, quay video cùng TV5, chụp ảnh cho báo cáo |

## D. Phối hợp
- **TV2 và TV3**: xin mẫu JSON trạng thái ngay tuần 1 (vị trí khối, orientation, cầu, split, cube điều khiển, trạng thái thắng/thua).
- **TV5**: thống nhất tên endpoint và định dạng trả về. Nhóm trưởng sẽ duyệt.
- **TV1**: cần số liệu solver hiện ra bảng. Hỏi TV1 nếu thiếu thông tin.

## E. Định nghĩa "xong"
- Chơi tay được hết 1 màn có đủ loại ô mà không lỗi hiển thị.
- Bấm Solve cho mỗi thuật toán thì khối tự động chạy đến đích.
- Chạy được trên máy khác chỉ bằng `python main.py` (không cần cài thêm gì cho phần web).

## F. Mẹo
- Nếu chưa quen Three.js: bắt đầu với ví dụ "hình lập phương xoay" trong tài liệu chính thức, rồi thêm dần.
- Lăn quanh cạnh là phần khó nhất. Làm riêng 1 hàm `rollAnimation(direction)`, thử kỹ trước khi thêm gì khác.
- Nếu quá tải, nhờ TV3 phụ phần hoạt ảnh cầu và công tắc (TV3 hiểu luật rõ nhất).

## G. Câu hỏi phỏng vấn nên chuẩn bị
- Tại sao JS không chứa luật chơi?
- Hoạt ảnh lăn được làm như thế nào?
- Khi bấm Solve A*, dữ liệu đi từ đâu đến đâu?

