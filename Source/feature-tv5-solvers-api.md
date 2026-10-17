# feature/tv5-solvers-api

Tài liệu này ghi lại những gì đã làm trên branch `feature/tv5-solvers-api` (phần việc của TV5). Các phần ở đây chỉ dùng luật chơi có sẵn trong `game/`, không sửa gì trong đó (xem `README_CORE.md`).

## Đã làm được gì

### 1. Đo kết quả của thuật toán

File `solvers/metrics.py` có hàm `run_solver(solver, game)`. Hàm này chạy một thuật toán giải đố rồi trả về cùng một bảng số liệu, dùng được cho mọi thuật toán:

| Mục | Ý nghĩa |
|---|---|
| `moves` | Các nước đi của lời giải. Là `None` nếu màn không giải được |
| `expanded` | Số trạng thái thuật toán đã xem xét |
| `time` | Thời gian giải (giây) |
| `peak_memory` | Bộ nhớ dùng nhiều nhất (byte) |
| `length` | Số nước đi của lời giải |

Mỗi thuật toán chỉ cần trả về `{"moves": ..., "expanded": ...}`, phần còn lại do `run_solver` tính. Thời gian và bộ nhớ được đo ở hai lần chạy riêng, vì đo bộ nhớ làm chương trình chạy chậm đi, nếu đo cùng lúc thì thời gian sẽ sai.

### 2. BFS (tìm theo từng lớp)

File `solvers/bfs.py`. Thuật toán thử hết các nước đi một bước, rồi hai bước, rồi ba bước... nên lời giải tìm được luôn **ngắn nhất**. Nó ghi nhớ các trạng thái đã đi qua để không đi lại.

### 3. DFS (đi sâu hết mức rồi mới quay lại)

File `solvers/dfs.py`. Thuật toán đi theo một hướng đến khi hết đường mới quay lại thử hướng khác.

- Cũng ghi nhớ trạng thái đã đi qua nên không bị lặp mãi.
- Không dùng hàm tự gọi lại chính nó, nên không bị lỗi tràn bộ nhớ.
- Có thể đặt giới hạn độ sâu bằng `max_depth`. Mặc định là không giới hạn.
- Lời giải thường dài hơn mức cần thiết. Báo cáo cần ghi rõ nhóm chọn DFS (không chọn IDS).

### 4. Máy chủ trung gian (API)

File `server/app.py` là cầu nối giữa giao diện 3D và phần Python. Giao diện gửi yêu cầu đến đây, máy chủ gọi luật chơi và các thuật toán rồi trả kết quả. Máy chủ không tự chứa luật chơi.

| Yêu cầu | Việc làm |
|---|---|
| `GET /api/levels` | Lấy danh sách màn |
| `POST /api/load` | Mở một màn, trả về bàn chơi và vị trí khối ban đầu |
| `POST /api/move` | Đi một nước (`U`, `D`, `L`, `R`), trả về vị trí mới và đang chơi, thắng hay thua |
| `POST /api/solve` | Cho máy tự giải bằng `bfs`, `dfs`, `ucs` hoặc `astar`, trả về lời giải và bảng số liệu |
| `POST /api/switch_control` | Đổi khối điều khiển. Chưa dùng được, trả về lỗi 501 |

Một số điểm cần biết:

- Khi khối rơi, `/api/move` vẫn trả về vị trí lúc rơi để giao diện vẽ khối rơi. Ván chơi vẫn giữ ở vị trí trước đó.
- Tên màn chỉ được là tên file màn, để không ai truy cập được file khác trên máy.
- Khi có lỗi, máy chủ trả mã lỗi rõ ràng để giao diện hiện thông báo: 400 (gửi sai hướng hoặc sai tên thuật toán), 404 (không có màn đó), 409 (chưa mở màn hoặc ván đã xong), 422 (dữ liệu gửi sai dạng), 500 (thuật toán bị lỗi), 501 (chưa làm), 504 (giải quá lâu).
- File `solvers/registry.py` ghi tên từng thuật toán. UCS và A* của TV1 sẽ tự được dùng khi có file `solvers/ucs.py` (hàm `ucs`) và `solvers/astar.py` (hàm `astar`). Chưa có thì trả về lỗi 501.

### 5. Giới hạn thời gian giải

File `server/runner.py` cho mỗi lần giải chạy trong một chương trình riêng. Nếu quá thời gian (mặc định 10 giây), chương trình đó bị tắt hẳn và máy chủ trả lỗi 504, nên máy chủ không bị đứng khi gặp màn quá khó. Có thể đổi thời gian bằng biến `BLOXORZ_SOLVE_TIMEOUT` hoặc thêm `timeout` vào yêu cầu giải.

### 6. Cách chạy dự án

- `main.py` bật máy chủ và tự mở trình duyệt. Nếu cổng đang bị dùng thì báo và gợi ý đổi cổng bằng `--port`.
- Nếu có file `web/index.html` thì máy chủ hiển thị luôn giao diện đó.
- `main.py` bắt in chữ theo kiểu UTF-8 vì cửa sổ lệnh Windows mặc định không in được tiếng Việt.
- `README.md` hướng dẫn chạy chỉ bằng hai lệnh: `pip install -r requirements.txt` và `python main.py`.
- `docs/video_script.md` là kịch bản nháp cho video demo.

## So sánh BFS và DFS trên 5 màn có sẵn

Số nước của lời giải và số trạng thái đã xem xét:

| Màn | BFS | DFS |
|---|---|---|
| L01 | 3 nước, 10 trạng thái | 15 nước, 25 trạng thái |
| L02 | 2 nước, 3 trạng thái | 2 nước, 3 trạng thái |
| L03 | 6 nước, 20 trạng thái | 7 nước, 11 trạng thái |
| L04 | 7 nước, 51 trạng thái | 16 nước, 20 trạng thái |
| L05 | 8 nước, 47 trạng thái | 24 nước, 32 trạng thái |

DFS cho lời giải dài hơn nhiều nhưng thường xem xét ít trạng thái hơn.

## Chạy kiểm tra

Từ thư mục `Source`:

```bash
pip install -r requirements.txt
python -m pytest -q                        # chạy toàn bộ 94 bài kiểm tra
python -m pytest tests/test_bfs.py -v      # BFS
python -m pytest tests/test_dfs.py -v      # DFS
python -m pytest tests/test_metrics.py -v  # đo kết quả
python -m pytest tests/test_api.py -v      # máy chủ
```

Các bài kiểm tra xem:

- Cả 5 màn có sẵn đều giải được, và đi theo lời giải thì thật sự đến được đích.
- Màn không giải được thì thuật toán vẫn dừng.
- BFS luôn cho lời giải ngắn nhất, DFS không bao giờ ngắn hơn BFS.
- `max_depth` của DFS cắt đúng.
- Bảng số liệu của `run_solver` đủ mục và đúng.
- Máy chủ: mở màn, đi một nước, thắng, thua, màn không có, hướng sai, giải quá giờ.

## Đã kiểm tra những gì

- 94 bài kiểm tra đều đạt.
- BFS và DFS đều giải được cả 5 màn L01 đến L05.
- Đã chạy thật `python main.py` và gọi thử `/api/levels`, `/api/solve` bằng curl, kết quả đúng. Khi cổng bị dùng, chương trình báo đúng.

## Chưa làm

- `POST /api/switch_control` (đổi khối điều khiển): chờ TV3 làm cơ chế tách khối.
- UCS và A* (TV1): chờ TV1 thêm file, dạng `solver(game) -> {"moves", "expanded"}`.
- Giao diện 3D trong `web/` (TV4).
- Chưa thử chạy trên máy sạch.
- Quay video demo (kịch bản nháp ở `docs/video_script.md`).
