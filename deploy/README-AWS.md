# Triển khai lab trên AWS

## Chạy cục bộ (PowerShell)

```powershell
.\.venv\Scripts\Activate.ps1
python prepare_data.py
python -m pytest tests/ -v --basetemp .tools/pytest-local
python -m scripts.run_experiments
mlflow ui --backend-store-uri sqlite:///mlflow.db
```

Script thí nghiệm ghi ba kết quả vào `nop-bai/results/experiments.json`, chọn bộ có F1 cao nhất vào `params.yaml`, rồi so sánh dữ liệu 22.361 và 44.722 mẫu trên cùng holdout. `comparison.json` là số liệu cục bộ, chưa chứng minh Actions hay EC2 đã chạy.

## DVC / S3

Dùng tên bucket thật; không tạo bucket hoặc VM nếu chưa xác định tài nguyên cần dùng.

```powershell
$env:AWS_PROFILE = 'default'
$env:AWS_DEFAULT_REGION = 'us-east-1'
$bucket = 'TEN_BUCKET_THAT'
dvc init
dvc remote add -d labstore "s3://$bucket/dvc"
dvc add data/train_batch1.csv data/holdout.csv data/train_batch2.csv
dvc push
```

Nếu DVC đã init thì bỏ lệnh init; nếu remote đã có thì dùng `dvc remote modify labstore url ...`. Không ghi access key vào `.dvc/config`. CI lấy credentials từ GitHub Secrets; EC2 dùng IAM role hoặc AWS credential chain. DVC local đã được init và dữ liệu được track nếu các bước đó chạy thành công; xem báo cáo trạng thái để biết kết quả thực tế.

## GitHub Actions

Thiết lập 5 secrets: `STORAGE_CREDENTIALS` (JSON có `aws_access_key_id`, `aws_secret_access_key`, thêm `aws_session_token` nếu dùng STS), `ARTIFACT_BUCKET`, `SERVER_HOST`, `SERVER_USER`, `SERVER_SSH_KEY`. Đặt repository variable `AWS_REGION` theo region của bucket (mặc định `us-east-1`). Đặt thêm variable EC2_SECURITY_GROUP_ID=sg-07071df86d14cd82f. CI cần quyền ec2:AuthorizeSecurityGroupIngress và ec2:RevokeSecurityGroupIngress trên security group này. Release mở SSH cho IP runner /32 rồi đóng rule đó ở bước always(). Nhập giá trị bí mật trong Settings của GitHub.

Workflow chỉ chạy test trên pull request. Push lên main chạy đủ bốn job. Job Train đưa candidate vào `artifacts/runs/<run-id>/<attempt>/`; Release chỉ copy candidate sang `artifacts/current/` sau khi F1 đạt 0.65. EC2 cần quyền đọc candidate và ghi prefix current để thực hiện copy. Một model không đạt sẽ không thay model đang phục vụ.

## EC2 Ubuntu

Đặt repo ở `/home/ubuntu/income-api`; cài Python 3.10, tạo `.venv` và cài **đúng phiên bản** trong `requirements-serving.txt` để tránh sai phiên bản model joblib. Nếu user khác ubuntu, sửa tất cả đường dẫn và User trong service.

```bash
cd ~/income-api
python3 -m venv .venv
.venv/bin/pip install -r requirements-serving.txt
cp deploy/income-api.env.example deploy/income-api.env
# Sửa ARTIFACT_BUCKET, AWS_DEFAULT_REGION và MODEL_PATH trong file env.
sudo cp deploy/income-api.service /etc/systemd/system/income-api.service
sudo systemctl daemon-reload
sudo systemctl enable income-api
```

EC2 dùng IAM role được phép GetObject với `artifacts/`, PutObject với `artifacts/current/`. CI cần đọc/ghi S3 object trong bucket cho DVC và upload candidate; DVC cũng cần ListBucket. Mở cổng 8080 cho nơi cần gọi API và cổng SSH cho runner. Deploy user cần được phép `sudo systemctl restart income-api` không tương tác.

Sau khi pipeline đầu tiên chạy, gọi `/healthz` và `/score` trên IP EC2. Workflow tự đồng bộ code serving và cài dependency trước khi restart.

## Bước 3

Chỉ ghép batch sau khi đã có lần chạy cloud baseline thành công. Không chạy `append_batch.py` nhiều lần vì script sẽ ghép trùng batch.

```powershell
python append_batch.py
dvc add data/train_batch1.csv
dvc push
git add data/train_batch1.csv.dvc
git commit -m 'data: bo sung 22361 mau train_batch2'
git push origin main
```

Luôn `dvc push` trước `git push`. Tải report artifact của hai lần Actions và điền số liệu cloud vào báo cáo; nếu dùng số liệu cục bộ phải ghi rõ nguồn. Bỏ qua screenshot theo yêu cầu của chủ dự án.
