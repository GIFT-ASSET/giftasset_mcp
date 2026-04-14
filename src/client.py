import httpx
import logging
import os
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

BASE_URL = os.environ.get("GIFTASSET_API_URL", "https://api.giftasset.dev/")

class GiftAssetClient:
    def __init__(self, api_key: Optional[str] = None):
        # We need an API key for the new Swagger spec endpoints. Get it via @giftassetmcp_bot
        self.api_key = api_key if api_key is not None else os.environ.get("GIFTASSET_API_KEY", "")
        if not self.api_key:
            logger.warning("No API key provided (env GIFTASSET_API_KEY or request header). API calls might fail with 403 Forbidden. Get your key from @giftassetmcp_bot")
            
        headers = {
            "x-api-token": self.api_key,
            "Accept-Encoding": "gzip, deflate"
        } if self.api_key else {
            "Accept-Encoding": "gzip, deflate"
        }
        self.client = httpx.AsyncClient(base_url=BASE_URL, headers=headers, timeout=30.0)

    async def aclose(self) -> None:
        await self.client.aclose()

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

    def _truncate_list(self, data: Any, limit: int = 100) -> Any:
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
        return self._truncate_list(data)

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
                                 receiver: int,
                                 name: str = "All",
                                 model: str = "All",
                                 symbol: str = "All",
                                 backdrop: str = "All",
                                 number: Optional[int] = None,
                                 from_price: Optional[int] = None,
                                 to_price: Optional[int] = None,
                                 markets: Optional[List[str]] = None,
                                 blockchain_view: Optional[bool] = None) -> Any:
        """POST /api/aggregator"""
        params = {"page": page}
        
        # Build payload based on the working example
        payload = {
            "page": page,  # Some endpoints might expect page in payload too
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
        return self._truncate_list(data)

    async def get_gifts_price_list(self, models: Optional[bool] = None, premarket: Optional[bool] = None) -> Any:
        # API requires models and premarket to be present as strings "true"/"false"
        params = {
            "models": str(models if models is not None else False).lower(),
            "premarket": str(premarket if premarket is not None else False).lower()
        }
        
        data = await self._request("GET", "/api/v1/gifts/get_gifts_price_list", params=params)
        return self._truncate_list(data, limit=30)

    async def get_gifts_price_list_history(self, collection_name: Optional[str] = None) -> Any:
        """GET /api/v1/gifts/get_gifts_price_list_history"""
        params = {}
        if collection_name: params["collection_name"] = collection_name
        data = await self._request("GET", "/api/v1/gifts/get_gifts_price_list_history", params=params)
        return self._truncate_list(data, limit=20)

    async def get_gift_by_name(self, name: str) -> Any:
        """GET /api/v1/gifts/get_gift_by_name"""
        params = {"name": name}
        data = await self._request("GET", "/api/v1/gifts/get_gift_by_name", params=params)
        return self._truncate_list(data)

    async def get_all_collections_by_user(
        self,
        username: Optional[str] = None,
        telegram_id: Optional[int] = None,
        include: Optional[List[str]] = None,
        exclude: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Any:
        """POST /api/v1/gifts/get_all_collections_by_user"""
        if not username and not telegram_id:
            raise ValueError("Must provide either username or telegram_id")
            
        params = {}
        if username: params["username"] = username
        if telegram_id: params["telegram_id"] = telegram_id
            
        payload = {
            "limit": limit,
            "offset": offset
        }
        if include is not None: payload["include"] = include
        if exclude is not None: payload["exclude"] = exclude
            
        data = await self._request("POST", "/api/v1/gifts/get_all_collections_by_user", params=params, json_data=payload)
        return self._truncate_list(data)

    async def get_user_profile_price(
        self,
        username: Optional[str] = None,
        telegram_id: Optional[int] = None,
        limit: int = 5,
        offset: int = 0
    ) -> Any:
        """
        GET /api/v1/gifts/get_user_profile_price
        
        NOTE FOR LLM: The totals (total_collection_price, total_model_price) in the response 
        are SUMS of prices for the gifts in the current page ONLY. If the user has more 
        than 'limit' gifts, you must fetch all pages using 'offset' to calculate 
        the full profile value.
        """
        if not username and not telegram_id:
            raise ValueError("Must provide either username or telegram_id")
            
        params = {"limit": limit, "offset": offset}
        if username: params["username"] = username
        if telegram_id: params["telegram_id"] = telegram_id

        data = await self._request("GET", "/api/v1/gifts/get_user_profile_price", params=params)
        return self._truncate_list(data)

    async def get_gift_by_user(
        self,
        username: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> Any:
        """GET /api/v1/gifts/get_gift_by_user"""
        if not username:
            raise ValueError("Must provide username")
            
        params = {"limit": limit, "offset": offset}
        if username: params["username"] = username

        data = await self._request("GET", "/api/v1/gifts/get_gift_by_user", params=params)
        return self._truncate_list(data)

    async def get_unique_gifts_price_list(self, collection_name: str) -> Any:
        """GET /api/v1/gifts/get_unique_gifts_price_list"""
        params = {"collection_name": collection_name}
        data = await self._request("GET", "/api/v1/gifts/get_unique_gifts_price_list", params=params)
        return self._truncate_list(data)

    async def get_gifts_collections_emission(self) -> Any:
        """GET /api/v1/gifts/get_gifts_collections_emission"""
        data = await self._request("GET", "/api/v1/gifts/get_gifts_collections_emission")
        return self._truncate_list(data, limit=50)

    async def get_gifts_collections_marketcap(self) -> Any:
        # GET /api/v1/gifts/get_gifts_collections_marketcap
        data = await self._request("GET", "/api/v1/gifts/get_gifts_collections_marketcap")
        return self._truncate_list(data, limit=50)

    async def get_gifts_collections_health_index(self) -> Any:
        # GET /api/v1/gifts/get_gifts_collections_health_index
        data = await self._request("GET", "/api/v1/gifts/get_gifts_collections_health_index")
        return self._truncate_list(data, limit=50)

    async def get_gifts_collections_greed_index(self) -> Any:
        # GET /api/v1/gifts/get_gifts_collections_greed_index
        data = await self._request("GET", "/api/v1/gifts/get_gifts_collections_greed_index")
        return self._truncate_list(data, limit=50)

    async def get_providers_volumes(self) -> Any:
        # GET /api/v1/gifts/get_providers_volumes
        data = await self._request("GET", "/api/v1/gifts/get_providers_volumes")
        return self._truncate_list(data)
