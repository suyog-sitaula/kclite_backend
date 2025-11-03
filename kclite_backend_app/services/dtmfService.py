

"""
DTMF service for Twilio outbound verification calls.

Goal
-----
When Twilio calls a verification/IVR number, automatically send the
DTMF digits for a code that you've stored in Redis.

How it works
------------
1) We fetch the code from Redis (e.g., key = f"verify:{target_number}").
2) We build a TwiML response that waits a moment, then sends DTMF digits.
   - We use <Play digits="..."> to transmit DTMF.
   - 'w' inside digits = 0.5s pause (so "ww" ≈ 1s wait before tones).
3) We start a Twilio call with that TwiML. As soon as the other side answers,
   Twilio will send the tones.

Notes
-----
- Set TWILIO_FROM_NUMBER to a number you own/verified. For BYOC, you can
  optionally set TWILIO_BYOC_TRUNK_SID to force routing over your BYOC trunk.
- If the IVR speaks a prompt (e.g., "Please enter your 6-digit code"), add a
  longer pre-wait before sending digits.
- You can also push DTMF to an already-live call via `send_dtmf_to_active_call`.

Env vars expected
-----------------
TWILIO_ACCOUNT_SID
TWILIO_AUTH_TOKEN
TWILIO_FROM_NUMBER
REDIS_URL  (e.g., redis://:password@localhost:6379/0)
TWILIO_STATUS_CALLBACK_URL  (optional)
TWILIO_BYOC_TRUNK_SID       (optional)
"""
from __future__ import annotations

import os
from typing import Optional
import json
from twilio.rest import Client
from util.redis_client import redis_client

# --- Twilio client ----------------------------------------------------------
_account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
_auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
if not _account_sid or not _auth_token:
    raise RuntimeError("TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN must be set")

client = Client(_account_sid, _auth_token)

_FROM = os.environ.get("TWILIO_FROM_NUMBER")
if not _FROM:
    raise RuntimeError("TWILIO_FROM_NUMBER must be set (owned/verified number)")

_STATUS_CB = os.environ.get("TWILIO_STATUS_CALLBACK_URL")
_BYOC_TRUNK_SID = os.environ.get("TWILIO_BYOC_TRUNK_SID")  # optional


# --- Helpers ---------------------------------------------------------------

def _get_code_from_redis(number) -> str:
    """Return the verification code string stored at `key` in Redis.
    Raises KeyError if missing.
    """
    data = json.loads(redis_client.get(f"validation_{number}"))
    code = data["validation_code"]
    if code is None:
        raise KeyError(f"No code found in Redis for key: validation_{number}")
    return str(code).strip()


def _build_digits_sequence(code: str, pre_wait_seconds: float = 3.0, append_hash: bool = True) -> str:
    """Build a DTMF sequence for Twilio <Play digits="...">.

    - 'w' is a 0.5 second pause.
    - We prepend enough 'w' to equal `pre_wait_seconds`.
    - We insert short waits between digits to be safe on slow IVRs.
    - Optionally append '#', which many verification IVRs expect.
    """
    if pre_wait_seconds < 0:
        pre_wait_seconds = 0

    # Convert seconds to a count of 'w' (0.5s each)
    pre_wait_w = max(0, int(round(pre_wait_seconds / 0.5)))
    head = "w" * pre_wait_w

    # Insert a small pause between each tone for reliability
    # e.g., 1w between digits
    between = "w"
    body = between.join(list(code))

    tail = "#" if append_hash else ""
    return f"{head}{body}{tail}"


def _twiml_for_digits(digits: str) -> str:
    """Return minimal TwiML that sends the given DTMF digits."""
    # You can optionally keep an extra explicit pause using <Pause> if needed.
    return f"""
<Response>
  <Play digits="{digits}"/>
</Response>
""".strip()


# --- Public API ------------------------------------------------------------


#this is for outbounding and we need ti inbound the call and tell the code so this wont work

#instead we will store the code in redis when we buy the number and when the call comes in we will fetch the code from redis and send the dtmf

# we need to modify the view that takes the call and if there is no verification code just calls the number and if there is a code it sends the dtmf
def call_and_send_dtmf(
    to_number: str,
    redis_key: str,
    *,
    pre_wait_seconds: float = 3.0,
    append_hash: bool = True,
    status_callback_url: Optional[str] = None,
) -> str:
    """Place an outbound call and auto-send DTMF for the code in Redis.

    Returns the created Call SID.
    """
    code = _get_code_from_redis(redis_key)
    digits = _build_digits_sequence(code, pre_wait_seconds=pre_wait_seconds, append_hash=append_hash)
    twiml = _twiml_for_digits(digits)

    kwargs = dict(
        to=to_number,
        from_=_FROM,
        twiml=twiml,
    )

    # Route via BYOC if provided
    if _BYOC_TRUNK_SID:
        kwargs["byoc_trunk_sid"] = _BYOC_TRUNK_SID

    # Status callbacks for lifecycle tracking
    cb_url = status_callback_url or _STATUS_CB
    if cb_url:
        kwargs["status_callback"] = cb_url
        kwargs["status_callback_event"] = ["initiated", "ringing", "answered", "completed"]

    call = client.calls.create(**kwargs)
    return call.sid


def send_dtmf_to_active_call(call_sid: str, redis_key: str, *, pre_wait_seconds: float = 0.5, append_hash: bool = True) -> str:
    """Push DTMF to an already-connected call by updating TwiML mid-call.

    Returns the Call SID.
    """
    code = _get_code_from_redis(redis_key)
    digits = _build_digits_sequence(code, pre_wait_seconds=pre_wait_seconds, append_hash=append_hash)
    twiml = _twiml_for_digits(digits)

    call = client.calls(call_sid).update(twiml=twiml)
    return call.sid


# --- Convenience: common Redis key pattern ---------------------------------

def redis_key_for_number(number: str) -> str:
    """Standardize how you map a phone number to a Redis key for codes."""
    return f"verify:{number}"