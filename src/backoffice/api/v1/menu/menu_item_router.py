from fastapi import APIRouter, File, Form, UploadFile, status

from src.backoffice.apps.menu.schemas.menu_item import (
    MenuItemCreate,
    MenuItemResponse,
    MenuItemUpdate,
)
from src.backoffice.core.dependencies import AuthenticatedUserDep, MenuApplicationDep

router = APIRouter(prefix="/menu", tags=["menu-items"])


@router.post("/", response_model=MenuItemResponse, status_code=status.HTTP_201_CREATED)
async def create_menu_item(
    payload: MenuItemCreate,
    request_user: AuthenticatedUserDep,
    application: MenuApplicationDep,
):
    return await application.create_menu_item(payload, request_user.id)


@router.get("/", response_model=list[MenuItemResponse])
async def get_company_menu_items(
    company_subdomain: str,
    request_user: AuthenticatedUserDep,
    application: MenuApplicationDep,
):
    return await application.get_company_menu_items(
        company_subdomain=company_subdomain,
        user_id=request_user.id,
    )


@router.get("/{slug}", response_model=MenuItemResponse)
async def get_menu_item(
    slug: str,
    request_user: AuthenticatedUserDep,
    application: MenuApplicationDep,
):
    return await application.get_menu_item_by_slug(slug, request_user.id)


@router.patch("/{slug}", response_model=MenuItemResponse)
async def update_menu_item(
    slug: str,
    payload: MenuItemUpdate,
    request_user: AuthenticatedUserDep,
    application: MenuApplicationDep,
):
    return await application.update_menu_item(slug, payload, request_user.id)


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_menu_item(
    slug: str,
    request_user: AuthenticatedUserDep,
    application: MenuApplicationDep,
):
    await application.delete_menu_item(slug, request_user.id)


@router.post("/{slug}/images", response_model=MenuItemResponse)
async def add_image_to_menu_item(
    slug: str,
    request_user: AuthenticatedUserDep,
    application: MenuApplicationDep,
    file: UploadFile = File(..., description="Image file"),  # TODO вынести
    alt_text: str = Form(..., description="Alternative text"),
    is_primary: bool = Form(..., description="Is it the main image"),
    display_order: int = Form(..., description="Display order"),
):
    """
    Add an image to a menu item

    - **slug**: Menu item slug
    - **file**: Image file (jpg, png, gif, webp, bmp, svg)
    - **alt_text**: Alternative text for the image
    - **is_primary**: Set as the primary image
    - **display_order**: Display order (0 - first)
    """
    return await application.add_image_to_menu_item(
        menu_item_slug=slug,
        file=file,
        user_id=request_user.id,
        alt_text=alt_text,
        is_primary=is_primary,
        display_order=display_order,
    )


@router.delete("/{slug}/images/{image_id}", response_model=MenuItemResponse)
async def remove_image_from_menu_item(
    slug: str,
    image_id: int,
    request_user: AuthenticatedUserDep,
    application: MenuApplicationDep,
):
    """
    Remove image from menu item

    - **slug**: Menu item slug
    - **image_id**: Image ID to remove
    """
    return await application.remove_image_from_menu_item(
        menu_item_slug=slug, image_id=image_id, user_id=request_user.id
    )


@router.put("/{slug}/images/{image_id}/set-primary", response_model=MenuItemResponse)
async def set_primary_image_for_menu_item(
    slug: str,
    image_id: int,
    request_user: AuthenticatedUserDep,
    application: MenuApplicationDep,
):
    """
    Set the image as the primary image for the menu item

    - **slug**: Menu item slug
    - **image_id**: Image ID to set as the primary image
    """
    return await application.set_primary_image_for_menu_item(
        menu_item_slug=slug, image_id=image_id, user_id=request_user.id
    )
