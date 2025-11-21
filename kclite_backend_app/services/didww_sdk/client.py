from django.conf import settings
from .utils import _request


class DidwwClient:
    """
    Client for DIDWW API v3, reading creds from Django settings.
    """

    def __init__(self):
        try:    
            self.base_url = "https://api.didww.com/v3"
            self.headers = {
                "Accept": "application/vnd.api+json",
                "Content-Type": "application/vnd.api+json",
                "Api-Key": settings.DIDWW_API_KEY,
            }
        except Exception as e:
            raise Exception(f"Error initializing DIDWW client: {e}")

    def create_inbound_trunks(self,username,sip_domain_host):
        url = f"{self.base_url}/voice_in_trunks"
        payload = {
            "data": {
    "type": "voice_in_trunks",
    "attributes": {
      "priority": "1",
      "weight": "2",
      "capacity_limit": 10,
      "ringing_timeout": 30,
      "name": "Office",
      "cli_format": "e164",
      "cli_prefix": "+",
      "description": "custom description",
      "configuration": {
        "type": "sip_configurations",
        "attributes": {
          "username": username,
          "host": sip_domain_host,
          "codec_ids": [
            9,
            7
          ],
          "rx_dtmf_format_id": 1,
          "tx_dtmf_format_id": 1,
          "resolve_ruri": "true",
          "auth_enabled": True,
          "auth_user": "username",
          "auth_password": "password",
          "auth_from_user": "Office",
          "auth_from_domain": "example.com",
          "sst_enabled": "false",
          "sst_min_timer": 600,
          "sst_max_timer": 900,
          "sst_refresh_method_id": 1,
          "sst_accept_501": "true",
          "sip_timer_b": 8000,
          "dns_srv_failover_timer": 2000,
          "rtp_ping": "false",
          "rtp_timeout": 30,
          "force_symmetric_rtp": "false",
          "symmetric_rtp_ignore_rtcp": "false",
          "rerouting_disconnect_code_ids": [
            58,
            59
          ],
          "port": 5060,
          "transport_protocol_id": 2,
          "max_transfers": 0,
          "max_30x_redirects": 0,
          "media_encryption_mode": "disabled",
          "stir_shaken_mode": "disabled",
          "allowed_rtp_ips": None
        }
      }
    }
  }
        }
        return _request("POST", url, headers=self.headers, json=payload)
    
    def update_inbound_trunk(self, inbound_trunk_id, sip_domain_host,username,password):
        url = f"{self.base_url}/voice_in_trunks/{inbound_trunk_id}"
        payload = {
            "data": {
    "id": inbound_trunk_id,
    "type": "voice_in_trunks",
    "attributes": {
      "configuration": {
        "type": "sip_configurations",
        "attributes": {
          "username": username,
          "host": sip_domain_host,
          "auth_enabled": True,
          "auth_user": username,
          "auth_password": password
        }
      }
    }}}
        return _request("PATCH", url, headers=self.headers, json=payload)
        
    def create_outbound_trunks(self):
        url = f"{self.base_url}/voice_out_trunks"
        payload = {
            "data": {
    "type": "voice_out_trunks",
    "attributes": {
      "name": "Outbound trunk 11",
      "allowed_sip_ips": settings.DIDWW_ALLOWED_SIP_ADDRESS,
      "on_cli_mismatch_action": "send_original_cli",
      "capacity_limit": 100,
      "allow_any_did_as_cli": True,
      "status": "active",
      "threshold_amount": "9999.0",
      "default_dst_action": "allow_all",
      "dst_prefixes": ["23"],
      "media_encryption_mode": "disabled",
      "allowed_rtp_ips": settings.DIDWW_ALLOWED_RTP_ADDRESS,
      "force_symmetric_rtp": False,
      "rtp_ping": False
    }
  }
        }
        return _request("POST", url, headers=self.headers, json=payload)

    def attach_number_to_trunk(self,number_id,trunk_id):
        url = f"{self.base_url}/dids/{number_id}"
        payload = {
            "data": {
                "id": number_id,
                "type": "dids",
               "relationships": {
      "voice_in_trunk": {
        "data": {
          "type": "voice_in_trunks",
          "id": trunk_id
        }
      }
    }
            }
        }
        return _request("PATCH", url, headers=self.headers, json=payload)

    def list_available_dids(self, country=None, group=None, filters=None):
        """
        Returns a list of available DID numbers (strings) for the given country code.
        """
        url = f"{self.base_url}/available_dids"
        params = {}
        if country:
            country_id = self.get_country_id(country)
            params.update({"filter[country.id]": country_id})

        if group:
            group_id = self.get_group_id(group)
            params.update({"filter[did_group_type.id]": group_id})

        if filters:
            params.update(filters)

        data = _request("GET", url, headers=self.headers, params=params)
        items = data.get("data", [])
        if not items:
            return []
        return items

    def get_group_types(self, name: str = None) -> dict:
        """
        Retrieve DID group types, optionally filtering by name (e.g. "Local", "Toll-free").
        """
        url = f"{self.base_url}/did_group_types"
        params = {"filter[name]": name} if name else {}
        return _request("GET", url, headers=self.headers, params=params)

    def get_group_id(self, group_name: str) -> str:
        """
        Convenience: return the DIDWW UUID for the given group type.
        """
        data = self.get_group_types(group_name).get("data", [])
        if not data:
            raise ValueError(f"Didww group type not found: {group_name}")
        return data[0]["id"]

    def get_countries(self, iso: str) -> dict:
        """
        Retrieve country details by ISO code.
        """
        url = f"{self.base_url}/countries"
        params = {"filter[iso]": iso}
        return _request("GET", url, headers=self.headers, params=params)

    def get_country_id(self, iso: str) -> str:
        """
        Convenience: return the DIDWW UUID for the given ISO country code.
        """
        data = self.get_countries(iso).get("data", [])
        if not data:
            raise ValueError(f"Country not found: {iso}")
        return data[0]["id"]

    def get_did_sku_id(self, did_id: str) -> str:
        url = f"{self.base_url}/available_dids/{did_id}"
        params = {"include": "did_group.stock_keeping_units"}
        resp = _request("GET", url, headers=self.headers, params=params)
        # Filter included items for type == "stock_keeping_units"
        for inc in resp.get("included", []):
            if inc.get("type") == "stock_keeping_units":
                return inc["id"]
        raise ValueError(f"No SKUs found for DID {did_id}")

    def list_did_groups(
        self,
        country_id: str,
        group_type_id: str = None,
        city_id: str = None,
        include_skus: bool = True,
        available_only: bool = True,
    ) -> dict:
        """
        List DID groups (number inventories) for a specific region.
        Optionally filter by group type (Local/Toll-free) and city.
        Includes stock_keeping_units if include_skus=True.
        """
        url = f"{self.base_url}/did_groups"
        params = {"filter[country.id]": country_id}
        if group_type_id:
            params["filter[did_group_type.id]"] = group_type_id
        if city_id:
            params["filter[city.id]"] = city_id
        if available_only:
            params["filter[is_available]"] = True
        if include_skus:
            params["include"] = "stock_keeping_units"
        return _request("GET", url, headers=self.headers, params=params)

    def extract_skus(self, did_groups_response: dict) -> list[dict]:
        """
        From a did_groups response, extract the included SKUs with pricing details.
        """
        skus = []
        included = did_groups_response.get("included", [])
        for item in included:
            if item.get("type") == "stock_keeping_units":
                attr = item.get("attributes", {})
                skus.append(
                    {
                        "id": item["id"],
                        "setup_price": attr.get("setup_price"),
                        "monthly_price": attr.get("monthly_price"),
                        "channels_included_count": attr.get("channels_included_count"),
                    }
                )
        return skus

    def create_order(
        self,
        sku_id: str,
        available_did_id: str = None,
    ) -> dict:
        """
        Place an order to purchase DID(s) under a given SKU.
        Optionally bind to an existing did_reservation_id for specific numbers.
        """
        url = f"{self.base_url}/orders"
        item_attrs = {
            "sku_id": sku_id,
            "available_did_id": available_did_id,
            # "qty": qty,
            # "allow_back_ordering": allow_back_ordering,
        }

        payload = {
            "data": {
                "type": "orders",
                "attributes": {
                    # "allow_back_ordering": False,
                    "items": [{"type": "did_order_items", "attributes": item_attrs}],
                },
            }
        }
        return _request("POST", url, headers=self.headers, json=payload)

    def buy_number(
        self,
        did_id: str,
    ) -> dict:
        """
        Convenience wrapper: full purchase flow for buying a DID number.

        :param did_id: DIDWW id
        :returns: Order response dict.
        """
        sku_id = self.get_did_sku_id(did_id)

        # 5) Place the order with the first SKU
        return self.create_order(
            sku_id=sku_id,
            available_did_id=did_id,
        )

    def send_sms(self, originator: str, destination: str, text: str) -> dict:
        """
        Send an outbound SMS via DIDWW HTTP Outbound SMS API.

        Uses the separate SMS-out endpoint and Basic Auth credentials
        from your HTTP-OUT trunk.
        """
        # SMS-out endpoint (single-SMS)
        url = settings.DIDWW_SMS_TRUNK_HOST

        payload = {
            "data": {
                "type": "outbound_messages",
                "attributes": {
                    "destination": destination,
                    "source": originator,
                    "content": text,
                },
            }
        }
        headers = {
            "Content-Type": "application/vnd.api+json",
        }
        # Use trunk credentials, not the API-Key header
        auth = (
            settings.DIDWW_SMS_TRUNK_USERNAME,
            settings.DIDWW_SMS_TRUNK_PASSWORD,
        )
        return _request("POST", url, headers=headers, json=payload, auth=auth)
