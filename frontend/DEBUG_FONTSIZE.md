Đã xác nhận vấn đề với fontSize. Sẽ tạo một custom extension FontSize đơn giản để thêm thuộc tính fontSize cho TextStyle mark.

Lỗi chính:
1. Extension chưa được add vào editor
2. Cần thêm `!important` vào CSS để override prose style
3. Code apply fontSize chưa đúng

Giải pháp:
- Thêm FontSize extension extends TextStyle
- Apply với !important trong style
- Test với selection và non-selection
