# TV3 — Đặc tả ô nâng cao (Fragile, Cầu, Công tắc, Tách/Ghép khối)

Tài liệu tham chiếu cho nhóm. **Đợt 1 chỉ cài:** fragile, cầu, soft, heavy, toggle/permanent. Các phần split, ghép, hành động `S`, sự kiện cho GUI chỉ được **ghi tài liệu**, chưa cài.

## A. Luật

### A1. Fragile
Khối *nằm* (1×2) đè lên ô `fragile` thì an toàn. Khối *đứng* (1×1 chạm sàn) trên ô `fragile` thì ô vỡ và khối rơi: nước đi đó bị coi là thua (`LOST`).

### A2. Cầu
Cầu đóng = `void`, cầu mở = `floor` thường (bất kể ký tự vẽ trên grid). Mỗi công tắc liên kết một hoặc nhiều cầu. Tình trạng cầu là **một phần của `State`**: cài bằng bitmask `int` `State.bridges`, bit `i` = 1 ⇔ cầu `id=i` đang mở. Đề gốc gợi ý "tuple bool"; nhóm chọn bitmask vì băm và so sánh nhanh, gọn hơn trong tập `visited`. Hai state cùng vị trí nhưng khác tình trạng cầu là **khác nhau**.

### A3. Ba loại công tắc
- **Soft**: kích hoạt khi bất kỳ phần nào của khối chạm ô công tắc, đứng hay nằm; cube đơn cũng kích hoạt được.
- **Heavy**: chỉ kích hoạt khi khối 1×1×2 *đứng*, không split. Nằm đè lên hoặc cube đơn đi qua thì không kích hoạt.
- **Split**: chỉ kích hoạt khi khối *đứng*, không split; khối dịch chuyển tới các vị trí định sẵn và tách thành 2 cube 1×1×1. *(Đợt 2, chưa cài; hiện chỉ validate JSON.)*

### A4. Hành vi công tắc
- **toggle**: mỗi lần kích hoạt đảo trạng thái các cầu liên kết.
- **permanent**: đặt cầu vào trạng thái cố định. Trong JSON là `open`/`close`; `"mode": "permanent"` kèm `state` (mặc định `true` = `open`, `false` = `close`) được chuẩn hóa về hai mode này.

Mỗi công tắc khai báo: loại, hành vi, danh sách cầu liên kết.

### A5. Tách và ghép *(Đợt 2, chưa cài)*
Trạng thái chứa vị trí 2 cube và cube đang điều khiển. Mỗi cube lăn 1 ô theo 4 hướng. Có hành động đổi cube điều khiển (ký hiệu `S`, phím cách) nằm trong `actions()` để solver tự giải được. Hai cube ghép lại thành 1×1×2 ngay khi ở hai ô kề nhau (`|r0-r1|+|c0-c1| == 1`). Cube đơn kích hoạt được soft, **không** kích hoạt được heavy/split, và **không** thắng màn (đứng trên goal vẫn `PLAYING`, `is_goal` = False khi đang split).

**Quy ước split đã chốt trong nhóm (không phải từ đề):**
`State.split = ((r0,c0),(r1,c1),active)`, `active ∈ {0,1}`. Khi split: `orient = STANDING` và `(r,c) = split[active]`. Hành động `S` chỉ đổi `active` và **không** kích hoạt lại công tắc. Khi split chỉ kiểm tra công tắc tại ô cube vừa di chuyển tới. Khối split khởi đầu điều khiển cube 0.

### Quyết định cần thống nhất
Cube đơn đứng trên `fragile` thì ô vỡ và cube thua (`LOST`), vì cube chiếm 1 ô, giống khối đứng. Đề gốc yêu cầu ghi quyết định này.

**Trạng thái: chờ nhóm xác nhận.**

## B. Schema JSON và thứ tự xử lý

`bridges` và `switches` đều tùy chọn (thiếu hoặc `[]` đều hợp lệ).

```json
{
  "version": 1, "id": "T1",
  "grid": ["..S#G", "....."],
  "start": [0, 0],
  "legend": {".": "floor", "#": "void", "G": "goal", "F": "fragile", "S": "floor"},
  "bridges": [{"id": 0, "cells": [[0, 3]], "open": false}],
  "switches": [{"cell": [0, 2], "type": "soft", "targets": [0], "mode": "toggle"}]
}
```

Ô `S` trên grid là `floor`. Ô cầu `(0,3)` vẽ `#` hay `.` đều được; trạng thái thật do `bridges` quyết định. Giá trị legend chỉ thuộc `floor|void|goal|fragile`.

- `bridges[i].id == i` (liên tục 0..n-1); `cells` không rỗng, nằm trong bàn, ký tự grid là `floor|void`; mỗi ô thuộc tối đa một cầu; `open` là bool.
- Công tắc `soft|heavy`: `cell`, `targets` (id cầu, không rỗng, phải tồn tại), `mode` ∈ `toggle|open|close|permanent`, `state` (bool, tùy chọn, chỉ cho `permanent`).
- Công tắc `split`: `cell`, `split_to` = hai ô khác nhau, đều là `floor`.
- Ô công tắc phải là `floor`, không trùng ô cầu, không trùng công tắc khác.

**Thứ tự xử lý một nước đi:**
1. **B1** Lăn hình học bằng `TRANSITIONS`, giữ nguyên `bridges`.
2. **B2** Kiểm tra rơi theo trạng thái cầu *hiện tại* (trước hiệu ứng): ô void / cầu đóng / ngoài bàn, hoặc đứng trên fragile → `LOST`. `LOST` thì trả state thô, **không** kích hoạt công tắc, `bridges` giữ nguyên.
3. **B3** Nếu không rơi, áp công tắc theo thứ tự khai báo: `toggle` = XOR bit, `open` = set bit, `close` = clear bit.

Ví dụ trên: đứng ở `(0,0)`, bấm `R` → khối nằm `(0,1)-(0,2)` chạm công tắc `(0,2)` → toggle mở cầu `0`.

## D. Phối hợp

- **Sự kiện cho TV4 (GUI)** — *đề xuất, chưa cài*; hiện `state_to_dict` chưa có trường sự kiện, định dạng chốt với TV4 ở đợt sau:
  - **cầu đổi trạng thái**: kèm id cầu và hướng (mở/đóng);
  - **ô vỡ**: fragile bị khối đứng/cube đè;
  - **tách**: kèm 2 vị trí đích;
  - **ghép**: kèm vị trí và hướng khối sau ghép.
- **Báo TV1/TV5 về hành động `S`** — *chưa cài ở Đợt 1*: khi đang split, `actions()` trả thêm `'S'` (sau `U,D,L,R`). Solver phải coi `S` là một hành động bình thường (cost 1.0) và nhớ rằng `State` gồm `bridges` và `split`, nên tập `visited` đã đúng.
- **`cost`** giữ nguyên 1.0 cho mọi nước đi, kể cả `S`; heuristic của A* (TV1) phải admissible với chi phí này.

## E. Tiêu chí "xong"

- [ ] Mỗi loại ô đặc biệt có ít nhất 1 màn chạy đúng bằng tay và giải được bằng BFS.
- [x] `pytest` qua toàn bộ.
- [x] Solver không lặp vô hạn khi có toggle: tình trạng cầu (và split) nằm trong `State` nên tập `visited` đúng. Có test BFS trên level có toggle (`test_bfs_soft_toggle_mo_cau`) chứng minh kết thúc.
- Trạng thái từng mục:
  - **Đợt 1** = fragile, cầu, soft, heavy, toggle/permanent — *đã cài*.
  - **Đợt 2** = split, `S`, ghép — *chưa làm*.
  - **Đợt 3** = bộ level (3–5 màn fragile, 3–5 màn công tắc+cầu, 3–5 màn có split) cùng TV1 — *chưa làm*.
