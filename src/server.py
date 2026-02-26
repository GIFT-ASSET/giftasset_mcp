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
async def get_user_gifts(
    username: Optional[str] = None,
    telegram_id: Optional[int] = None,
    limit: int = 50,
    offset: int = 0
) -> str:
    """
    Get a paginated list of NFT gifts owned by a specific Telegram user.
    Must provide either username or telegram_id.
    
    Args:
        username: Telegram username (without @)
        telegram_id: Telegram numeric ID
        limit: Number of gifts to return (1-50)
        offset: Pagination offset
    """
    try:
        data = await tg_client.get_user_gifts(
            username=username, telegram_id=telegram_id, 
            limit=limit, offset=offset
        )
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


if __name__ == "__main__":
    # Run the server using stdio transport (default for MCP)
    mcp.run(transport='stdio')
