"""API routes for items CRUD operations."""

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user_id
from app.core.database import get_db
from app.items.schemas import ItemCreate, ItemListResponse, ItemResponse, ItemUpdate
from app.items.service import create_item, delete_item, get_item, list_items, update_item

router = APIRouter(prefix="/items", tags=["items"])


@router.get("", response_model=ItemListResponse)
async def list_items_route(
    user_id: str = Depends(get_current_user_id),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> ItemListResponse:
    """List items for the authenticated user with pagination."""
    skip = (page - 1) * limit
    items, total = await list_items(db, user_id=user_id, skip=skip, limit=limit)
    return ItemListResponse(
        items=[ItemResponse.model_validate(item) for item in items],
        total=total,
    )


@router.post("", response_model=ItemResponse, status_code=201)
async def create_item_route(
    data: ItemCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ItemResponse:
    """Create a new item for the authenticated user."""
    item = await create_item(db, user_id=user_id, data=data)
    return ItemResponse.model_validate(item)


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item_route(
    item_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ItemResponse:
    """Get a single item by ID."""
    item = await get_item(db, item_id=item_id, user_id=user_id)
    return ItemResponse.model_validate(item)


@router.patch("/{item_id}", response_model=ItemResponse)
async def update_item_route(
    item_id: str,
    data: ItemUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ItemResponse:
    """Update an existing item with partial data."""
    item = await update_item(db, item_id=item_id, user_id=user_id, data=data)
    return ItemResponse.model_validate(item)


@router.delete("/{item_id}", status_code=204)
async def delete_item_route(
    item_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Delete an item by ID."""
    await delete_item(db, item_id=item_id, user_id=user_id)
    return Response(status_code=204)
