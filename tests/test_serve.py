from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from src import serve


@pytest.fixture
def client(monkeypatch):
    model = Mock()
    model.predict.return_value = [1]
    monkeypatch.setattr(serve, "download_model", lambda: None)
    monkeypatch.setattr(serve.joblib, "load", lambda _: model)
    with TestClient(serve.app) as client:
        yield client, model


def test_healthz(client):
    response = client[0].get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.parametrize("prediction,label", [(0, "thu_nhap_thap"), (1, "thu_nhap_cao")])
def test_score(client, prediction, label):
    client[1].predict.return_value = [prediction]
    response = client[0].post("/score", json={"features": [28, 2, 14, 2, 11, 0, 1, 0, 0, 45]})
    assert response.status_code == 200
    assert response.json() == {"prediction": prediction, "label": label}
    assert list(client[1].predict.call_args.args[0].columns) == serve.FEATURE_NAMES


@pytest.mark.parametrize("features", [[], [1] * 9, [1] * 11])
def test_reject_wrong_feature_count(client, features):
    assert client[0].post("/score", json={"features": features}).status_code == 400
    client[1].predict.assert_not_called()


def test_reject_non_numeric_features(client):
    assert client[0].post("/score", json={"features": ["bad"] * 10}).status_code == 422


def test_download_model_uses_s3(monkeypatch, tmp_path):
    monkeypatch.setenv("ARTIFACT_BUCKET", "test-bucket")
    monkeypatch.setattr(serve, "MODEL_PATH", tmp_path / "models/model.joblib")
    s3 = Mock()
    def download(bucket, key, destination):
        assert bucket == "test-bucket"
        assert key == "artifacts/current/model.joblib"
        from pathlib import Path
        Path(destination).write_bytes(b"model")
    s3.download_file.side_effect = download
    monkeypatch.setattr(serve.boto3, "client", lambda _: s3)
    serve.download_model()
    assert serve.MODEL_PATH.read_bytes() == b"model"
