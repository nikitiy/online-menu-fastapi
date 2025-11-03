from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class MenuItemBase(BaseModel):
    """Base menu item schema"""

    name: str = Field(..., min_length=1, max_length=255, description="Name")
    description: str = Field(..., min_length=1, description="Description")
    grams: int = Field(..., gt=0, description="Grams")
    kilocalories: Optional[int] = Field(None, ge=0, description="Kilocalories")
    proteins: Optional[int] = Field(None, ge=0, description="Proteins")
    fats: Optional[int] = Field(None, ge=0, description="Fats")
    carbohydrated: Optional[int] = Field(None, ge=0, description="Carbohydrated")


class MenuImageCreateData(BaseModel):
    """Create menu image data schema"""

    alt_text: Optional[str] = Field(None, description="Alternative text")
    display_order: int = Field(0, description="Display order")
    is_primary: bool = Field(False, description="Is primary")


class MenuItemCreate(MenuItemBase):
    """Menu item schema"""

    category_slug: str = Field(..., description="Category slug")
    company_subdomain: Optional[str] = Field(
        None,
        description="Company subdomain",
    )


class MenuItemUpdate(BaseModel):
    """Update menu item schema"""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    category_slug: Optional[str] = Field(None, description="Category slug")
    company_subdomain: Optional[str] = Field(None, description="Company subdomain")
    grams: Optional[int] = Field(None, gt=0)
    kilocalories: Optional[int] = Field(None, ge=0)
    proteins: Optional[int] = Field(None, ge=0)
    fats: Optional[int] = Field(None, ge=0)
    carbohydrated: Optional[int] = Field(None, ge=0)


class MenuImageResponse(BaseModel):
    """Response menu image schema"""

    display_order: int = Field(..., description="Display order")
    is_primary: bool = Field(..., description="Is primary")
    url: str = Field(..., description="URL")

    model_config = ConfigDict(from_attributes=True)


class MenuItemResponse(MenuItemBase):
    """Response menu item schema"""

    slug: str
    breadcrumbs: List[Dict[str, str]] = Field(..., description="Breadcrumbs")
    images: List[MenuImageResponse] = Field(
        default_factory=list, description="Images list"
    )

    model_config = ConfigDict(from_attributes=True)


class MenuItemListResponse(BaseModel):
    """Response menu item list schema"""

    items: List[MenuItemResponse]
    total: int
    page: int
    size: int
    pages: int

    model_config = ConfigDict(from_attributes=True)
