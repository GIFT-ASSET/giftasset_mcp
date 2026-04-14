import asyncio
import httpx
import json
import logging
import os
from collections import OrderedDict
from typing import Optional, Literal, List
from mcp.server.fastmcp import FastMCP
from .client import GiftAssetClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("giftasset-mcp")

mcp = FastMCP("giftasset-analyst")

_CLIENT_CACHE_MAX = int(os.getenv("MCP_CLIENT_CACHE_MAX", "128"))
_clients: "OrderedDict[str, GiftAssetClient]" = OrderedDict()

def _get_api_key() -> str:
    # In HTTP/SSE transports, allow per-request API key via header.
    try:
        ctx = mcp.get_context()
        req = ctx.request_context.request  # Starlette Request in HTTP/SSE
        key = req.headers.get("x-api-key") or req.headers.get("x-api-token")
        if key:
            return key
    except Exception:
        pass
    return os.environ.get("GIFTASSET_API_KEY", "")

def tg_client() -> GiftAssetClient:
    key = _get_api_key()
    client = _clients.get(key)
    if client is not None:
        _clients.move_to_end(key)
        return client
    client = GiftAssetClient(api_key=key)
    _clients[key] = client
    while len(_clients) > _CLIENT_CACHE_MAX:
        _, evicted = _clients.popitem(last=False)
        try:
            asyncio.get_running_loop().create_task(evicted.aclose())
        except RuntimeError:
            pass
    return client


@mcp.tool()
async def get_gift_info(slug: str) -> str:
    """
    Get all information about a specific Telegram Gift using its slug.
    
    Args:
        slug: Slug of the gift (e.g., 'plushpepe-1')
    """
    try:
        data = await tg_client().get_gift_info(slug=slug)
        return json.dumps({"status": "success", "data": data}, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, indent=2)


@mcp.tool()
async def get_market_actions(
    page: int = 0,
    mode: Literal["collection_number", "collection", "number", "model", "pattern", "backdrop"] = "collection_number",
    action_type: Literal["buy", "listing", "change_price"] = "buy",
    gift: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    market: Optional[str] = None
) -> str:
    """
    Get aggregated market actions (buys, listings, price changes) for gifts.
    
    Args:
        page: Page number for pagination
        mode: Grouping mode for market aggregation
        action_type: Market action type ('buy', 'listing', 'change_price')
        gift: Optional gift identifier (slug or URL)
        min_price: Optional minimum price filter in TON
        max_price: Optional maximum price filter in TON
        market: Optional market filter ('offchain', etc)
    """
    try:
        data = await tg_client().get_market_actions(
            page=page, mode=mode, action_type=action_type,
            gift=gift, min_price=min_price, max_price=max_price, market=market
        )
        return json.dumps({"status": "success", "data": data}, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, indent=2)


@mcp.tool()
async def get_gifts_aggregator(
    receiver: int,
    page: int = 0,
    name: str = "All",
    model: str = "All",
    symbol: str = "All",
    backdrop: str = "All",
    number: Optional[int] = None,
    from_price: Optional[int] = None,
    to_price: Optional[int] = None,
    markets: Optional[List[str]] = None,
    blockchain_view: Optional[bool] = None
) -> str:
    """
    Get filtered NFT gift aggregator data. Returns unified NFTs lists from various markets.
    
    Args:
        page: Page number to fetch
        name: NFT name filter (use 'All' to disable)
        model: Model name filter (use 'All' to disable)
        symbol: Symbol name filter (use 'All' to disable)
        backdrop: Backdrop name filter (use 'All' to disable)
        number: Specific gift number
        from_price: Minimum price filter
        to_price: Maximum price filter
        markets: List of specific markets ['tonnel', 'portals', 'fragment']
        blockchain_view: Filter by blockchain view availability
        receiver: Receiver telegram_id
    """
    try:
        data = await tg_client().get_gifts_aggregator(
            page=page, name=name, model=model, symbol=symbol, backdrop=backdrop,
            number=number, from_price=from_price, to_price=to_price,
            markets=markets, blockchain_view=blockchain_view, receiver=receiver
        )
        return json.dumps({"status": "success", "data": data}, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, indent=2)


@mcp.tool()
async def get_unique_last_sales(
    collection_name: str,
    limit: int = 10,
    model_name: Optional[str] = None
) -> str:
    """
    Get unique last sales for a specific collection.
    
    Args:
        collection_name: Name of the collection (e.g., 'Evil Eye')
        limit: Number of gifts to return
        model_name: Optional model name filter
    """
    try:
        data = await tg_client().get_unique_last_sales(
            collection_name=collection_name, limit=limit, model_name=model_name
        )
        return json.dumps({"status": "success", "data": data}, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, indent=2)


@mcp.tool()
async def get_all_collections_last_sale() -> str:
    """
    Get last sale on providers for all collections.
    """
    try:
        data = await tg_client().get_all_collections_last_sale()
        return json.dumps({"status": "success", "data": data}, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, indent=2)


@mcp.tool()
async def get_gifts_update_stat() -> str:
    """
    Get statistics on gift improvements/upgrades per day.
    """
    try:
        data = await tg_client().get_gifts_update_stat()
        return json.dumps({"status": "success", "data": data}, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, indent=2)

@mcp.tool()
async def get_ton_price() -> str:
    """
    Get the current price of TON (The Open Network) in USD.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("https://tonapi.io/v2/rates?tokens=ton&currencies=usd")
            response.raise_for_status()
            data = response.json()
            ton_data = data.get("rates", {}).get("TON", {})
            return json.dumps({"status": "success", "data": ton_data}, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, indent=2)

@mcp.tool()
async def get_gifts_price_list(
    models: bool = False,
    premarket: bool = False
) -> str:
    """
    Get current floor prices for all gift collections across all marketplaces.

    Args:
        models: If True, return model-level prices instead of collection-level (default: False)
        premarket: If True, filter to include only premarket collections (default: False)
    """
    try:
        data = await tg_client().get_gifts_price_list(models=models, premarket=premarket)
        return json.dumps({"status": "success", "data": data}, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, indent=2)


@mcp.tool()
async def get_gifts_price_list_history(
    collection_name: Optional[str] = None
) -> str:
    """
    Get historical price data for gift collections with 24h and 7d timeframes.

    Args:
        collection_name: Name of a specific collection to retrieve history for (e.g., 'Loot Bag'). Omit for all collections.
    """
    try:
        data = await tg_client().get_gifts_price_list_history(collection_name=collection_name)
        return json.dumps({"status": "success", "data": data}, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, indent=2)


@mcp.tool()
async def get_gift_by_name(name: str) -> str:
    """
    Get a specific gift by its exact name.
    
    Args:
        name: Exact name of the gift (e.g., 'EasterEgg-1')
    """
    try:
        data = await tg_client().get_gift_by_name(name=name)
        return json.dumps({"status": "success", "data": data}, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, indent=2)


@mcp.tool()
async def get_all_collections_by_user(
    username: Optional[str] = None,
    telegram_id: Optional[int] = None,
    include: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
    limit: int = 100,
    offset: int = 0
) -> str:
    """
    Get all collections owned by a specific Telegram user with filtering options.
    Must provide either username or telegram_id.
    
    Args:
        username: Telegram username (without @)
        telegram_id: Telegram numeric ID
        include: List of collection names to include
        exclude: List of collection names to exclude
        limit: Pagination limit
        offset: Pagination offset
    """
    try:
        data = await tg_client().get_all_collections_by_user(
            username=username, telegram_id=telegram_id,
            include=include, exclude=exclude,
            limit=limit, offset=offset
        )
        return json.dumps({"status": "success", "data": data}, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, indent=2)


@mcp.tool()
async def get_user_profile_price(
    username: Optional[str] = None,
    telegram_id: Optional[int] = None,
    limit: int = 5,
    offset: int = 0
) -> str:
    """
    Get the total profile price and top gifts for a specific Telegram user.
    Returns total profile value across different markets (getgems, portals, tonnel) 
    calculated both by collection floor price (total_collection_price) and 
    model floor price (total_model_price), along with the list of their top gifts 
    with detailed market data.
    Must provide either username or telegram_id.
    
    Args:
        username: Telegram username (without @)
        telegram_id: Telegram numeric ID
        limit: Number of top gifts to return
        offset: Pagination offset

    IMPORTANT FOR LLM: The 'total_collection_price' and 'total_model_price' are calculated ONLY 
    for the gifts returned in the current page (within the specified limit). To get the 
    absolute total cost for a profile with many gifts, you MUST iterate through all 
    pages using offsets and sum the values manually.
    """
    try:
        data = await tg_client().get_user_profile_price(
            username=username, telegram_id=telegram_id,
            limit=limit, offset=offset
        )
        return json.dumps({"status": "success", "data": data}, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, indent=2)


@mcp.tool()
async def get_gift_by_user(
    username: Optional[str] = None,
    limit: int = 10,
    offset: int = 0
) -> str:
    """
    Get a detailed list of gifts owned by a specific Telegram user, including market prices,
    rarity attributes, and provider statistics.
    Must provide either username or telegram_id.
    
    Args:
        username: Telegram username (without @)
        limit: Number of gifts to return
        offset: Pagination offset
    """
    try:
        data = await tg_client().get_gift_by_user(
            username=username,
            limit=limit, offset=offset
        )
        return json.dumps({"status": "success", "data": data}, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, indent=2)


@mcp.tool()
async def get_unique_gifts_price_list(
    collection_name: str
) -> str:
    """
    Get information on collection gift prices.
    
    Args:
        collection_name: Name of the collection (e.g., 'Loot Bag')
    """
    try:
        data = await tg_client().get_unique_gifts_price_list(collection_name=collection_name)
        return json.dumps({"status": "success", "data": data}, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, indent=2)


@mcp.tool()
async def get_gifts_collections_emission() -> str:
    """
    Get information about unique gifts issue inside collections.
    """
    try:
        data = await tg_client().get_gifts_collections_emission()
        return json.dumps({"status": "success", "data": data}, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, indent=2)


@mcp.tool()
async def get_gifts_collections_marketcap() -> str:
    """
    Get the market-cap of gifts.
    """
    try:
        data = await tg_client().get_gifts_collections_marketcap()
        return json.dumps({"status": "success", "data": data}, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, indent=2)


@mcp.tool()
async def get_gifts_collections_health_index() -> str:
    """
    Get collection health index (liquidity, mcap, whales).
    """
    try:
        data = await tg_client().get_gifts_collections_health_index()
        return json.dumps({"status": "success", "data": data}, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, indent=2)


@mcp.tool()
async def get_gifts_collections_greed_index() -> str:
    """
    Get greed index (hidden, upgraded, owners).
    """
    try:
        data = await tg_client().get_gifts_collections_greed_index()
        return json.dumps({"status": "success", "data": data}, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, indent=2)


@mcp.tool()
async def get_providers_volumes() -> str:
    """
    Get providers' sales volumes.
    """
    try:
        data = await tg_client().get_providers_volumes()
        return json.dumps({"status": "success", "data": data}, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, indent=2)


if __name__ == "__main__":
    transport = os.getenv("MCP_TRANSPORT", "stdio").lower()
    if transport not in ("stdio", "sse", "streamable-http"):
        raise SystemExit(f"Invalid MCP_TRANSPORT={transport!r}. Use stdio | sse | streamable-http")
    if transport == "stdio":
        mcp.run(transport="stdio")
    else:
        mcp.settings.host = os.getenv("MCP_HOST", "0.0.0.0")
        mcp.settings.port = int(os.getenv("MCP_PORT", "8000"))
        logger.info(f"Starting MCP over {transport} on {mcp.settings.host}:{mcp.settings.port}")
        mcp.run(transport=transport)
