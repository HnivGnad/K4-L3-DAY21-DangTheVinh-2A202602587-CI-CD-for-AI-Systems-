"""Run three experiments and a local batch-2 comparison without changing tracked CSVs."""
import json
import shutil
from pathlib import Path

import pandas as pd
import yaml
from src.train import train

EXPERIMENTS = [
    {"n_estimators": 100, "learning_rate": 0.1, "max_depth": 3},
    {"n_estimators": 50, "learning_rate": 0.05, "max_depth": 2},
    {"n_estimators": 200, "learning_rate": 0.1, "max_depth": 5},
]


def main():
    destination = Path("nop-bai/results")
    destination.mkdir(parents=True, exist_ok=True)
    reports = []
    for params in EXPERIMENTS:
        train(params)
        reports.append(json.loads(Path("outputs/report.json").read_text()))
    best = max(reports, key=lambda report: report["f1_score"])
    Path("params.yaml").write_text(yaml.safe_dump(best["params"]), encoding="utf-8")
    # Recreate the selected baseline so the saved baseline artifact matches its report.
    train(best["params"])
    baseline = json.loads(Path("outputs/report.json").read_text())
    shutil.copy2("models/model.joblib", "outputs/baseline.joblib")
    combined = pd.concat([pd.read_csv("data/train_batch1.csv"),
                          pd.read_csv("data/train_batch2.csv")], ignore_index=True)
    combined_path = Path("outputs/train_combined.csv")
    combined.to_csv(combined_path, index=False)
    train(best["params"], data_path=str(combined_path))
    updated = json.loads(Path("outputs/report.json").read_text())
    (destination / "experiments.json").write_text(json.dumps(reports, indent=2), encoding="utf-8")
    (destination / "comparison.json").write_text(
        json.dumps({"execution": "local; not evidence of cloud deployment",
                    "baseline": baseline, "updated": updated}, indent=2), encoding="utf-8")
    shutil.copy2("models/model.joblib", "outputs/updated.joblib")
    shutil.copy2("outputs/baseline.joblib", "models/model.joblib")
    Path("outputs/report.json").write_text(json.dumps(baseline, indent=2), encoding="utf-8")
    print(json.dumps({"selected": best["params"], "baseline_f1": baseline["f1_score"],
                      "updated_f1": updated["f1_score"]}, indent=2))


if __name__ == "__main__":
    main()
