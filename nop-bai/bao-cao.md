# Báo Cáo Lab Day 21 - CI/CD cho AI Systems

| | |
|---|---|
| Họ và tên | Đặng Thế Vinh |
| MSSV | 2A202602587 |
| Lớp / Khóa | K4 |
| Repo GitHub | https://github.com/HnivGnad/K4-L3-DAY21-DangTheVinh-2A202602587-CI-CD-for-AI-Systems- |
| Ngày báo cáo | 07-10-2026 |

## 1. Bộ Siêu Tham Số Đã Chọn và Lý Do

| Lần chạy | n_estimators | learning_rate | max_depth | f1_score | accuracy |
|---|---|---|---|---|---|
| 1 | 100 | 0.1 | 3 | 0.710900 | 0.878000 |
| 2 | 50 | 0.05 | 2 | 0.605128 | 0.846000 |
| 3 | 200 | 0.1 | 5 | 0.714932 | 0.874000 |

**Bộ siêu tham số đã chọn:** `n_estimators=200`, `learning_rate=0.1`, `max_depth=5`.

**Lý do:** Bộ này đạt F1 lớp dương cao nhất trong ba thí nghiệm thực tế, trên cùng holdout 500 mẫu. Lần có accuracy cao nhất không trùng với lần có F1 cao nhất. Learning rate nhỏ thường cần nhiều cây hơn để bù mức đóng góp thấp của mỗi cây. Ba lần chạy đổi cả độ sâu nên chưa tách riêng tác động từng tham số. Kết quả được ghi vào MLflow và JSON ở local.

## 2. Vì Sao Ngưỡng Chất Lượng Đặt Trên F1 Chứ Không Phải Accuracy

Adult có khoảng 24,8% mẫu thu nhập cao. Mô hình luôn dự đoán thu nhập thấp vẫn đạt accuracy khoảng 75,2%, nhưng không tìm được trường hợp dương nào và có F1 bằng 0. F1 là trung bình điều hòa của precision và recall lớp dương, phản ánh cả gán nhầm và bỏ sót. Vì vậy, pipeline kiểm tra F1 tối thiểu 0,65; accuracy chỉ dùng tham khảo. Không dùng weighted vì lớp đa số chi phối, cũng không dùng macro vì nó trung bình hai lớp, không tương đương F1 của target=1. Macro cho hai lớp trọng số bằng nhau. Hàm tính dùng chế độ binary mặc định.

## 3. Khó Khăn Gặp Phải và Cách Giải Quyết

| Khó khăn | Nguyên nhân | Cách giải quyết |
|---|---|---|
| Không gọi được Python. | PATH và launcher chưa nhận bản cài. | Tạo môi trường Python 3.10 riêng. |
| DVC push bị AccessDenied. | IAM user thiếu quyền S3 của bucket. | Gắn policy giới hạn bucket và các prefix dvc/, artifacts/. |
| Model có thể bị thay trước gate. | Khung ban đầu upload vào current ngay ở Train. | Lưu candidate riêng và chỉ promote sau gate. |

## 4. So Sánh Bước 2 và Bước 3 (bắt buộc, 2 - 3 câu)

| | f1_score | accuracy |
|---|---|---|
| Bước 2 (mô phỏng cục bộ, 22.361 mẫu) | 0.714932 | 0.874000 |
| Bước 3 (mô phỏng cục bộ, 44.722 mẫu) | 0.735426 | 0.882000 |

**Nhận xét:** F1 thay đổi +0.020494 khi gấp đôi dữ liệu cùng nguồn, với cùng bộ tham số và holdout. Thêm dữ liệu không đảm bảo cải thiện vì phân phối tương tự và holdout chỉ có 500 mẫu. DVC push và API EC2 đã kiểm tra thành công với model baseline khởi động thủ công; chưa xác nhận hai lần Actions, nên bảng dùng số liệu local. Screenshot được bỏ qua.
