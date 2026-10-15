# Bloxorz Solver Core

Thư mục này chứa engine trò chơi cốt lõi (core game engine) và các bài kiểm thử xác thực (validation tests) cho dự án bộ giải đố Bloxorz (Bloxorz solver).

## Các tính năng đã triển khai

### Mô hình trạng thái trò chơi

`game/state.py` định nghĩa đối tượng giá trị (value object) `State` bất biến (immutable) và ba hướng của khối:

- `STANDING` (Đứng): khối chiếm một ô.
- `LYING_H` (Nằm ngang): khối chiếm hai ô theo chiều ngang.
- `LYING_V` (Nằm dọc): khối chiếm hai ô theo chiều dọc.

Bảng di chuyển (movement table) hoàn chỉnh gồm 12 trạng thái được tập trung tại `TRANSITIONS`. Hàm hỗ trợ `cells()` chuyển đổi một hướng và tọa độ neo (anchor coordinate) thành các ô mà khối đang chiếm giữ. Các đối tượng trạng thái vẫn duy trì tính chất có thể băm (hashable), do đó chúng có thể được sử dụng trong tập hợp các trạng thái đã duyệt (visited-state set) được duy trì bởi một thuật toán tìm kiếm.

Quá trình tuần tự hóa (serialization) trạng thái được cung cấp bởi `state_to_dict()` và `state_from_dict()`. Siêu dữ liệu về trạng thái tách khối (split-state metadata) được bảo toàn trong suốt quá trình chuyển đổi qua lại với JSON (JSON round-tripping), trong khi chỉ các cặp tọa độ được sử dụng để lưu trữ vị trí chiếm dụng trên bảng (board occupancy).

### Luật chơi

`game/game.py` cung cấp giao diện trò chơi dành cho bộ giải (solver-facing interface):

- `initial_state()` tạo trạng thái bắt đầu.
- `actions(state)` chỉ trả về các hành động hợp lệ (legal actions) theo một thứ tự tất định (deterministic) là `U` (Lên), `D` (Xuống), `L` (Trái), `R` (Phải).
- `result(state, action)` áp dụng một nước đi hợp lệ mà không làm thay đổi (mutating) đầu vào.
- `is_goal(state)` kiểm tra xem khối có đang đứng thẳng trên đích đến (goal) hay không.
- `cost(state, action, next_state)` trả về chi phí của một bước di chuyển đơn vị.

Phương thức `step()` dành cho chế độ chơi thủ công (manual-play) cũng trả về trạng thái kết quả thô khi khối bị rơi, cho phép giao diện người dùng kết xuất (render) hoạt ảnh khối rơi xuống.

Engine xử lý các vấn đề sau:

- ranh giới bảng và các ô hổng (void cells);
- các ô dễ vỡ (fragile cells), chỉ gây nguy hiểm khi khối đứng thẳng trên đó;
- điều kiện chiến thắng: chỉ khi khối đứng thẳng trên đích đến;
- các hành động không hợp lệ và các nước đi dẫn đến việc khối bị rơi.

### Tải màn chơi

`game/level_loader.py` xác thực và tải các màn chơi định dạng JSON. Quá trình xác thực kiểm tra:

- các trường bắt buộc gồm `grid` (lưới), `start` (điểm bắt đầu) và `legend` (chú giải);
- lưới phải có dạng hình chữ nhật và không được để trống;
- các ký hiệu trên lưới đã được định nghĩa (known grid symbols);
- có chính xác một đích đến;
- tọa độ bắt đầu nằm bên trong bảng;
- ô bắt đầu không phải là ô hổng cũng không phải là ô dễ vỡ.

Các khóa bổ sung của màn chơi (level keys) như `switches` (công tắc) và `bridges` (cây cầu) được giữ lại để phát triển các cơ chế (mechanics) trong tương lai.

### Tiện ích giải đố và các màn chơi

`tools/check_levels.py` chứa một tiện ích tìm kiếm theo chiều rộng (breadth-first search). Nó sử dụng giao diện trò chơi để tìm ra lời giải ngắn nhất (tính theo số nước đi) và có thể xác minh tất cả các màn chơi được tích hợp sẵn (bundled levels) từ dòng lệnh.

Các màn chơi mẫu hiện tại được lưu trữ trong thư mục `levels/`:

- `L01.json`
- `L02.json`
- `L03.json`
- `L04.json`
- `L05.json`

## Chạy dự án

Từ thư mục gốc của kho lưu trữ (repository root):

```bash
cd Source
(Tạo môi trường ảo
python -m venv env
hoặc python3 -m venv env
source env/bin/activate)
pip install -r requirements.txt
python -m pytest -q (cho toàn bộ 48 test)
hoặc python -m pytest test/test_orientation.py -v (unit test 12 trạng thái)
hoặc python -m tools.check_levels (test nạp các màn từ .json)
```


Bộ kiểm thử (test suite) bao quát việc chuyển đổi hướng, tính có thể đảo ngược (reversibility), các nước đi hợp lệ, các ô dễ vỡ và ô hổng, các trạng thái thắng/thua, tính bất biến (immutability) và khả năng băm (hashing) của trạng thái, tuần tự hóa JSON, xác thực màn chơi, và việc giải quyết tất cả các màn chơi được tích hợp sẵn.

## Trạng thái xác minh hiện tại

Bản triển khai đã được xác minh bằng:
- 12 bài test orientation vượt qua;
- 48 bài kiểm thử pytest vượt qua;
- quá trình biên dịch Python thành công;
- toàn bộ 5 màn chơi tích hợp sẵn đều được giải quyết bằng thuật toán tìm kiếm theo chiều rộng.

## Quy tắc dọn dẹp kho lưu trữ (Repository hygiene)

Không commit môi trường ảo cục bộ, bộ nhớ cache của pytest, hay Python bytecode. Đây là những tệp được sinh tự động hoặc đặc thù cho từng máy. Thay vào đó, hãy commit các tệp mã nguồn, bài kiểm thử, màn chơi JSON, tài liệu và các siêu dữ liệu về thư viện phụ thuộc (dependency metadata).