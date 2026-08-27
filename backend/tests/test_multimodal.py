"""Multimodal endpoints: degradation, extraction, and OUR verdict math."""
import base64
import json

import httpx
import respx

from app.config import settings

# 1x1 px PNG
_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)


def test_status_reports_off_without_key(client):
    r = client.get("/api/multimodal/status")
    assert r.status_code == 200
    assert r.json() == {
        "vision": False,
        "transcription": False,
        "vision_model": None,
        "transcription_model": None,
    }


def test_analyze_bill_503_without_key(client):
    r = client.post(
        "/api/multimodal/analyze-bill",
        files={"file": ("bill.png", _PNG, "image/png")},
        data={"city": "Delhi", "treatment_id": "t_knee"},
    )
    assert r.status_code == 503


def test_transcribe_503_without_key(client):
    r = client.post(
        "/api/multimodal/transcribe",
        files={"file": ("clip.webm", b"fakeaudio", "audio/webm")},
    )
    assert r.status_code == 503


@respx.mock
def test_analyze_bill_extracts_and_scores_against_our_data(client, monkeypatch):
    monkeypatch.setattr(settings, "groq_api_key", "test-key")

    model_reply = {
        "choices": [
            {
                "message": {
                    "content": json.dumps(
                        {
                            "hospital_name": "Delhi Premium Hospital",
                            "document_type": "bill",
                            "detected_treatment": "knee replacement surgery",
                            "line_items": [
                                {"description": "Implant", "amount": 250000},
                                {"description": "Surgeon + OT", "amount": 300000},
                            ],
                            "total_amount": 550000,
                            "currency": "INR",
                            "notes": None,
                        }
                    )
                }
            }
        ]
    }
    respx.post("https://api.groq.com/openai/v1/chat/completions").mock(
        return_value=httpx.Response(200, json=model_reply)
    )

    r = client.post(
        "/api/multimodal/analyze-bill",
        files={"file": ("bill.png", _PNG, "image/png")},
        data={"city": "Delhi", "treatment_id": "t_knee"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["extracted"]["total_amount"] == 550000
    assert body["matched_treatment"]["id"] == "t_knee"
    assert body["our_estimate"] is not None
    # Delhi knee pooled range is ~80k-420k; 550k bill -> "above"
    assert body["verdict"] == "above"


@respx.mock
def test_analyze_bill_rejects_non_json_model_output(client, monkeypatch):
    monkeypatch.setattr(settings, "groq_api_key", "test-key")
    respx.post("https://api.groq.com/openai/v1/chat/completions").mock(
        return_value=httpx.Response(
            200, json={"choices": [{"message": {"content": "sorry, I can't read this"}}]}
        )
    )
    r = client.post(
        "/api/multimodal/analyze-bill",
        files={"file": ("bill.png", _PNG, "image/png")},
        data={"city": "Delhi"},
    )
    assert r.status_code == 503


def test_analyze_bill_rejects_bad_mime(client, monkeypatch):
    monkeypatch.setattr(settings, "groq_api_key", "test-key")
    r = client.post(
        "/api/multimodal/analyze-bill",
        files={"file": ("bill.txt", b"hello", "text/plain")},
        data={"city": "Delhi"},
    )
    assert r.status_code == 422
