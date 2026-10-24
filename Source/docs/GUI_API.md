# GUI_API – Giao diện 3D (TV4) nói chuyện với backend (TV5) như thế nào

**Nguyên tắc:** JavaScript chỉ vẽ. Luật chơi (`game/`) và thuật toán (`solvers/`) nằm ở Python.
Mỗi nước đi, giao diện gửi yêu cầu lên máy chủ rồi vẽ lại đúng trạng thái nhận về.

```
Phím / nút  ->  main.js  ->  api.js (fetch)  ->  FastAPI (server/app.py)  ->  game/, solvers/
                                  ^                                              |
                                  |   JSON: state, status, moves, metrics        |
                  scene.js (Three.js: vẽ + hoạt ảnh)  <-------------------------+
```

| File | Việc |
|------|------|
| `web/api.js` | Gọi `fetch()`, dịch JSON backend sang "mô hình vẽ" (`normLevel`, `normState`), báo lỗi dễ đọc |
| `web/scene.js` | Dựng ô, khối, cube; hoạt ảnh lăn, rơi, vỡ, chìm vào goal, cầu trượt, tách/ghép |
| `web/main.js` | Nối phím, nút, bảng số liệu, phát lại lời giải |

## Endpoint đang dùng

| Yêu cầu | Gửi | Nhận |
|---------|-----|------|
| `GET /api/levels` | – | `{"levels": ["L01", ...]}` |
| `POST /api/load` | `{"level_id": "L13"}` | `{"level_id", "level": {...JSON màn...}, "state": {...}}` (cũng dùng cho Restart / New Game) |
| `POST /api/move` | `{"direction": "U"\|"D"\|"L"\|"R"}` | `{"state": {...}, "status": "PLAYING"\|"WON"\|"LOST"}` |
| `POST /api/switch_control` | `{}` | như `/api/move`; chỉ hợp lệ khi khối đã tách đôi (hành động `S`) |
| `POST /api/solve` | `{"algorithm": "bfs"\|"dfs"\|"ids"\|"ucs"\|"astar", "level_id": "L13"}` | `{"solved", "moves": ["R","D",...,"S"], "metrics": {"expanded","time","peak_memory","length"}}` |

Đơn vị bảng số liệu trên giao diện: thời gian `time` (giây) đổi sang ms, `peak_memory` (byte) đổi sang KB.

## Trạng thái (`state`) giao diện đọc

```json
{ "orient": 0, "r": 0, "c": 5, "cells": [[0,5]], "bridges": 0,
  "split": [[0,5],[0,11],0], "status": "PLAYING" }
```

- `orient`: 0 đứng, 1 nằm ngang, 2 nằm dọc; `(r, c)` là ô neo.
- `bridges`: bitmask, bit `i` = 1 nghĩa là cầu `id=i` đang mở.
- `split`: `null` hoặc `[[r0,c0],[r1,c1],active]`; `active` là cube đang điều khiển.
- Khi `status = "LOST"`, backend trả **trạng thái thô** (đã lăn ra ngoài / lên ô hỏng). Giao diện vẽ khối rơi từ đó.
  Nếu cube / khối đứng trên ô `fragile` thì vẽ ô vỡ cùng khối, còn lại vẽ rơi khỏi sàn.

## Màn chơi (`level`) giao diện đọc

`grid` + `legend` (`floor|void|goal|fragile`), `bridges[].cells`, `switches[]`
(`type` = `soft|heavy|split`, `targets`, `split_to`). Ô cầu do `bridges[].cells` quyết định, ký tự trên `grid` bị bỏ qua.

## Lỗi hiển thị cho người chơi

| Mã | Ý nghĩa | Giao diện |
|----|---------|-----------|
| không kết nối được | máy chủ chưa chạy | thông báo đỏ: chạy `python main.py` rồi tải lại |
| 400 / 404 / 409 / 422 | sai hướng, không có màn, ván đã xong, dữ liệu sai dạng | thông báo đỏ lấy từ `detail` của backend |
| 501 | UCS / A* chưa có | thông báo "Thuật toán ... chưa được cài đặt." |
| 504 | giải quá thời gian | thông báo đỏ |

## Chưa có phía backend, cần báo nhóm

- Sự kiện hoạt ảnh (`cầu đổi`, `ô vỡ`, `tách`, `ghép`) chưa có trong `state_to_dict`; giao diện **tự suy ra** bằng cách so sánh trạng thái trước và sau (chỉ để vẽ, không tính luật).
- Địa chỉ khác `localhost:8000` (ví dụ Live Server cổng 5500): thêm `?api=http://127.0.0.1:8000` vào URL và bật CORS ở máy chủ.
