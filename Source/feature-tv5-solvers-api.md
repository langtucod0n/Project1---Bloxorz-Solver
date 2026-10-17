# feature/tv5-solvers-api

Tài liệu này mô tả những phần đã triển khai trên branch `feature/tv5-solvers-api` (TV5: thuật toán tìm kiếm không thông tin, module đo đạc, API backend, đóng gói). Các solver chỉ dùng giao diện `Game` của core engine (xem `README_CORE.md`), không sửa gì trong `game/`.

## Các tính năng đã triển khai

### Module đo đạc

`solvers/metrics.py` cung cấp hàm `run_solver(solver, game)` dùng chung cho mọi solver.

Quy ước solver: `solver(game) -> {"moves": list[str] | None, "expanded": int}`, trong đó `moves` là `None` nếu màn không có lời giải và `expanded` là số node được lấy ra để mở rộng.

`run_solver` bọc solver và trả về cấu trúc kết quả thống nhất:

| Trường | Ý nghĩa |
|---|---|
| `moves` | Danh sách nước đi của lời giải, `None` nếu không có lời giải |
| `expanded` | Số node đã mở rộng |
| `time` | Thời gian tìm kiếm (giây), đo bằng `time.perf_counter` |
| `peak_memory` | Bộ nhớ đỉnh (byte), đo bằng `tracemalloc` |
| `length` | Số nước đi của lời giải, `None` nếu không có lời giải |

Vì `tracemalloc` làm chương trình chậm đáng kể, thời gian và bộ nhớ được đo ở **hai lần chạy riêng** để thời gian không bị méo.

### BFS

`solvers/bfs.py` triển khai tìm kiếm theo chiều rộng bằng `collections.deque`. Một từ điển `parent` đóng vai trò đồng thời là tập `visited` và là nơi lưu cha của mỗi trạng thái để dựng lại đường đi. BFS cho lời giải **ngắn nhất theo số nước đi**.

### DFS

`solvers/dfs.py` triển khai tìm kiếm theo chiều sâu:

- dùng stack tự tạo, **không đệ quy**, nên không tràn stack;
- có tập `visited` nên không lặp vô hạn;
- tham số tùy chọn `max_depth` (mặc định không giới hạn) dùng để cắt nhánh quá sâu;
- đẩy các hành động theo thứ tự ngược để nước đầu tiên theo thứ tự `U, D, L, R` được thử trước.

DFS thường cho lời giải dài và không tối ưu. Lựa chọn DFS (thay vì IDS) cần được ghi rõ trong báo cáo.

### API backend

`server/app.py` (FastAPI) là cầu nối giữa giao diện 3D và Python. Máy chủ chỉ gọi vào `game/` và `solvers/`, không chứa luật chơi.

- `GET /api/levels`, `POST /api/load`, `POST /api/move`, `POST /api/solve`, `POST /api/switch_control`. Định dạng chi tiết nằm trong `README.md`.
- `solvers/registry.py` ánh xạ tên thuật toán (`bfs`, `dfs`, `ucs`, `astar`) sang solver. UCS và A* của TV1 được nạp lười từ `solvers/ucs.py` và `solvers/astar.py`; chưa có file thì API trả 501.
- `/api/move` trả trạng thái thô khi khối rơi (`status = LOST`) để giao diện vẽ hoạt ảnh; ván giữ nguyên ở vị trí trước.
- `level_id` chỉ chấp nhận tên file màn, chặn đường dẫn kiểu `../`.
- Xử lý lỗi bằng mã HTTP: 400, 404, 409, 422, 500, 501, 504.

`server/runner.py` chạy mỗi lần giải trong một **tiến trình riêng** (`multiprocessing`, chế độ `spawn`). Khi quá thời gian (mặc định 10 giây, đổi bằng `BLOXORZ_SOLVE_TIMEOUT` hoặc tham số `timeout` của request) tiến trình bị dừng hẳn và API trả 504, nên máy chủ không bị treo trên màn quá khó.

### Đóng gói

`main.py` khởi động máy chủ bằng uvicorn và tự mở trình duyệt. Nếu cổng bị chiếm thì báo và gợi ý `--port` khác. Nếu `web/index.html` tồn tại thì được phục vụ tại `/`. Script ép stdout sang UTF-8 vì console Windows (cp1252) không in được tiếng Việt. `README.md` hướng dẫn chạy dự án bằng đúng hai lệnh `pip install -r requirements.txt` và `python main.py`.

## So sánh BFS và DFS trên các màn có sẵn

Độ dài lời giải và số node mở rộng:

| Màn | BFS | DFS |
|---|---|---|
| L01 | 3 nước, 10 node | 15 nước, 25 node |
| L02 | 2 nước, 3 node | 2 nước, 3 node |
| L03 | 6 nước, 20 node | 7 nước, 11 node |
| L04 | 7 nước, 51 node | 16 nước, 20 node |
| L05 | 8 nước, 47 node | 24 nước, 32 node |

DFS cho lời giải dài hơn rõ rệt nhưng thường mở rộng ít node hơn.

## Chạy kiểm thử

Từ thư mục `Source`:

```bash
pip install -r requirements.txt
python -m pytest -q                    # toàn bộ 94 test
python -m pytest tests/test_bfs.py -v  # BFS
python -m pytest tests/test_dfs.py -v  # DFS
python -m pytest tests/test_metrics.py -v  # metrics
python -m pytest tests/test_api.py -v  # API
```

Các test bao quát: giải được cả 5 màn tích hợp sẵn, lời giải phát lại đúng bằng `Game.result` và kết thúc ở ô đích, màn không có lời giải vẫn dừng, BFS cho lời giải ngắn nhất, `max_depth` của DFS, cấu trúc kết quả và bộ nhớ đỉnh của `run_solver`, các endpoint API (nạp màn, đi một nước, thắng/thua, màn không tồn tại, hướng sai, timeout 504).

## Trạng thái xác minh hiện tại

- 94 bài kiểm thử pytest vượt qua;
- đã chạy thật `python main.py` và gọi `/api/levels`, `/api/solve` bằng curl; cổng bị chiếm được báo đúng;
- BFS và DFS đều giải được cả 5 màn L01–L05;
- lời giải DFS không bao giờ ngắn hơn lời giải BFS.

## Chưa triển khai

- `POST /api/switch_control` trả 501 vì `Game` chưa có cơ chế tách khối (TV3);
- UCS và A* (TV1): API sẽ tự dùng khi có `solvers/ucs.py` (hàm `ucs`) và `solvers/astar.py` (hàm `astar`) dạng `solver(game) -> {"moves", "expanded"}`;
- chưa thử trên máy sạch và chưa có giao diện `web/` (TV4);
- video demo (kịch bản nháp ở `docs/video_script.md`).
