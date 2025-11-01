from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class MenuImageBase(BaseModel):
    """Base menu image schema"""

    alt_text: Optional[str] = Field(None, description="Alternative text for menu image")
    display_order: int = Field(0, description="Display order")
    is_primary: bool = Field(False, description="Is primary")


class MenuImageCreate(MenuImageBase):
    """Create menu image schema"""

    menu_item_id: int = Field(..., description="Menu item ID")


class MenuImageUpdate(BaseModel):
    """Update menu image schema"""

    alt_text: Optional[str] = Field(None, description="Alternative text for menu image")
    display_order: Optional[int] = Field(None, description="Display order")
    is_primary: Optional[bool] = Field(None, description="Is primary")
    is_active: Optional[bool] = Field(None, description="Is active")


class MenuImageResponse(MenuImageBase):
    """Response menu image schema"""

    id: int = Field(..., description="Image ID")
    filename: str = Field(..., description="File name")
    original_filename: str = Field(..., description="Original file name")
    file_path: str = Field(..., description="Path of file")
    file_size: int = Field(..., description="File size")
    mime_type: str = Field(..., description="MIME file type")
    width: Optional[int] = Field(None, description="Width")
    height: Optional[int] = Field(None, description="Height")
    url: str = Field(..., description="URL")
    thumbnails: List[dict] = Field(default_factory=list, description="Thumbnails")
    is_active: bool = Field(..., description="Is active")
    created_at: datetime = Field(..., description="Created at")
    updated_at: datetime = Field(..., description="Updated at")
    menu_item_id: int = Field(..., description="Menu item ID")

    model_config = ConfigDict(from_attributes=True)


class MenuImageListResponse(BaseModel):
    """Response menu image list schema"""

    images: List[MenuImageResponse] = Field(..., description="List of images")
    total: int = Field(..., description="Count of images")


class MenuImageUploadResponse(BaseModel):
    """Upload response menu image schema"""

    success: bool = Field(..., description="Success")
    message: str = Field(..., description="Message")
    image: MenuImageResponse = Field(..., description="Image")


class MenuImageDeleteResponse(BaseModel):
    """Delete response menu image schema"""

    success: bool = Field(..., description="Success")
    message: str = Field(..., description="Message")


class MenuImagePresignedUrlResponse(BaseModel):
    """Presigned URL menu image schema"""

    url: str = Field(..., description="Presigned URL")
    expires_at: datetime = Field(..., description="Expires at")
    image_id: int = Field(..., description="Image ID")


class ThumbnailInfo(BaseModel):
    """Thumbnail info schema"""

    size: str = Field(..., description="Size (small, medium, large)")
    width: int = Field(..., description="Width")
    height: int = Field(..., description="Height")
    file_path: str = Field(..., description="File path")
    url: str = Field(..., description="URL")
