# Trạng thái dự án

MSSV: **2A202602587**. AWS us-east-1. Bỏ qua screenshot theo yêu cầu.

- Hoàn thiện train, FastAPI, DVC S3 và workflow bốn job Unit Test → Train → Quality Gate → Release.
- 19/19 kiểm thử thành công; cú pháp shell và Python trong workflow đã kiểm tra.
- Ba thí nghiệm MLflow đã chạy; chọn n_estimators=200, learning_rate=0.1, max_depth=5.
- Local baseline: F1=0.714932, accuracy=0.874; local batch gộp: F1=0.735426, accuracy=0.882.
- DVC push thành công ba file vào income-lab-vinh-2a202602587-20261007-01/dvc.
- EC2 52.90.230.2 đã cài API và systemd income-api active/enabled. IAM role income-api-role.
- Model baseline được kiểm tra gate rồi upload thủ công vào S3 current để khởi động API. Đây là bootstrap, chưa phải bằng chứng Actions.
- Kiểm tra API thực qua HTTP: healthz=ok; hai payload mẫu trả thu_nhap_thap và thu_nhap_cao. Xem results/ec2-api.json.
- Security group chỉ mở SSH 22 và API 8080 cho IP máy người dùng 42.117.48.218/32; đã gỡ rule SQL 1433 và TCP 0 từ lần cấu hình nhầm.

## Đang chờ

Cần sự cho phép rõ ràng để đưa AWS credentials và private key SSH vào GitHub Secrets của repository. Cơ chế duyệt tự động đã chặn việc gửi secrets khi chưa có xác nhận này.
Chưa xác minh bốn job Actions và commit dữ liệu kích hoạt pipeline. Dữ liệu train_batch1 vẫn giữ 22.361 mẫu để chạy cloud baseline trước khi ghép batch. Chưa commit/push thay đổi.