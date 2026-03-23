"""API routes for items CRUD operations."""

from fastapi import APIRouter, Depends, Query, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import log_audit_event, persist_audit_event
from app.core.auth import get_current_user_id
from app.core.database import get_db
from app.core.rate_limit import limiter
from app.items.schemas import (
    ItemCreate,
    ItemListResponse,
    ItemResponse,
    ItemStatusType,
    ItemUpdate,
)
from app.items.service import (
    SortDir,
    SortField,
    create_item,
    delete_item,
    get_item,
    list_items,
    update_item,
)

router = APIRouter(prefix="/items", tags=["items"])


@router.get("", response_model=ItemListResponse)
@limiter.limit("60/minute")
async def list_items_route(
    request: Request,
    user_id: str = Depends(get_current_user_id),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: str | None = Query(
        None, description="Search items by title or description"
    ),
    sort_by: SortField = Query("created_at", description="Sort by field"),
    sort_dir: SortDir = Query("desc", description="Sort direction"),
    status: ItemStatusType | None = Query(None, description="Filter by status"),
    db: AsyncSession = Depends(get_db),
) -> ItemListResponse:
    """List items with search, sort, filter, and pagination."""
    skip = (page - 1) * limit
    items, total = await list_items(
        db,
        user_id=user_id,
        skip=skip,
        limit=limit,
        search=search,
        sort_by=sort_by,
        sort_dir=sort_dir,
        status=status,
    )
    log_audit_event(
        user_id=user_id, action="list", resource_type="item", resource_id="*"
    )
    return ItemListResponse(
        items=[ItemResponse.model_validate(item) for item in items],
        total=total,
    )


@router.post("", response_model=ItemResponse, status_code=201)
@limiter.limit("30/minute")
async def create_item_route(
    request: Request,
    data: ItemCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ItemResponse:
    """Create a new item for the authenticated user."""
    item = await create_item(db, user_id=user_id, data=data)
    await persist_audit_event(
        db, user_id=user_id, action="create", resource_type="item", resource_id=item.id
    )
    return ItemResponse.model_validate(item)


@router.get("/{item_id}", response_model=ItemResponse)
@limiter.limit("60/minute")
async def get_item_route(
    request: Request,
    item_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ItemResponse:
    """Get a single item by ID."""
    item = await get_item(db, item_id=item_id, user_id=user_id)
    log_audit_event(
        user_id=user_id, action="read", resource_type="item", resource_id=item_id
    )
    return ItemResponse.model_validate(item)


@router.patch("/{item_id}", response_model=ItemResponse)
@limiter.limit("30/minute")
async def update_item_route(
    request: Request,
    item_id: str,
    data: ItemUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ItemResponse:
    """Update an existing item with partial data."""
    item = await update_item(db, item_id=item_id, user_id=user_id, data=data)
    await persist_audit_event(
        db, user_id=user_id, action="update", resource_type="item", resource_id=item_id
    )
    return ItemResponse.model_validate(item)


@router.delete("/{item_id}", status_code=204)
@limiter.limit("30/minute")
async def delete_item_route(
    request: Request,
    item_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Delete an item by ID."""
    await delete_item(db, item_id=item_id, user_id=user_id)
    await persist_audit_event(
        db, user_id=user_id, action="delete", resource_type="item", resource_id=item_id
    )
    return Response(status_code=204)
