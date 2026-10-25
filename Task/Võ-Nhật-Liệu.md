# TV1 - Nhóm trưởng + Search & Experiment Lead

**Chuyên ngành:** Khoa học máy tính
**Vai trò:** Team Lead, UCS, A*, thực nghiệm (benchmark), phần Experiments trong báo cáo

## Bảng tổng quan nhóm

| TV | Chuyên ngành | Vai trò chính |
|----|--------------|---------------|
| 1 (Võ Nhật Liệu)| Khoa học máy tính | Team Lead, UCS, A*, Thực nghiệm |
| 2 (Nguyễn Huy Thành)| Công nghệ tri thức | Game Core (luật cơ bản) |
| 3 (Hồ Văn Lực)| Công nghệ tri thức | Advanced Tiles (ô đặc biệt) |
| 4 (Hồ Trần Anh Kiệt)| Công nghệ thông tin | GUI 3D (Three.js) |
| 5 (Nguyễn Trần Minh Trí)| Mạng máy tính và viễn thông | BFS, DFS/IDS, đo đạc, API backend, Video |

## Mục tiêu

Điều phối cả nhóm để nộp đúng hạn, và tự làm phần "AI" cốt lõi: UCS, A*, heuristic, so sánh các thuật toán.

## A. Việc của nhóm trưởng

- [ ] Tạo GitHub repo (Private), mời 4 bạn, khóa nhánh `main` (bắt buộc Pull Request).
- [ ] Tạo Issues và bảng Todo/Doing/Done cho từng việc trong 5 file này.
- [ ] Tuần 1: cùng TV2 chốt **giao diện trạng thái chung** (mục C bên dưới) trước ngày 3.
- [ ] Họp nhanh 15 phút mỗi đầu tuần, kiểm tra tiến độ mỗi cuối tuần.
- [ ] Review và merge Pull Request. Đọc code của cả nhóm để trả lời phỏng vấn.
- [ ] Cuối dự án: đóng băng `main`, gắn tag `v1.0-submit`, nộp file `MSSV1_MSSV2_...`.
- [ ] Ghi bảng phân công và phần trăm hoàn thành vào báo cáo (dựa trên Issues và commit).

## B. Việc kỹ thuật

### B1. UCS (10đ)
- [ ] File `solvers/ucs.py`, dùng `heapq`, có tập `visited`/`best_cost`.
- [ ] **Hàm chi phí** (viết rõ trong báo cáo), đề xuất:
  - Mỗi nước lăn bình thường: chi phí 1.
  - Lăn lên/nằm trên ô fragile: chi phí 2 (rủi ro hơn).
  - Các chi phí luôn > 0 để UCS đúng.
- [ ] Giải thích: nếu mọi nước đều là 1 thì UCS = BFS, nên phải có chi phí không đều.

### B2. A* (10đ)
- [ ] File `solvers/astar.py`, dùng `f = g + h`.
- [ ] Heuristic đề xuất (chọn 1, hoặc kết hợp bằng `max`):
  - Manhattan từ khối đến ô đích, chia 2, nhân chi phí nhỏ nhất của 1 nước đi.
  - Cộng phạt orientation: khối chưa đứng thì cần thêm ít nhất 1 nước.
  - Hoặc: khoảng cách ngắn nhất trên lưới 4 hướng, bỏ qua void/fragile (cận dưới).
- [ ] **Chứng minh trong báo cáo**: h không bao giờ lớn hơn chi phí thật (admissible) và có consistent không. Phải đúng với hàm chi phí ở B1 (h dùng chi phí nhỏ nhất của 1 nước, không dùng số 1 nếu chi phí nhỏ nhất khác 1).
- [ ] Viết test kiểm tra trên màn nhỏ: A* ra lời giải có chi phí bằng UCS.

### B3. Thực nghiệm (20đ)
- [ ] Chốt **bộ test cố định**, 4 nhóm, mỗi nhóm 3-5 màn (tổng 12-16 màn):
  1. Đơn giản (không ô đặc biệt)
  2. Có ô fragile
  3. Có công tắc và cầu
  4. Kết hợp (fragile + công tắc + split)
  Phối hợp TV2/TV3 để làm file JSON cho các màn này.
- [ ] File `benchmark/run_all.py`: chạy mỗi thuật toán trên mỗi màn, lặp lại 3-5 lần, lấy trung bình thời gian.
- [ ] Ghi 4 số liệu: thời gian, bộ nhớ đỉnh, số node mở rộng, độ dài lời giải (dùng module đo của TV5).
- [ ] Xuất file CSV, vẽ biểu đồ bằng `matplotlib` (cột/đường theo nhóm màn).
- [ ] Viết nhận xét: thuật toán nào nhanh, nào tốn bộ nhớ, vì sao DFS ra lời giải dài, vì sao A* mở ít node hơn, trường hợp nào A* không hơn BFS.

## C. Giao diện trạng thái chung (chốt cùng TV2)

```
initial_state(level)
actions(state)           -> danh sách nước đi hợp lệ
result(state, action)    -> trạng thái mới
is_goal(state)
cost(state, action)
```
Trạng thái phải **hashable** (dùng tuple/frozenset) và gồm: vị trí khối, orientation, tình trạng từng cầu, và (nếu tách) vị trí 2 cube + cube đang điều khiển.

## D. Cấu trúc thư mục

```
Source/
  main.py  README.md  requirements.txt
  game/  solvers/  benchmark/  levels/  server/  web/  tests/
Report.pdf
```

## E. Phần báo cáo của bạn
- Hình thức hóa bài toán (state, action, transition, goal, cost, heuristic, tránh trạng thái lặp).
- Mô tả UCS và A*, hàm chi phí, chứng minh heuristic.
- Toàn bộ phần **Experiments** (bảng, biểu đồ, nhận xét).
- Tổng hợp, kiểm tra định dạng và gộp báo cáo cuối.

## F. Mốc thời gian

| Tuần | Việc |
|------|------|
| 1 | Chốt giao diện trạng thái, tạo repo + Issues, thiết kế chi phí và heuristic trên giấy, UCS ban đầu |
| 2 | Hoàn thiện UCS, A*, tạo bộ test, nối solver vào API |
| 3 | Chạy benchmark, vẽ biểu đồ, viết báo cáo, kiểm tra nộp |

## G. Định nghĩa "xong"
- UCS và A* chạy đúng trên cả 4 nhóm màn, A* cùng chi phí với UCS.
- Bộ test cố định và file CSV kết quả nằm trong repo.
- Phần chứng minh heuristic đọc lại không có chỗ hở.

## H. Câu hỏi phỏng vấn nên chuẩn bị
- Tại sao UCS của nhóm khác BFS? Hàm chi phí chọn vì sao?
- Heuristic của nhóm có admissible không? Nếu đổi hàm chi phí thì sao?
- Trạng thái gồm những gì, tại sao phải có tình trạng cầu?
