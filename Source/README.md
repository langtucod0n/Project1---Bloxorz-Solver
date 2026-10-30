# Bloxorz Solver — Hướng dẫn chạy mã nguồn

## Yêu cầu hệ thống

| Thành phần | Phiên bản tối thiểu |
|---|---|
| Python | 3.12+ |
| Hệ điều hành | Windows / macOS / Linux |
| Trình duyệt | Chrome, Edge, Firefox (hỗ trợ WebGL) |

## 1. Cài đặt

### 1.1. Tạo môi trường ảo (khuyến nghị)

```bash
cd Source
python -m venv .venv
```

Kích hoạt môi trường ảo:

- **Windows (PowerShell)**:
  ```powershell
  .venv\Scripts\Activate.ps1
  ```
- **Windows (CMD)**:
  ```cmd
  .venv\Scripts\activate.bat
  ```
- **macOS / Linux**:
  ```bash
  source .venv/bin/activate
  ```

### 1.2. Cài đặt thư viện

```bash
pip install -r requirements.txt
```

Các thư viện cần thiết:

| Thư viện | Mục đích |
|---|---|
| `fastapi` | API backend |
| `uvicorn` | Máy chủ ASGI |
| `httpx` | HTTP client (dùng trong test) |
| `pytest` | Chạy unit test |
| `matplotlib` | Vẽ biểu đồ benchmark |

## 2. Chạy ứng dụng web (GUI 3D)

Từ thư mục `Source`, chạy:

```bash
python main.py
```

Trình duyệt sẽ tự mở tại `http://127.0.0.1:8000/`. Giao diện 3D cho phép:
- Chọn màn chơi (L01 – L16)
- Chơi thủ công bằng phím mũi tên
- Chọn thuật toán giải tự động và xem hoạt ảnh lời giải

### Tuỳ chọn dòng lệnh

| Tham số | Mô tả | Mặc định |
|---|---|---|
| `--host` | Địa chỉ IP | `127.0.0.1` |
| `--port` | Cổng | `8000` |
| `--no-browser` | Không tự mở trình duyệt | Tắt |

Ví dụ chạy trên cổng khác:

```bash
python main.py --port 9000
```

## 3. Chạy unit test

```bash
python -m pytest -v
```

Chạy riêng các test liên quan đến heuristic:

```bash
python -m pytest -v -k "heuristic or combined or consistent"
```

## 4. Chạy benchmark

So sánh hiệu năng tất cả thuật toán (BFS, DFS, IDS, UCS, A*) trên 16 màn:

```bash
python -m benchmark.run_all
```

Kết quả được ghi vào `benchmark/results.csv`. Để vẽ biểu đồ từ kết quả:

```bash
python -m benchmark.plot
```

## 5. Cấu trúc thư mục

```
Source/
├── main.py              # Điểm vào chính — khởi động server
├── requirements.txt     # Danh sách thư viện
├── pytest.ini           # Cấu hình pytest
│
├── game/                # Luật chơi Bloxorz
│   ├── game.py          #   Lớp Game: trạng thái, hành động, kết quả
│   ├── state.py         #   State, hằng số orientation, bảng chuyển đổi
│   └── level_loader.py  #   Đọc và kiểm tra file màn chơi JSON
│
├── solvers/             # Các thuật toán tìm kiếm
│   ├── bfs.py           #   Breadth-First Search
│   ├── dfs.py           #   Depth-First Search
│   ├── ids.py           #   Iterative Deepening Search
│   ├── ucs.py           #   Uniform-Cost Search
│   ├── astar.py         #   A* Search
│   ├── heuristics.py    #   Hàm heuristic (Manhattan/2, combined)
│   ├── costs.py         #   Hàm chi phí (có phụ thu fragile)
│   ├── metrics.py       #   Đo thời gian, bộ nhớ, số node mở rộng
│   ├── registry.py      #   Bảng tên thuật toán → hàm solver
│   ├── loader.py        #   Hàm tiện ích nạp màn chơi
│   └── game_access.py   #   Lớp trung gian truy cập Game
│
├── server/              # API backend
│   ├── app.py           #   FastAPI endpoints
│   └── runner.py        #   Chạy solver có giới hạn thời gian
│
├── web/                 # Giao diện 3D (frontend)
│   ├── index.html
│   ├── style.css
│   ├── main.js
│   ├── scene.js         #   Render 3D bằng Three.js
│   └── api.js           #   Gọi API từ frontend
│
├── levels/              # Dữ liệu 16 màn chơi (JSON)
│   ├── L01.json … L16.json
│
├── tests/               # Unit test
│
├── benchmark/           # Benchmark & biểu đồ
│   ├── run_all.py
│   ├── plot.py
│   └── results.csv
│
└── tools/               # Script tiện ích
```

## 6. Các thuật toán giải

| Thuật toán | Tên trong API | Tối ưu? | Ghi chú |
|---|---|---|---|
| BFS | `bfs` | ✅ (chi phí đồng nhất) | Cơ bản |
| DFS | `dfs` | ❌ | Dùng làm mốc so sánh |
| IDS | `ids` | ✅ (chi phí đồng nhất) | Tiết kiệm bộ nhớ hơn BFS |
| UCS | `ucs` | ✅ | Tối ưu với chi phí không đồng nhất |
| A* | `astar` | ✅ | Heuristic dẫn đường, nhanh nhất |

## 7. API endpoints

Tài liệu API tương tác có tại `http://127.0.0.1:8000/docs` (Swagger UI) khi server đang chạy.

| Phương thức | Đường dẫn | Mô tả |
|---|---|---|
| `GET` | `/api/levels` | Danh sách các màn chơi |
| `POST` | `/api/load` | Nạp một màn chơi |
| `POST` | `/api/move` | Di chuyển khối (U/D/L/R) |
| `POST` | `/api/switch_control` | Đổi cube điều khiển (khi khối tách) |
| `POST` | `/api/solve` | Giải tự động bằng thuật toán chỉ định |

## 8. Xử lý sự cố

| Vấn đề | Giải pháp |
|---|---|
| `Cổng 8000 đang bị chiếm` | Chạy `python main.py --port 8001` |
| `ModuleNotFoundError` | Kiểm tra đã kích hoạt venv và `pip install -r requirements.txt` |
| Trình duyệt không tự mở | Truy cập thủ công `http://127.0.0.1:8000/` |
| Lỗi encoding tiếng Việt trên Windows | Chạy `chcp 65001` trong CMD trước khi chạy lệnh |
