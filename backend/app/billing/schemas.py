"""Billing request/response schemas."""

from pydantic import BaseModel


class CheckoutRequest(BaseModel):
    price_id: str
    success_url: str = "http://localhost:3000/dashboard?checkout=success"
    cancel_url: str = "http://localhost:3000/dashboard?checkout=cancel"


class PortalRequest(BaseModel):
    return_url: str = "http://localhost:3000/dashboard"


class WebhookPayload(BaseModel):
    type: str
    data: dict
