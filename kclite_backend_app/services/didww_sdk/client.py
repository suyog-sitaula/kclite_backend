from django.conf import settings
from .utils import _request


class DidwwClient:
    """
    Client for DIDWW API v3, reading creds from Django settings.
    """

    def __init__(self):
        self.base_url = "https://api.didww.com/v3"
        self.headers = {
            "Accept": "application/vnd.api+json",
            "Content-Type": "application/vnd.api+json",
            "Api-Key": settings.DIDWW_API_KEY,
        }

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
