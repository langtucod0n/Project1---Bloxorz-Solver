# Kịch bản video demo (nháp)

Quay bằng OBS Studio, có phụ đề hoặc thuyết minh, đăng YouTube công khai, đưa link vào báo cáo. Quay thử một lần trước, quay bản cuối khi giao diện đã chốt.

## Phần 1: Giao diện (5đ)

1. Mở bằng `python main.py`, trình duyệt tự mở.
2. Chọn từng màn trong danh sách; chỉ rõ các loại ô: thường, hổng (void), đích (goal), dễ vỡ (fragile), công tắc, cầu.
3. Cho thấy khối ở ba tư thế: đứng, nằm ngang, nằm dọc.
4. Giới thiệu các nút điều khiển và các nút chọn thuật toán.

## Phần 2: Tính năng (5đ)

1. Chơi tay: lăn khối, bước lên công tắc để cầu hiện ra, thắng một màn.
2. Thua: lăn ra ngoài bàn và đứng lên ô dễ vỡ, thấy khối rơi.
3. Chạy lần lượt BFS, IDS, UCS, A* (DFS làm mốc so sánh) trên cùng một màn; mỗi lần phát lại lời giải.
4. So sánh số liệu: số node mở rộng, thời gian, bộ nhớ đỉnh, độ dài lời giải.
5. Một màn quá khó để cho thấy báo hết thời gian (504) thay vì treo máy.

## Cần chờ người khác trước khi quay

- Giao diện 3D (TV4), ô công tắc và cầu (TV3), UCS và A* (TV1).
