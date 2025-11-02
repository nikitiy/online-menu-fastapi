from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class MenuItemBase(BaseModel):
    """Base menu item schema"""

    name: str = Field(..., min_length=1, max_length=255, description="Name")
    description: str = Field(..., min_length=1, description="Description")
    category_id: int = Field(..., description="Category ID")
    grams: int = Field(..., gt=0, description="Grams")
    kilocalories: Optional[int] = Field(None, ge=0, description="Kilocalories")
    proteins: Optional[int] = Field(None, ge=0, description="Proteins")
    fats: Optional[int] = Field(None, ge=0, description="Fats")
    carbohydrated: Optional[int] = Field(None, ge=0, description="Carbohydrated")
    owner_company_id: Optional[int] = Field(
        None, description="Owner company ID (for non-template positions)"
    )


class MenuImageCreateData(BaseModel):
    """Create menu image data schema"""

    alt_text: Optional[str] = Field(None, description="Alternative text")
    display_order: int = Field(0, description="Display order")
    is_primary: bool = Field(False, description="Is primary")


class MenuItemCreate(MenuItemBase):
    """Menu item schema"""


class MenuItemUpdate(BaseModel):
    """Update menu item schema"""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    category_id: Optional[int] = None
    grams: Optional[int] = Field(None, gt=0)
    kilocalories: Optional[int] = Field(None, ge=0)
    proteins: Optional[int] = Field(None, ge=0)
    fats: Optional[int] = Field(None, ge=0)
    carbohydrated: Optional[int] = Field(None, ge=0)


class MenuImageResponse(BaseModel):
    """Response menu image schema"""

    id: int = Field(..., description="Image ID")
    filename: str = Field(..., description="File name")
    original_filename: str = Field(..., description="Original file name")
    file_path: str = Field(..., description="File path")
    file_size: int = Field(..., description="File size")
    mime_type: str = Field(..., description="MIME file type")
    width: Optional[int] = Field(None, description="Width")
    height: Optional[int] = Field(None, description="Height")
    alt_text: Optional[str] = Field(None, description="Alternative text")
    display_order: int = Field(..., description="Display order")
    is_primary: bool = Field(..., description="Is primary")
    is_active: bool = Field(..., description="Is active")
    url: str = Field(..., description="URL")
    created_at: datetime = Field(..., description="Created at")
    updated_at: datetime = Field(..., description="Updated at")

    model_config = ConfigDict(from_attributes=True)


class MenuItemResponse(MenuItemBase):
    """Response menu item schema"""

    id: int
    slug: str
    breadcrumbs: List[Dict[str, str]] = Field(..., description="Breadcrumbs")
    images: List[MenuImageResponse] = Field(
        default_factory=list, description="Images list"
    )
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class MenuItemListResponse(BaseModel):
    """Response menu item list schema"""

    items: List[MenuItemResponse]
    total: int
    page: int
    size: int
    pages: int

    model_config = ConfigDict(from_attributes=True)
