# feature/tv5-search-api

Báo cáo phần việc của TV5 trên branch `feature/tv5-search-api`, chia theo các mục A1 đến A6 trong file nhiệm vụ để dễ đối chiếu. Các phần ở đây chỉ dùng luật chơi có sẵn trong `game/`, không sửa gì trong đó (xem `README_CORE.md`).

Ký hiệu: `[x]` là đã xong, `[ ]` là chưa xong.

## Tổng quan

| Mục | Việc | Trạng thái |
|---|---|---|
| A1 | BFS | Xong |
| A2 | DFS | Xong |
| A3 | Đo kết quả của thuật toán | Xong |
| A4 | Máy chủ trung gian (API) | Làm được một phần, chờ TV1, TV3, TV4 |
| A5 | Đóng gói và chạy | Làm được một phần, chờ TV4 |
| A6 | Video demo | Chưa làm, chỉ có kịch bản nháp |

---

## A1. BFS (tìm theo từng lớp)

File: `solvers/bfs.py`, kiểm tra: `tests/test_bfs.py`.

- [x] Dùng `collections.deque` và nơi ghi nhớ các trạng thái đã đi qua.
- [x] Trả về các nước đi của lời giải (nếu có) và số trạng thái đã xem xét. Kèm bảng số liệu đầy đủ khi bọc bằng `run_solver` (mục A3).
- [x] Dùng thẳng trạng thái của TV2 để ghi nhớ, không cần sửa gì.

Cách hoạt động: thử hết các nước đi một bước, rồi hai bước, rồi ba bước... nên lời giải tìm được luôn **ngắn nhất**.

Kết quả: giải được cả 5 màn L01 đến L05.

## A2. DFS (đi sâu hết mức rồi mới quay lại)

File: `solvers/dfs.py`, kiểm tra: `tests/test_dfs.py`.

- [x] Chọn DFS (không chọn IDS). **Báo cáo chung của nhóm cần ghi rõ lựa chọn này.**
- [x] Ghi nhớ trạng thái đã đi qua nên không bị lặp mãi.
- [x] Không dùng hàm tự gọi lại chính nó mà dùng ngăn xếp tự tạo, nên không bị lỗi tràn bộ nhớ. Có thể đặt giới hạn độ sâu bằng `max_depth` (mặc định không giới hạn).
- [x] Nhận xét cho báo cáo: lời giải DFS thường dài và không tối ưu (xem bảng dưới).

So sánh BFS và DFS trên 5 màn có sẵn, gồm số nước của lời giải và số trạng thái đã xem xét:

| Màn | BFS | DFS |
|---|---|---|
| L01 | 3 nước, 10 trạng thái | 15 nước, 25 trạng thái |
| L02 | 2 nước, 3 trạng thái | 2 nước, 3 trạng thái |
| L03 | 6 nước, 20 trạng thái | 7 nước, 11 trạng thái |
| L04 | 7 nước, 51 trạng thái | 16 nước, 20 trạng thái |
| L05 | 8 nước, 47 trạng thái | 24 nước, 32 trạng thái |

DFS cho lời giải dài hơn nhiều nhưng thường xem xét ít trạng thái hơn.

## A3. Đo kết quả của thuật toán

File: `solvers/metrics.py`, kiểm tra: `tests/test_metrics.py`.

- [x] Hàm `run_solver(solver, game)` bọc quanh mỗi thuật toán và đo 4 số liệu:
  - Thời gian giải (`time.perf_counter`).
  - Bộ nhớ dùng nhiều nhất (`tracemalloc`).
  - Số trạng thái đã xem xét (đếm mỗi lần lấy một trạng thái ra để mở rộng).
  - Độ dài lời giải (số nước đi).
- [x] Mọi thuật toán trả về cùng một bảng:

| Mục | Ý nghĩa |
|---|---|
| `moves` | Các nước đi của lời giải. Là `None` nếu màn không giải được |
| `expanded` | Số trạng thái đã xem xét |
| `time` | Thời gian giải (giây) |
| `peak_memory` | Bộ nhớ dùng nhiều nhất (byte) |
| `length` | Số nước đi của lời giải |

- [ ] Gửi mẫu bảng này cho TV1 và TV4. Tin nhắn đã soạn, chưa gửi.

Mỗi thuật toán chỉ cần trả về `{"moves": ..., "expanded": ...}`, phần còn lại do `run_solver` tính. Thời gian và bộ nhớ được đo ở hai lần chạy riêng, vì đo bộ nhớ làm chương trình chạy chậm đi, nếu đo cùng lúc thì thời gian sẽ sai.

## A4. Máy chủ trung gian (API)

Các file: `server/app.py`, `server/runner.py`, `solvers/registry.py`, kiểm tra: `tests/test_api.py`.

- [x] Dùng FastAPI. Máy chủ chỉ gọi vào `game/` và `solvers/`, không tự chứa luật chơi.
- [ ] Chốt định dạng JSON của trạng thái cùng TV2, TV3, TV4 và nhóm trưởng. Hiện đang dùng định dạng trong `docs/example_state.json`, chưa có xác nhận của ai.

Các yêu cầu máy chủ nhận:

| Yêu cầu | Việc làm | Trạng thái |
|---|---|---|
| `GET /api/levels` | Lấy danh sách màn | [x] |
| `POST /api/load` | Mở một màn, trả về bàn chơi và vị trí khối ban đầu | [x] |
| `POST /api/move` | Đi một nước (`U`, `D`, `L`, `R`), trả về vị trí mới và đang chơi, thắng hay thua | [x] |
| `POST /api/solve` với `bfs`, `dfs` | Cho máy tự giải, trả về lời giải và bảng số liệu | [x] |
| `POST /api/solve` với `ucs`, `astar` | Như trên | [ ] chờ TV1, hiện trả lỗi 501 |
| `POST /api/switch_control` | Đổi khối điều khiển | [ ] chờ TV3, hiện trả lỗi 501 |

- [x] Xử lý lỗi rõ ràng, trả mã lỗi để giao diện hiện thông báo: 400 (gửi sai hướng hoặc sai tên thuật toán), 404 (không có màn đó), 409 (chưa mở màn hoặc ván đã xong), 422 (dữ liệu gửi sai dạng), 500 (thuật toán bị lỗi), 501 (chưa làm), 504 (giải quá lâu).
- [x] Giới hạn thời gian cho mỗi lần giải: mỗi lần giải chạy trong một chương trình riêng, quá 10 giây thì bị tắt hẳn và máy chủ trả lỗi 504, nên không bị đứng khi gặp màn quá khó. Đổi thời gian bằng biến `BLOXORZ_SOLVE_TIMEOUT` hoặc thêm `timeout` vào yêu cầu giải.

Một số điểm cần biết:

- Khi khối rơi, `/api/move` vẫn trả về vị trí lúc rơi để giao diện vẽ khối rơi. Ván chơi vẫn giữ ở vị trí trước đó.
- Tên màn chỉ được là tên file màn, để không ai truy cập được file khác trên máy.
- `solvers/registry.py` ghi tên từng thuật toán. UCS và A* của TV1 sẽ tự được dùng khi có file `solvers/ucs.py` (hàm `ucs`) và `solvers/astar.py` (hàm `astar`), dạng `solver(game) -> {"moves", "expanded"}`.
- [ ] Nối với giao diện của TV4 và thử cùng nhau. Chờ TV4.

## A5. Đóng gói và chạy

Các file: `main.py`, `requirements.txt`, `README.md`.

- [x] `main.py` bật máy chủ và tự mở trình duyệt. Nếu cổng đang bị dùng thì báo và gợi ý đổi cổng bằng `--port`. Nếu có file `web/index.html` thì máy chủ hiển thị luôn giao diện đó.
- [x] `requirements.txt` ghi fastapi, uvicorn, httpx, pytest. [ ] matplotlib chưa có, TV1 sẽ thêm khi cần.
- [x] `README.md` hướng dẫn chạy chỉ bằng hai lệnh `pip install -r requirements.txt` và `python main.py`, kèm cấu trúc thư mục và cách xử lý khi cổng bị chiếm.
- [ ] **Chưa thử chạy trên máy sạch** (máy khác hoặc môi trường ảo mới). Mới thử trên máy của TV5.

Lưu ý: `main.py` bắt in chữ theo kiểu UTF-8 vì cửa sổ lệnh Windows mặc định không in được tiếng Việt.

## A6. Video demo

File: `docs/video_script.md` (kịch bản nháp).

- [x] Viết kịch bản trước, gồm hai phần theo đề: giao diện (5đ) và tính năng (5đ).
- [ ] Quay màn hình bằng OBS Studio, có phụ đề hoặc thuyết minh.
- [ ] Đăng lên YouTube ở chế độ công khai, đưa link vào báo cáo.

Chưa quay được vì phải chờ giao diện của TV4, ô công tắc và cầu của TV3, UCS và A* của TV1.

---

## Chạy kiểm tra

Từ thư mục `Source`:

```bash
pip install -r requirements.txt
python -m pytest -q                        # chạy toàn bộ 94 bài kiểm tra
python -m pytest tests/test_bfs.py -v      # A1
python -m pytest tests/test_dfs.py -v      # A2
python -m pytest tests/test_metrics.py -v  # A3
python -m pytest tests/test_api.py -v      # A4
```

Đã kiểm tra:

- 94 bài kiểm tra đều đạt.
- BFS và DFS đều giải được cả 5 màn L01 đến L05, đi theo lời giải thì thật sự đến được đích.
- BFS luôn cho lời giải ngắn nhất, DFS không bao giờ ngắn hơn BFS.
- Đã chạy thật `python main.py` và gọi thử `/api/levels`, `/api/solve` bằng curl, kết quả đúng. Khi cổng bị dùng, chương trình báo đúng.
