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
- **Split**: chỉ kích hoạt khi khối *đứng*, không split; khối dịch chuyển tới các vị trí định sẵn và tách thành 2 cube 1×1×1. *(Đợt 2, đã cài.)*

### A4. Hành vi công tắc
- **toggle**: mỗi lần kích hoạt đảo trạng thái các cầu liên kết.
- **permanent**: đặt cầu vào trạng thái cố định. Trong JSON là `open`/`close`; `"mode": "permanent"` kèm `state` (mặc định `true` = `open`, `false` = `close`) được chuẩn hóa về hai mode này.

Mỗi công tắc khai báo: loại, hành vi, danh sách cầu liên kết.

### A5. Tách và ghép *(Đợt 2, đã cài)*
Trạng thái chứa vị trí 2 cube và cube đang điều khiển. Mỗi cube lăn 1 ô theo 4 hướng. Có hành động đổi cube điều khiển (ký hiệu `S`, phím cách) nằm trong `actions()` để solver tự giải được. Hai cube ghép lại thành 1×1×2 ngay khi ở hai ô kề nhau (`|r0-r1|+|c0-c1| == 1`). Cube đơn kích hoạt được soft, **không** kích hoạt được heavy/split, và **không** thắng màn (đứng trên goal vẫn `PLAYING`, `is_goal` = False khi đang split).

**Biểu diễn (đã chốt trong nhóm):** `State.split = ((r0,c0),(r1,c1),active)`, `active ∈ {0,1}`; không split thì `None`. Khi split: `orient = STANDING`, `(r,c) = split[active]`, `bridges` giữ nguyên. Khối split khởi đầu điều khiển cube 0.

**Luật cài đặt:**
1. **Kích hoạt split**: sau B2 (không rơi), khối thường *đứng* (`split is None`) trên ô công tắc `split` ⇒ tách tại `split_to`, điều khiển cube 0, `bridges` giữ nguyên. Nằm đè công tắc ⇒ không tách. Dùng lại được mỗi lần khối 1×2 đứng xuống.
2. **Hành động**: khi split `actions` trả `U, D, L, R, S`; không split chỉ `U, D, L, R`. `U/D/L/R` làm cube đang điều khiển lăn 1 ô. `S` chỉ đổi `active` (và `(r,c)`), **không** kích hoạt công tắc, không đổi `bridges`, không bao giờ làm rơi; `S` khi không split ⇒ `ValueError`.
3. **Một nước của cube**: **B1** cube lăn (cube kia giữ nguyên) → **B2** ô mới là void / cầu đóng / ngoài bàn / `fragile` ⇒ `LOST` (trả state thô, `bridges` giữ nguyên) → **B3** chỉ xét công tắc tại ô cube *vừa đến*: soft kích hoạt, heavy và split thì không → **ghép** (sau B3): hai cube kề nhau ⇒ cùng hàng `LYING_H` tại `(r, min c)`, cùng cột `LYING_V` tại `(min r, c)`, `split=None`, `bridges` giữ nguyên (gồm thay đổi do B3 vừa xảy ra).
4. **`status` / `is_goal` khi split**: duyệt từng cube; cube ở void / cầu đóng / ngoài bàn / fragile ⇒ `LOST`, ngược lại `PLAYING` (kể cả cube đứng trên goal). `is_goal` = `False` khi split. Chỉ khối ghép rồi đứng trên goal mới `WON`.
5. `cost` = 1.0 cho mọi hành động kể cả `S`. `actions/result/step` dùng chung một đường tính `_land`.

**Quy tắc P1–P5:**
- **P1**: cube lăn vào ô cube kia là nước *không hợp lệ* (không phải rơi): loại khỏi `actions`, `result` và `step` đều `ValueError`. (Hai cube kề nhau luôn bị ghép nên tình huống này chỉ xảy ra với state dựng tay.)
- **P2**: hai ô `split_to` không được trùng hoặc kề nhau (loader báo `LevelError`), nên ghép chỉ xảy ra sau một nước `U/D/L/R` của cube.
- **P3**: công tắc nằm trên ô `split_to` **không** kích hoạt lúc tách; chỉ ô cube vừa *lăn tới* mới kích hoạt.
- **P4**: nếu B3 đóng một cầu mà một ô của khối nằm hoặc cube đứng yên đang đứng trên đó ⇒ state sau B3 là `LOST`. `step` trả `(state_sau_B3, "LOST")` với `bridges` **đã đổi** (khác rơi ở B2: state thô, `bridges` giữ nguyên); `result` ⇒ `ValueError`; `actions` loại nước đó. Áp dụng cho cả khối thường lẫn cube.
- **P5**: một màn có thể có nhiều công tắc split, mỗi cái có `split_to` riêng.

**Quy tắc bổ sung (Đợt 2):**
- `mode` là **bắt buộc** cho công tắc `soft|heavy`.
- Công tắc **không** kích hoạt ở trạng thái đầu: chỉ kích hoạt khi khối *đáp xuống* bằng một nước đi, kể cả khi `start` trùng công tắc.
- `start` không được nằm trên ô của cầu đang đóng; `split_to` không được trùng ô của bất kỳ cầu nào (loader báo `LevelError`).

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
- Công tắc `split`: `cell`, `split_to` = hai ô đều là `floor`, không thuộc cầu nào, không trùng và không kề nhau.
- Ô công tắc phải là `floor`, không trùng ô cầu, không trùng công tắc khác. `start` không nằm trên cầu đang đóng.

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
- **Báo TV1/TV5 về hành động `S`** — *đã cài ở Đợt 2*: khi đang split, `actions()` trả thêm `'S'` (sau `U,D,L,R`). Solver phải coi `S` là một hành động bình thường (cost 1.0) và nhớ rằng `State` gồm `bridges` và `split`, nên tập `visited` đã đúng.
- **`cost`** giữ nguyên 1.0 cho mọi nước đi, kể cả `S`; heuristic của A* (TV1) phải admissible với chi phí này.

## E. Tiêu chí "xong"

- [ ] Mỗi loại ô đặc biệt có ít nhất 1 màn chạy đúng bằng tay và giải được bằng BFS. *(Đã có level dựng trong test; file level thật ở Đợt 3.)*
- [x] `pytest` qua toàn bộ.
- [x] Solver không lặp vô hạn khi có toggle: tình trạng cầu (và split) nằm trong `State` nên tập `visited` đúng. Có test BFS trên level có toggle (`test_bfs_soft_toggle_mo_cau`, `test_bfs_ket_thuc_khi_khong_giai_duoc`) chứng minh kết thúc.
- Trạng thái từng mục:
  - **Đợt 1** = fragile, cầu, soft, heavy, toggle/permanent — *đã cài*.
  - **Đợt 2** = split, `S`, ghép — *đã cài*.
  - **Đợt 3** = bộ level (3–5 màn fragile, 3–5 màn công tắc+cầu, 3–5 màn có split) cùng TV1 — *chưa làm*.
