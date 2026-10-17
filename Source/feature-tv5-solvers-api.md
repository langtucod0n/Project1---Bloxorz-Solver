# feature/tv5-solvers-api

Tài liệu này mô tả những phần đã triển khai trên branch `feature/tv5-solvers-api` (TV5: thuật toán tìm kiếm không thông tin, module đo đạc). Các solver chỉ dùng giao diện `Game` của core engine (xem `README_CORE.md`), không sửa gì trong `game/`.

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
python -m pytest -q                    # toàn bộ 79 test
python -m pytest tests/test_bfs.py -v  # BFS
python -m pytest tests/test_dfs.py -v  # DFS
python -m pytest tests/test_metrics.py -v  # metrics
```

Các test bao quát: giải được cả 5 màn tích hợp sẵn, lời giải phát lại đúng bằng `Game.result` và kết thúc ở ô đích, màn không có lời giải vẫn dừng, BFS cho lời giải ngắn nhất, `max_depth` của DFS, cấu trúc kết quả và bộ nhớ đỉnh của `run_solver`.

## Trạng thái xác minh hiện tại

- 79 bài kiểm thử pytest vượt qua;
- BFS và DFS đều giải được cả 5 màn L01–L05;
- lời giải DFS không bao giờ ngắn hơn lời giải BFS.

## Chưa triển khai

- API backend (`server/app.py`);
- đóng gói (`main.py`, `requirements.txt`, README chạy dự án);
- video demo;
- các solver UCS và A* (thuộc TV1).
