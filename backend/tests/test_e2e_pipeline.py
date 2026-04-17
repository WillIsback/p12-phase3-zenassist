import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient  # noqa: E402

from main import app  # noqa: E402

ALLOWED_TAGS = [
    "Debt collection",
    "Consumer Loan",
    "Credit card or prepaid card",
    "Mortgage",
    "Vehicle loan or lease",
    "Student loan",
    "Payday loan, title loan, or personal loan",
    "Checking or savings account",
    "Bank account or service",
    "Money transfer, virtual currency, or money service",
    "Money transfers",
    "Other financial services",
]


def load_mock_data() -> list[dict[str, str | None]]:
    data_path = Path(__file__).resolve().parents[1] / "data" / "mock_data.json"
    with data_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def test_end_to_end_tagging_pipeline(request, capsys) -> None:
    client = TestClient(app)
    is_verbose = request.config.getoption("verbose") > 0

    root_resp = client.get("/")
    assert root_resp.status_code == 200
    assert root_resp.json() == {"message": "API est opérationnelle"}

    health_resp = client.get("/health")
    assert health_resp.status_code == 200
    assert health_resp.json() == {"status": "ok", "model_ready": True}

    mock_data = load_mock_data()
    assert len(mock_data) > 0

    for item in mock_data:
        response = client.post("/tag", json={"user_claim": item["content"]})
        assert response.status_code == 200, response.text

        payload = response.json()
        if is_verbose:
            with capsys.disabled():
                print(f"{payload['tag']} ({payload['confidence']}) - {item['content']}")
        assert "tag" in payload
        assert payload["tag"] in ALLOWED_TAGS
        assert "confidence" in payload
        assert payload["confidence"] is None or isinstance(payload["confidence"], float)
