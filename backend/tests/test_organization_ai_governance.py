"""Política de governança de IA por organização (score de risco)."""

from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_patch_org_ai_governance_owner_admin(async_client) -> None:
    reg = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "govowner2@example.com",
            "username": "govowner2",
            "full_name": "Gov Owner",
            "password": "testpass123",
        },
    )
    assert reg.status_code == 201, reg.text
    login = await async_client.post(
        "/api/v1/auth/login",
        data={"username": "govowner2", "password": "testpass123"},
    )
    assert login.status_code == 200, login.text
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    org = await async_client.post(
        "/api/v1/organizations",
        json={"name": "Escritório Governança 2", "description": "teste"},
        headers=headers,
    )
    assert org.status_code == 201, org.text
    org_id = org.json()["id"]

    me = await async_client.get("/api/v1/organizations/me", headers=headers)
    assert me.status_code == 200
    body = me.json()
    assert isinstance(body, list) and len(body) >= 1
    assert body[0]["risk_ai_human_review_required"] is False

    patch = await async_client.patch(
        f"/api/v1/organizations/{org_id}/ai-governance",
        json={
            "risk_ai_human_review_required": True,
            "risk_ai_governance_reference_url": "https://example.com/ripd-risco.pdf",
        },
        headers=headers,
    )
    assert patch.status_code == 200, patch.text
    data = patch.json()
    assert data["risk_ai_human_review_required"] is True
    assert "ripd-risco" in (data.get("risk_ai_governance_reference_url") or "")

    inv = await async_client.post(
        "/api/v1/investigations",
        headers=headers,
        json={
            "target_name": "Alvo governança IA",
            "target_cpf_cnpj": "52998224725",
            "target_description": "teste",
            "priority": 1,
        },
    )
    assert inv.status_code == 201, inv.text
    inv_id = inv.json()["id"]
    risk = await async_client.get(f"/api/v1/investigations/{inv_id}/risk-score", headers=headers)
    assert risk.status_code == 200, risk.text
    rj = risk.json()
    assert rj.get("governance", {}).get("human_review_required") is True
    assert any("[Governança]" in str(x) for x in (rj.get("recommendations") or []))

    ack = await async_client.post(
        f"/api/v1/investigations/{inv_id}/risk-score-review",
        headers=headers,
    )
    assert ack.status_code == 200, ack.text
    inv_get = await async_client.get(f"/api/v1/investigations/{inv_id}", headers=headers)
    assert inv_get.status_code == 200
    assert inv_get.json().get("risk_score_reviewed_at")
    assert inv_get.json().get("risk_score_reviewed_by_id")

    ack2 = await async_client.post(
        f"/api/v1/investigations/{inv_id}/risk-score-review",
        headers=headers,
    )
    assert ack2.status_code == 409
