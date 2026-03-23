"""Billing request/response schemas."""

import re

from pydantic import BaseModel, field_validator

from app.core.url_validation import validate_redirect_url


class CheckoutRequest(BaseModel):
    price_id: str
    success_url: str
    cancel_url: str

    @field_validator("price_id")
    @classmethod
    def validate_price_id(cls, v: str) -> str:
        if not re.match(r"^price_[a-zA-Z0-9]+$", v):
            raise ValueError("Invalid Stripe price ID format")
        return v

    @field_validator("success_url", "cancel_url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        return validate_redirect_url(v)


class PortalRequest(BaseModel):
    # customer_id intentionally excluded — must be resolved server-side from user_id
    return_url: str

    @field_validator("return_url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        return validate_redirect_url(v)


class WebhookPayload(BaseModel):
    type: str
    data: dict


class CheckoutResponse(BaseModel):
    """Response from checkout session creation."""

    url: str


class PortalResponse(BaseModel):
    """Response from portal session creation."""

    url: str


class WebhookResponse(BaseModel):
    """Response from webhook processing."""

    handled: bool
    type: str
