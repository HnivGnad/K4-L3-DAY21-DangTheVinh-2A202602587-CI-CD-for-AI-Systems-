"""Write the lab report from measured local experiment results."""
import json
from pathlib import Path


def main():
    destination = Path("nop-bai")
    experiments = json.loads((destination / "results/experiments.json").read_text())
    comparison = json.loads((destination / "results/comparison.json").read_text())
    cloud_path = destination / "results/cloud-comparison.json"
    cloud = json.loads(cloud_path.read_text()) if cloud_path.exists() else None
    if cloud:
        comparison = cloud
    baseline, updated = comparison["baseline"], comparison["updated"]
    measurement_source = "GitHub Actions" if cloud else "local simulation"
    params = baseline["params"]
    rows = "\n".join(
        f"| {i} | {r['params']['n_estimators']} | {r['params']['learning_rate']} | "
        f"{r['params']['max_depth']} | {r['f1_score']:.6f} | {r['accuracy']:.6f} |"
        for i, r in enumerate(experiments, 1))
    delta = updated["f1_score"] - baseline["f1_score"]
    best_accuracy = max(experiments, key=lambda r: r["accuracy"])
    same = "trùng" if best_accuracy["params"] == params else "không trùng"
    report = f"""# Báo Cáo Lab Day 21 - CI/CD cho AI Systems

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
{rows}

**Bộ siêu tham số đã chọn:** `n_estimators={params['n_estimators']}`, `learning_rate={params['learning_rate']}`, `max_depth={params['max_depth']}`.

**Lý do:** Bộ này đạt F1 lớp dương cao nhất trong ba thí nghiệm thực tế, trên cùng holdout 500 mẫu. Lần có accuracy cao nhất {same} với lần có F1 cao nhất. Learning rate nhỏ thường cần nhiều cây hơn để bù mức đóng góp thấp của mỗi cây. Ba lần chạy đổi cả độ sâu nên chưa tách riêng tác động từng tham số. Kết quả được ghi vào MLflow và JSON ở local.

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
| Bước 2 (mô phỏng cục bộ, 22.361 mẫu) | {baseline['f1_score']:.6f} | {baseline['accuracy']:.6f} |
| Bước 3 (mô phỏng cục bộ, 44.722 mẫu) | {updated['f1_score']:.6f} | {updated['accuracy']:.6f} |

**Nhận xét:** F1 thay đổi {delta:+.6f} khi gấp đôi dữ liệu cùng nguồn, với cùng bộ tham số và holdout. Thêm dữ liệu không đảm bảo cải thiện vì phân phối tương tự và holdout chỉ có 500 mẫu. DVC push và API EC2 đã kiểm tra thành công với model baseline khởi động thủ công; chưa xác nhận hai lần Actions, nên bảng dùng số liệu local. Screenshot được bỏ qua.
"""
    if cloud:
        report = report.replace("mô phỏng cục bộ", measurement_source)
        old_status = "DVC push và API EC2 đã kiểm tra thành công với model baseline khởi động thủ công; chưa xác nhận hai lần Actions, nên bảng dùng số liệu local."
        report = report.replace(old_status, "Hai lần huấn luyện cloud và lần push chỉ đổi chú thích DVC đã thành công; phần trigger được xác minh sau khi bật workflow repo fork.")
        if not cloud.get("automatic_trigger_verified", False):
            report = report.replace("Hai lần huấn luyện cloud và lần push chỉ đổi chú thích DVC đã thành công; phần trigger được xác minh sau khi bật workflow repo fork.", "Hai lần pipeline cloud đã thành công qua workflow_dispatch; commit dữ liệu đã push nhưng GitHub chưa tự tạo run, nên chưa xác nhận trigger push.")
        report += "\nActions: [baseline](" + cloud["baseline_run"]["url"] + ") | [updated](" + cloud["updated_run"]["url"] + ").\n"
        if cloud.get("automatic_run"):
            report += "[Automatic data-only push](" + cloud["automatic_run"]["url"] + ").\n"
    (destination / "bao-cao.md").write_text(report, encoding="utf-8")
    print(f"Report written: {len(report.split())} whitespace-delimited words")


if __name__ == "__main__":
    main()
