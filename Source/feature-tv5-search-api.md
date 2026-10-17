# feature/tv5-search-api

Tài liệu này mô tả những gì đã làm trên branch `feature/tv5-search-api` (phần việc của TV5). Nội dung chia theo các mục A1 đến A6 trong file nhiệm vụ để dễ đối chiếu. Các phần ở đây chỉ dùng luật chơi có sẵn trong `game/`, không sửa gì trong đó (xem `README_CORE.md`).

## A1. BFS (tìm theo từng lớp)

File `solvers/bfs.py`. Thuật toán thử hết các nước đi một bước, rồi hai bước, rồi ba bước... nên lời giải tìm được luôn **ngắn nhất**.

- Dùng `collections.deque` làm hàng chờ.
- Ghi nhớ các trạng thái đã đi qua để không đi lại, và nhớ trạng thái đứng trước để dựng lại đường đi.
- Trả về các nước đi của lời giải (hoặc `None` nếu màn không giải được) và số trạng thái đã xem xét.
- Dùng thẳng trạng thái của TV2 để ghi nhớ, không cần sửa gì.

Cả 5 màn L01 đến L05 đều giải được.

## A2. DFS (đi sâu hết mức rồi mới quay lại)

File `solvers/dfs.py`. Thuật toán đi theo một hướng đến khi hết đường mới quay lại thử hướng khác.

- Nhóm chọn DFS, không chọn IDS. Lý do: DFS cho lời giải khác BFS rõ rệt nên so sánh giữa hai thuật toán có ý nghĩa, còn IDS cho kết quả gần như trùng BFS.
- Ghi nhớ trạng thái đã đi qua nên không bị lặp mãi.
- Không dùng hàm tự gọi lại chính nó mà dùng ngăn xếp tự tạo, nên không bị lỗi tràn bộ nhớ.
- Có thể đặt giới hạn độ sâu bằng `max_depth`. Mặc định là không giới hạn.

Lời giải của DFS thường dài và không tối ưu. So sánh trên 5 màn có sẵn (số nước của lời giải, số trạng thái đã xem xét):

| Màn | BFS | DFS |
|---|---|---|
| L01 | 3 nước, 10 trạng thái | 15 nước, 25 trạng thái |
| L02 | 2 nước, 3 trạng thái | 2 nước, 3 trạng thái |
| L03 | 6 nước, 20 trạng thái | 7 nước, 11 trạng thái |
| L04 | 7 nước, 51 trạng thái | 16 nước, 20 trạng thái |
| L05 | 8 nước, 47 trạng thái | 24 nước, 32 trạng thái |

DFS cho lời giải dài hơn nhiều (ví dụ L01: 15 nước so với 3 nước) nhưng thường xem xét ít trạng thái hơn.

## A3. Đo kết quả của thuật toán

File `solvers/metrics.py`. Hàm `run_solver(solver, game)` chạy một thuật toán rồi trả về cùng một bảng số liệu, dùng được cho mọi thuật toán:

| Mục | Ý nghĩa |
|---|---|
| `moves` | Các nước đi của lời giải. Là `None` nếu màn không giải được |
| `expanded` | Số trạng thái đã xem xét |
| `time` | Thời gian giải (giây), đo bằng `time.perf_counter` |
| `peak_memory` | Bộ nhớ dùng nhiều nhất (byte), đo bằng `tracemalloc` |
| `length` | Số nước đi của lời giải |

Mỗi thuật toán chỉ cần trả về `{"moves": ..., "expanded": ...}`, phần còn lại do `run_solver` tính. Thời gian và bộ nhớ được đo ở hai lần chạy riêng, vì đo bộ nhớ làm chương trình chạy chậm đi, nếu đo cùng lúc thì thời gian sẽ sai.

## A4. Máy chủ trung gian (API)

Các file `server/app.py`, `server/runner.py`, `solvers/registry.py`. Máy chủ dùng FastAPI, là cầu nối giữa giao diện 3D và phần Python. Giao diện gửi yêu cầu đến đây, máy chủ gọi luật chơi và các thuật toán rồi trả kết quả. Máy chủ không tự chứa luật chơi.

| Yêu cầu | Việc làm |
|---|---|
| `GET /api/levels` | Lấy danh sách màn |
| `POST /api/load` | Mở một màn, trả về bàn chơi và vị trí khối ban đầu |
| `POST /api/move` | Đi một nước (`U`, `D`, `L`, `R`), trả về vị trí mới và đang chơi, thắng hay thua |
| `POST /api/solve` | Cho máy tự giải bằng `bfs` hoặc `dfs`, trả về lời giải và bảng số liệu |
| `POST /api/switch_control` | Đổi khối điều khiển. Chưa dùng được, hiện trả lỗi 501 |

Một số điểm cần biết:

- Khi khối rơi, `/api/move` vẫn trả về vị trí lúc rơi để giao diện vẽ khối rơi. Ván chơi vẫn giữ ở vị trí trước đó.
- Tên màn chỉ được là tên file màn, để không ai truy cập được file khác trên máy.
- Khi có lỗi, máy chủ trả mã lỗi rõ ràng để giao diện hiện thông báo: 400 (gửi sai hướng hoặc sai tên thuật toán), 404 (không có màn đó), 409 (chưa mở màn hoặc ván đã xong), 422 (dữ liệu gửi sai dạng), 500 (thuật toán bị lỗi), 501 (chưa làm), 504 (giải quá lâu).
- Mỗi lần giải chạy trong một chương trình riêng. Quá 10 giây thì chương trình đó bị tắt hẳn và máy chủ trả lỗi 504, nên máy chủ không bị đứng khi gặp màn quá khó. Đổi thời gian bằng biến `BLOXORZ_SOLVE_TIMEOUT` hoặc thêm `timeout` vào yêu cầu giải.
- `solvers/registry.py` ghi tên từng thuật toán. UCS và A* của TV1 sẽ tự được dùng khi có file `solvers/ucs.py` (hàm `ucs`) và `solvers/astar.py` (hàm `astar`), dạng `solver(game) -> {"moves", "expanded"}`. Chưa có thì `/api/solve` với hai tên này trả lỗi 501.
- Định dạng trạng thái trả về đang theo `docs/example_state.json` của TV2.

## A5. Đóng gói và chạy

Các file `main.py`, `requirements.txt`, `README.md`.

- `main.py` bật máy chủ và tự mở trình duyệt. Nếu cổng đang bị dùng thì báo và gợi ý đổi cổng bằng `--port`. Nếu có file `web/index.html` thì máy chủ hiển thị luôn giao diện đó.
- `main.py` bắt in chữ theo kiểu UTF-8 vì cửa sổ lệnh Windows mặc định không in được tiếng Việt.
- `requirements.txt` ghi fastapi, uvicorn, httpx, pytest.
- `README.md` hướng dẫn chạy chỉ bằng hai lệnh `pip install -r requirements.txt` và `python main.py`, kèm cấu trúc thư mục và cách xử lý khi cổng bị chiếm.
- Đã thử trên môi trường ảo mới: lấy bản sạch của branch, cài bằng `pip install -r requirements.txt`, chạy `python main.py`. Toàn bộ bài kiểm tra đạt, `/api/levels`, `/api/solve` và `/docs` trả kết quả đúng.

## A6. Video demo

File `docs/video_script.md` là kịch bản nháp, gồm hai phần theo đề: giao diện và tính năng. Video chưa được quay.

## Kiến trúc backend và link video (cho mục B)

### Giao diện nói chuyện với Python qua đâu

Giao diện 3D chạy trong trình duyệt (JavaScript), còn luật chơi và thuật toán nằm trong Python. Hai bên nói chuyện với nhau qua **máy chủ web FastAPI** bằng các yêu cầu HTTP, dữ liệu gửi đi và nhận về đều ở dạng JSON.

```
Trình duyệt (giao diện 3D, web/)
        |  yêu cầu HTTP + JSON  (/api/load, /api/move, /api/solve ...)
        v
Máy chủ FastAPI (server/app.py)
        |  gọi hàm Python
        v
game/  (luật chơi)      solvers/  (BFS, DFS, đo kết quả; UCS, A* của TV1)
```

- Luật chơi và thuật toán chỉ nằm trong Python. Giao diện không tự tính nước đi, mỗi lần đi một nước nó hỏi máy chủ và vẽ lại theo trạng thái nhận về.
- Máy chủ chỉ làm trung gian: nhận yêu cầu, gọi `game/` và `solvers/`, đổi kết quả sang JSON, báo lỗi bằng mã HTTP.
- Mỗi lần giải chạy trong một chương trình riêng có giới hạn thời gian, nên một màn quá khó không làm đứng cả máy chủ.
- `main.py` bật máy chủ, đồng thời phục vụ luôn các file giao diện trong `web/` nên chỉ cần một lệnh để chạy cả hai.
- Trạng thái ván chơi hiện được giữ trong bộ nhớ của máy chủ (một ván tại một thời điểm), phù hợp với việc một người chơi và một trình duyệt.

Phần này cần TV4 xem lại, vì điểm nối giữa giao diện và máy chủ là điểm chung của hai người.

### Link video

Chưa có, vì video chưa được quay. Sau khi đăng lên YouTube, điền link vào đây: _(chưa có)_

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

Các bài kiểm tra xem:

- Cả 5 màn có sẵn đều giải được, và đi theo lời giải thì thật sự đến được đích.
- Màn không giải được thì thuật toán vẫn dừng.
- BFS luôn cho lời giải ngắn nhất, DFS không bao giờ ngắn hơn BFS.
- `max_depth` của DFS cắt đúng.
- Bảng số liệu của `run_solver` đủ mục và đúng.
- Máy chủ: mở màn, đi một nước, thắng, thua, màn không có, hướng sai, giải quá giờ.

## Trạng thái kiểm tra hiện tại

- 94 bài kiểm tra đều đạt.
- BFS và DFS đều giải được cả 5 màn L01 đến L05.
- Đã chạy thật `python main.py` và gọi thử bằng curl, kể cả trong môi trường ảo mới. Khi cổng bị dùng, chương trình báo đúng.
- Mới thử trên máy Windows của TV5, chưa thử trên máy khác.

## Chưa làm

- UCS và A* trong `/api/solve`: chờ TV1 thêm `solvers/ucs.py` và `solvers/astar.py`.
- `POST /api/switch_control`: chờ TV3 làm cơ chế tách khối.
- Chốt định dạng JSON của trạng thái với TV2, TV3, TV4 và nhóm trưởng.
- Nối với giao diện 3D trong `web/` (TV4) và thử cùng nhau.
- Thêm matplotlib vào `requirements.txt` (TV1 thêm khi cần).
- Gửi bảng kết quả của `run_solver` cho TV1 và TV4.
- Quay và đăng video demo.
