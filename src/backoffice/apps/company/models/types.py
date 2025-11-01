from enum import Enum as PyEnum


class CompanyRole(str, PyEnum):
    OWNER = "owner"
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"


class CompanyEstablishmentType(str, PyEnum):
    RESTAURANT = "restaurant"
    CAFE = "cafe"
    COFFEE_SHOP = "coffee_shop"
    BAR = "bar"
    OTHER = "other"


class CuisineCategory(str, PyEnum):
    JAPANESE = "japanese"
    RUSSIAN = "russian"
    OTHER = "other"
