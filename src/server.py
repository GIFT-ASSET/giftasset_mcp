import asyncio
import httpx
import json
import logging
from typing import Optional, Literal, List
from mcp.server.fastmcp import FastMCP
from .client import GiftAssetClient

# Configure basic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("giftasset-mcp")

# Initialize FastMCP Server
mcp = FastMCP("giftasset-analyst")
tg_client = GiftAssetClient()


@mcp.tool()
async def get_gift_info(slug: str) -> str:
    """
    Get all information about a specific Telegram Gift using its slug.
    
    Args:
        slug: Slug of the gift (e.g., 'plushpepe-1')
    """
    try:
        data = await tg_client.get_gift_info(slug=slug)
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
        data = await tg_client.get_market_actions(
            page=page, mode=mode, action_type=action_type,
            gift=gift, min_price=min_price, max_price=max_price, market=market
        )
        return json.dumps({"status": "success", "data": data}, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, indent=2)


@mcp.tool()
async def get_gifts_aggregator(
    page: int = 0,
    name: str = "All",
    model: str = "All",
    symbol: str = "All",
    backdrop: str = "All",
    number: Optional[int] = None,
    from_price: Optional[int] = None,
    to_price: Optional[int] = None,
    markets: Optional[List[str]] = None,
    blockchain_view: Optional[bool] = None,
    receiver: Optional[int] = None
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
        data = await tg_client.get_gifts_aggregator(
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
        data = await tg_client.get_unique_last_sales(
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
        data = await tg_client.get_all_collections_last_sale()
        return json.dumps({"status": "success", "data": data}, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, indent=2)


@mcp.tool()
async def get_gifts_update_stat() -> str:
    """
    Get statistics on gift improvements/upgrades per day.
    """
    try:
        data = await tg_client.get_gifts_update_stat()
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
    models: Optional[bool] = None,
    premarket: Optional[bool] = None
) -> str:
    """
    Get current floor prices for all gift collections across all marketplaces.

    Args:
        models: If True, return model-level prices instead of collection-level
        premarket: If True, filter to include only premarket collections
    """
    try:
        data = await tg_client.get_gifts_price_list(models=models, premarket=premarket)
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
        data = await tg_client.get_gifts_price_list_history(collection_name=collection_name)
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
        data = await tg_client.get_gift_by_name(name=name)
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
        data = await tg_client.get_all_collections_by_user(
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
        data = await tg_client.get_user_profile_price(
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
        data = await tg_client.get_gift_by_user(
            username=username,
            limit=limit, offset=offset
        )
        return json.dumps({"status": "success", "data": data}, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, indent=2)


if __name__ == "__main__":
    # Run the server using stdio transport (default for MCP)
    mcp.run(transport='stdio')
