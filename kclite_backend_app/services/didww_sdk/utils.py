# utils.py
import requests
from django.conf import settings
from .exceptions import DidwwAPIError

import requests
from django.conf import settings
from .exceptions import DidwwAPIError


def _request(method, url, headers=None, params=None, json=None, auth=None):
    """
    Wrapper around requests.request, raising DidwwAPIError on non-2xx.
    Automatically injects:
      - Basic Auth (username/password) when calling your SMS trunk host
      - Api-Key header when calling the DIDWW v3 JSON API
    """
    # -----------------------------
    # 1) Decide which credentials to use
    # -----------------------------
    sms_host = settings.DIDWW_SMS_TRUNK_HOST.rstrip("/")
    if url.startswith(sms_host):
        # SMS‐OUT trunk: Basic Auth + only Content-Type
        auth = (
            settings.DIDWW_SMS_TRUNK_USERNAME,
            settings.DIDWW_SMS_TRUNK_PASSWORD,
        )
        headers = {"Content-Type": "application/vnd.api+json"}
    else:
        # DIDWW v3 JSON‑API: Api‑Key header (keep any Accept/Content-Type set by caller)
        headers = headers.copy() if headers else {}
        headers["Api-Key"] = settings.DIDWW_API_KEY

    # -----------------------------
    # 2) Make the HTTP request
    # -----------------------------
    response = requests.request(
        method=method,
        url=url,
        headers=headers,
        params=params,
        json=json,
        auth=auth,
    )

    # -----------------------------
    # 3) Error handling
    # -----------------------------
    if not response.ok:
        try:
            error_body = response.json()
        except ValueError:
            error_body = response.text
        raise DidwwAPIError(response.status_code, error_body)

    return response.json()
