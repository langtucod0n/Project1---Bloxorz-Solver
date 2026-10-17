# TV5 - BFS, DFS/IDS, Đo đạc, API Backend, Video

**Chuyên ngành:** Mạng máy tính và viễn thông
**Vai trò:** Thuật toán tìm kiếm không thông tin (BFS, DFS/IDS), module đo hiệu năng, máy chủ API nối Python với giao diện 3D, đóng gói chạy, và quay/dựng video demo.

## Bảng tổng quan nhóm

| TV | Chuyên ngành | Vai trò chính |
|----|--------------|---------------|
| 1 (Võ Nhật Liệu)| Khoa học máy tính | Team Lead, UCS, A*, Thực nghiệm |
| 2 (Nguyễn Huy Thành)| Công nghệ tri thức | Game Core (luật cơ bản) |
| 3 (Hồ Văn Lực)| Công nghệ tri thức | Advanced Tiles (ô đặc biệt) |
| 4 (Hồ Trần Anh Kiệt)| Công nghệ thông tin | GUI 3D (Three.js) |
| 5 (Nguyễn Trần Minh Trí)| Mạng máy tính và viễn thông | BFS, DFS/IDS, đo đạc, API backend, Video |

## Mục tiêu

Làm hai thuật toán cơ bản (20đ), module đo 4 số liệu dùng chung cho mọi solver, máy chủ API để giao diện 3D gọi được, và video demo (10đ).

## A. Việc cần làm

### A1. BFS (10đ)
- [x] File `solvers/bfs.py`, dùng `collections.deque` và tập `visited`.
- [x] Trả về danh sách nước đi của lời giải (nếu có) và số liệu đo đạc.
- [x] Trạng thái là hashable (TV2 làm), nên dùng thẳng trong tập `visited`.

### A2. DFS hoặc IDS (10đ)
- [x] File `solvers/dfs.py`. Có thể chọn IDS thay DFS, **ghi rõ trong báo cáo**. **(đã chọn DFS, ghi trong Source/feature-tv5-search-api.md)**
- [x] Bắt buộc xử lý trạng thái lặp (tập `visited`), để không chạy vòng tròn.
- [x] Nếu dùng DFS thuần, đặt giới hạn độ sâu để không tràn stack (đề xuất không đệ quy, dùng stack tự tạo).
- [x] Nhận xét trong báo cáo: lời giải DFS thường dài, không tối ưu. **(có trong Source/feature-tv5-search-api.md)**

### A3. Module đo đạc (dùng chung, làm sớm)
- [x] File `solvers/metrics.py` với hàm bọc quanh mỗi solver, đo:
  - **Thời gian tìm kiếm** (`time.perf_counter`).
  - **Bộ nhớ đỉnh** (`tracemalloc`).
  - **Số node mở rộng** (đếm mỗi lần lấy node ra mở rộng).
  - **Độ dài lời giải** (số nước đi).
- [x] Giao diện thống nhất: mọi solver trả về cùng một cấu trúc kết quả, ví dụ `{moves, expanded, time, peak_memory, length}`.
- [ ] Gửi mẫu cấu trúc cho TV1 và TV4 ngay tuần 1. TV1 dùng để benchmark, TV4 dùng để hiển thị. **(chưa gửi)**

### A4. API backend (tuần 1 đến 2)
- [x] Dùng FastAPI hoặc Flask. File `server/app.py`.
- [x] Python giữ toàn bộ luật và solver. API chỉ gọi vào `game/` và `solvers/`.
- [ ] Endpoint đề xuất: **(xong levels, load, move, solve với bfs/dfs; chưa có ucs/astar (chờ TV1) và switch_control (chờ TV3))**
  - `POST /api/load` với `level_id` -> trạng thái ban đầu
  - `POST /api/move` với `direction` -> trạng thái mới
  - `POST /api/switch_control` -> đổi cube điều khiển
  - `POST /api/solve` với `algorithm` (`bfs`, `dfs`, `ucs`, `astar`) và `level_id` -> `{moves, metrics}`
  - `GET /api/levels` -> danh sách màn
- [ ] Định dạng JSON trạng thái chốt cùng TV2, TV3 và TV4. Nhóm trưởng duyệt. **(chưa chốt với TV2, TV3, TV4)**
- [x] Xử lý lỗi rõ ràng (nước đi sai, màn không tồn tại, solver hết thời gian) và trả mã lỗi để giao diện hiện thông báo.
- [x] Đặt giới hạn thời gian cho mỗi lần giải để máy chủ không bị treo trên màn quá khó.

### A5. Đóng gói và chạy (tuần 3)
- [x] `main.py`: khởi động máy chủ và tự mở trình duyệt.
- [x] `requirements.txt` liệt kê đúng thư viện (FastAPI/Flask, uvicorn, matplotlib cho TV1). **(chưa có matplotlib, TV1 thêm)**
- [x] `README.md`: đúng 2 lệnh `pip install -r requirements.txt` và `python main.py`, kèm cấu trúc thư mục và lưu ý nếu cổng bị chiếm.
- [x] **Thử chạy trên máy sạch** (máy khác hoặc môi trường ảo mới) trước khi nộp. **(đã thử bằng môi trường ảo mới trên máy Windows của TV5; chưa thử trên máy khác)**

### A6. Video demo (10đ)
- [x] Viết kịch bản trước, gồm 2 phần theo đề: **(bản nháp ở Source/docs/video_script.md)**
  1. **Giao diện (5đ)**: bàn cờ có đủ loại ô (thường, void, goal, fragile, công tắc, cầu), khối ở các orientation, các nút điều khiển.
  2. **Tính năng (5đ)**: chơi tay (lăn khối, kích hoạt công tắc, thắng, thua), chạy BFS, DFS, UCS, A* và phát lại lời giải.
- [ ] Quay màn hình bằng OBS Studio, **có phụ đề hoặc lời thuyết minh** (Anh hoặc Việt). **(chưa làm; chờ TV1, TV3, TV4)**
- [ ] Tải lên YouTube ở chế độ công khai, đưa link vào báo cáo. **(chưa làm)**
- [ ] Dành đủ thời gian: quay thử 1 lần trước, để TV4 chỉnh giao diện, rồi quay bản cuối vào tuần 3. **(chưa làm)**

## B. Phần báo cáo của bạn
- Mô tả BFS, DFS/IDS (cách xử lý trạng thái lặp).
- Mô tả module đo đạc và cách đo bộ nhớ.
- Phần hướng dẫn chạy và kiến trúc backend (cùng TV4).
- Link video.

## C. Mốc thời gian

| Tuần | Việc |
|------|------|
| 1 | BFS, DFS trên màn đơn giản, module đo đạc, gửi cấu trúc kết quả cho TV1 và TV4 |
| 2 | API backend, nối với TV4, nối UCS và A* của TV1 vào API |
| 3 | Đóng gói, README, thử máy sạch, quay và dựng video, nối link vào báo cáo |

## D. Phối hợp
- **TV2 và TV3**: gọi `game/` trực tiếp, cần giao diện 5 hàm ổn định.
- **TV4**: thống nhất endpoint và JSON, test thử cùng nhau sớm.
- **TV1**: kết quả đo đạc chạy được ở benchmark; hỗ trợ TV1 nếu thiếu số liệu.

## E. Định nghĩa "xong"
- BFS tìm được lời giải ngắn nhất theo số nước trên mọi màn của bộ test.
- DFS/IDS ra lời giải hợp lệ trên các màn, không lặp vô hạn.
- Giao diện gọi được cả 4 solver qua API và nhận lại số liệu.
- Người ngoài làm theo README thì chạy được.
- Video có phụ đề/thuyết minh, link YouTube công khai.

## F. Câu hỏi phỏng vấn nên chuẩn bị
- BFS và DFS khác nhau ở đâu? Vì sao BFS cho lời giải ngắn nhất?
- Nếu không có tập `visited` thì chuyện gì xảy ra?
- Bộ nhớ đỉnh đo bằng công cụ nào, đo ở đâu?
- Giao diện nói chuyện với Python qua đâu?

