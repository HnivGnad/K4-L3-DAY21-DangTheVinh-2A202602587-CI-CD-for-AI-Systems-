import json
import joblib
import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import accuracy_score, f1_score
from src.train import FEATURE_NAMES, train


def _make_temp_data(tmp_path):
    rng = np.random.default_rng(0)
    frame = pd.DataFrame(rng.random((200, len(FEATURE_NAMES))), columns=FEATURE_NAMES)
    frame["target"] = rng.integers(0, 2, size=200)
    train_path, eval_path = tmp_path / "train.csv", tmp_path / "holdout.csv"
    frame.iloc[:160].to_csv(train_path, index=False)
    frame.iloc[160:].to_csv(eval_path, index=False)
    return str(train_path), str(eval_path)


@pytest.fixture
def trained(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("MLFLOW_TRACKING_URI", "sqlite:///" + (tmp_path / "mlflow.db").as_posix())
    train_path, eval_path = _make_temp_data(tmp_path)
    f1 = train({"n_estimators": 10, "learning_rate": 0.1, "max_depth": 2},
               data_path=train_path, eval_path=eval_path)
    return f1, tmp_path, eval_path


def test_train_returns_float(trained):
    f1, _, _ = trained
    assert isinstance(f1, float)
    assert 0.0 <= f1 <= 1.0


def test_report_file_created(trained):
    f1, tmp_path, eval_path = trained
    report = json.loads((tmp_path / "outputs/report.json").read_text())
    model = joblib.load(tmp_path / "models/model.joblib")
    frame = pd.read_csv(eval_path)
    predictions = model.predict(frame[FEATURE_NAMES])
    assert report["f1_score"] == f1 == f1_score(frame.target, predictions)
    assert report["accuracy"] == accuracy_score(frame.target, predictions)
    assert report["train_samples"] == 160
    assert report["eval_samples"] == 40


def test_model_file_created(trained):
    _, tmp_path, eval_path = trained
    model_path = tmp_path / "models/model.joblib"
    assert model_path.is_file()
    model = joblib.load(model_path)
    assert list(model.feature_names_in_) == FEATURE_NAMES
    assert set(model.predict(pd.read_csv(eval_path)[FEATURE_NAMES])) <= {0, 1}
