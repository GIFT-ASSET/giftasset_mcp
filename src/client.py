import httpx
import logging
import os
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

BASE_URL = "https://api.giftasset.dev/"

class GiftAssetClient:
    def __init__(self):
        # We need an API key for the new Swagger spec endpoints. Get it via @giftassetmcp_bot
        self.api_key = os.environ.get("GIFTASSET_API_KEY", "")
        if not self.api_key:
            logger.warning("GIFTASSET_API_KEY environment variable is not set. API calls might fail with 403 Forbidden. Get your key from @giftassetmcp_bot")
            
        headers = {"x-api-token": self.api_key} if self.api_key else {}
        self.client = httpx.AsyncClient(base_url=BASE_URL, headers=headers, timeout=30.0)

    async def _request(self, method: str, endpoint: str, params: Optional[Dict] = None, json_data: Optional[Dict] = None) -> Any:
        try:
            response = await self.client.request(method, endpoint, params=params, json=json_data)
            
            # Special handling for SwiftGifts 4XXs to return JSON errors properly
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                    raise Exception(f"API Error {response.status_code}: {error_data}")
                except Exception as parse_e:
                    response.raise_for_status()

            data = response.json()
            if data and isinstance(data, dict) and "ok" in data and not data["ok"]:
                logger.error(f"API returned not ok: {data}")
                raise Exception(f"API Error: {data.get('description', 'Unknown error')}")
            return data.get("result", data) if isinstance(data, dict) else data
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {e}")
            raise Exception(f"HTTP Error {e.response.status_code}: {e.response.text}")
        except httpx.RequestError as e:
            logger.error(f"Request error occurred: {e}")
            raise Exception(f"Connection Error: Could not reach GiftAsset API. {str(e)}")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            raise Exception(f"Unexpected Error: {str(e)}")

    def _truncate_list(self, data: Any, limit: int = 15) -> Any:
        """Truncate large lists to prevent context window overflow."""
        if isinstance(data, list):
            if len(data) > limit:
                return {
                    "items": data[:limit], 
                    "note": f"List truncated: showing top {limit} out of {len(data)} items due to context limits."
                }
            return data
        elif isinstance(data, dict):
            # Known list keys in new openapi JSON schemas
            for key in ["items", "markets", "gifts"]:
                if key in data and isinstance(data[key], list):
                    if len(data[key]) > limit:
                        data[key] = data[key][:limit]
                        data["note"] = f"'{key}' truncated to top {limit} items"
            return data
        return data

    async def get_gift_info(self, slug: str) -> Any:
        """POST /api/gifts"""
        payload = {"slug": slug}
        data = await self._request("POST", "/api/gifts", json_data=payload)
        return self._truncate_list(data, limit=20)

    async def get_market_actions(self, 
                               page: int = 0, 
                               mode: str = "collection_number", 
                               action_type: str = "buy",
                               gift: Optional[str] = None,
                               min_price: Optional[float] = None,
                               max_price: Optional[float] = None,
                               market: Optional[str] = None) -> Any:
        """POST /api/actions/markets"""
        params = {"page": page, "mode": mode}
        payload = {"type": action_type}
        if gift: payload["gift"] = gift
        if min_price is not None: payload["min_price"] = min_price
        if max_price is not None: payload["max_price"] = max_price
        if market: payload["market"] = market

        data = await self._request("POST", "/api/actions/markets", params=params, json_data=payload)
        return self._truncate_list(data, limit=15)

    async def get_gifts_aggregator(self,
                                 page: int,
                                 name: str = "All",
                                 model: str = "All",
                                 symbol: str = "All",
                                 backdrop: str = "All",
                                 number: Optional[int] = None,
                                 from_price: Optional[int] = None,
                                 to_price: Optional[int] = None,
                                 markets: List[str] = None,
                                 blockchain_view: Optional[bool] = None,
                                 receiver: Optional[int] = None) -> Any:
        """POST /api/aggregator"""
        params = {"page": page}
        
        # Build payload based on the working example
        payload = {
            "name": name,
            "model": model,
            "symbol": symbol,
            "backdrop": backdrop,
            "number": number,
            "from_price": from_price,
            "to_price": to_price,
            "market": markets if markets is not None else None,
            "blochainView": blockchain_view if blockchain_view is not None else None,
            "receiver": receiver
        }

        data = await self._request("POST", "/api/aggregator", params=params, json_data=payload)
        return self._truncate_list(data, limit=20)

    async def get_unique_last_sales(self, collection_name: str, limit: int = 10, model_name: Optional[str] = None) -> Any:
        """GET /api/v1/gifts/get_unique_last_sales"""
        params = {"collection_name": collection_name, "limit": limit}
        if model_name: params["model_name"] = model_name
        data = await self._request("GET", "/api/v1/gifts/get_unique_last_sales", params=params)
        return self._truncate_list(data, limit=limit)

    async def get_all_collections_last_sale(self) -> Any:
        """GET /api/v1/gifts/get_all_collections_last_sale"""
        data = await self._request("GET", "/api/v1/gifts/get_all_collections_last_sale")
        return self._truncate_list(data, limit=20)

    async def get_gifts_update_stat(self) -> Any:
        """GET /api/v1/gifts/get_gifts_update_stat"""
        data = await self._request("GET", "/api/v1/gifts/get_gifts_update_stat")
        return self._truncate_list(data, limit=20)

    async def get_user_gifts(self, 
                           username: Optional[str] = None,
                           telegram_id: Optional[int] = None,
                           limit: int = 50,
                           offset: int = 0) -> Any:
        """GET /api/user_gifts"""
        if not username and not telegram_id:
            raise ValueError("Must provide either username or telegram_id")
            
        params = {"limit": limit, "offset": offset}
        if username: params["username"] = username
        if telegram_id: params["telegram_id"] = telegram_id

        data = await self._request("GET", "/api/user_gifts", params=params)
        return self._truncate_list(data, limit=20)
