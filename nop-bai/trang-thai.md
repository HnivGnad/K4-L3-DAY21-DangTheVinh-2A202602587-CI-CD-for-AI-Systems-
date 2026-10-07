# Trạng thái hoàn thành dự án

MSSV: **2A202602587**. AWS us-east-1. Screenshot được bỏ qua theo yêu cầu.

## Đã hoàn thành và xác minh

- Train: GradientBoosting, MLflow params/metrics/model, JSON report và joblib.
- Ba thí nghiệm local; chọn n_estimators=200, learning_rate=0.1, max_depth=5.
- 19/19 kiểm thử qua cả local và GitHub Actions; DVC status, pip check và cú pháp workflow thành công.
- DVC S3: ba batch ban đầu và phiên bản train_batch1 mới (44.722 mẫu) đã upload.
- Năm GitHub Secrets được mã hóa sau khi người dùng cho phép; biến AWS_REGION và EC2_SECURITY_GROUP_ID.
- Baseline cloud: F1=0.7149321267, accuracy=0.874, train_samples=22361.
- Updated cloud: F1=0.7354260090, accuracy=0.882, train_samples=44722.
- Ba lần Actions có đủ bốn job Unit Test → Train → Quality Gate → Release thành công.
- Hai lần đầu dùng workflow_dispatch. Sau enable workflow của repo fork, commit 6b7f9b3 chỉ thêm chú thích vào data/train_batch1.csv.dvc đã tự tạo run từ event push, huấn luyện trên dữ liệu cập nhật và triển khai thành công. Commit thay hash dữ liệu trước đó là 395c0cf; lúc đó push chưa tạo run. Không gộp hai sự kiện này thành một bằng chứng.
- EC2 52.90.230.2: service income-api active/enabled, IAM role income-api-role. Report current S3 khớp model của lần Actions tự động gần nhất.
- Healthz=ok; hai payload mẫu trả thu_nhap_thap và thu_nhap_cao qua API thực.
- Release đồng bộ source, cài dependency, promote candidate sau gate, restart và kiểm tra health. Rule SSH của runner đã đóng; chỉ còn 22 và 8080 cho IP 42.117.48.218/32.

Bằng chứng: results/experiments.json, results/cloud-comparison.json, results/ec2-api.json.

- [Baseline Actions](https://github.com/HnivGnad/K4-L3-DAY21-DangTheVinh-2A202602587-CI-CD-for-AI-Systems-/actions/runs/37644362651)
- [Updated Actions](https://github.com/HnivGnad/K4-L3-DAY21-DangTheVinh-2A202602587-CI-CD-for-AI-Systems-/actions/runs/37645226460)
- [Automatic data-only push](https://github.com/HnivGnad/K4-L3-DAY21-DangTheVinh-2A202602587-CI-CD-for-AI-Systems-/actions/runs/37645799385)

## Phần người dùng thực hiện

Dán URL repository vào bài nộp trên VLearn. Các bonus tùy chọn không thực hiện. Không chạy append_batch.py lại với batch1 hiện tại vì đã có đủ batch2.

## Ghi nhận quá trình duyệt

Công cụ duyệt tự động từng từ chối đặt lại chính sách toàn repository thành allowed_actions=all vì phạm vi bảo mật quá rộng. Chính sách được giữ nguyên; đã bật riêng workflow và xác minh run push thành công, nên không còn cần thay đổi này.