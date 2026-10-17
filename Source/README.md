# Bloxorz Solver

Trò chơi Bloxorz kèm các thuật toán tìm kiếm (BFS, DFS, UCS, A*) và giao diện 3D chạy trên trình duyệt.

## Chạy dự án

Từ thư mục `Source`:

```bash
pip install -r requirements.txt
python main.py
```

Máy chủ chạy tại http://127.0.0.1:8000/ và tự mở trình duyệt. Tài liệu API tương tác ở `/docs`.

Tùy chọn của `main.py`:

| Tùy chọn | Ý nghĩa |
|---|---|
| `--port 8001` | Đổi cổng. Nếu cổng 8000 bị chiếm, chương trình sẽ báo và gợi ý cổng khác |
| `--no-browser` | Không tự mở trình duyệt |
| `--host 0.0.0.0` | Cho máy khác trong mạng truy cập |

Đặt biến môi trường `BLOXORZ_SOLVE_TIMEOUT` (giây, mặc định 10) để đổi thời gian tối đa cho mỗi lần giải.

## Cấu trúc thư mục

```
Source/
├── main.py              khởi động máy chủ, mở trình duyệt
├── requirements.txt
├── game/                luật chơi (state, game, level_loader)
├── levels/              các màn chơi JSON
├── solvers/             bfs, dfs, metrics (đo đạc), registry (tên thuật toán -> solver)
├── server/              API FastAPI (app.py) và runner.py (chạy solver có giới hạn thời gian)
├── web/                 giao diện 3D (Three.js); có index.html thì được phục vụ tại "/"
├── tools/               tiện ích kiểm tra màn chơi
├── benchmark/           thực nghiệm so sánh thuật toán
├── docs/                ví dụ định dạng JSON
└── tests/               pytest
```

## API

| Endpoint | Body | Kết quả |
|---|---|---|
| `GET /api/levels` | | `{levels: ["L01", ...]}` |
| `POST /api/load` | `{level_id}` | `{level_id, level, state}` |
| `POST /api/move` | `{direction}` (`U`/`D`/`L`/`R`) | `{state, status}` với `status` là `PLAYING`, `WON` hoặc `LOST` |
| `POST /api/switch_control` | | Chưa hỗ trợ (501) |
| `POST /api/solve` | `{algorithm, level_id, timeout?}` | `{algorithm, level_id, solved, moves, metrics}` |

`algorithm` là `bfs`, `dfs`, `ucs` hoặc `astar`. `metrics` gồm `expanded`, `time` (giây), `peak_memory` (byte), `length`.

Mã lỗi: 400 (hướng hoặc thuật toán sai), 404 (màn không tồn tại), 409 (chưa nạp màn hoặc ván đã kết thúc), 422 (dữ liệu sai dạng), 500 (solver lỗi), 501 (chưa cài đặt), 504 (giải quá thời gian).

Khi đi vào ô hổng hoặc ô dễ vỡ, `/api/move` trả `status = LOST` cùng trạng thái thô để giao diện vẽ khối rơi; ván giữ nguyên ở vị trí trước đó.

## Kiểm thử

```bash
python -m pytest -q
```
