from typing import TypeVar

from slugify import slugify

T = TypeVar("T")


class SlugService:
    @staticmethod
    def set_slug(instance: T, name: str, slug_field: str = "slug") -> str:
        """
        Sets the slug for an object in the format {base_slug}-{id}
        """
        base_slug = slugify(name)
        object_id = getattr(instance, "id", None)

        if object_id is None:
            raise ValueError("The object must have an ID to generate a slug")

        slug = f"{base_slug}-{object_id}"
        setattr(instance, slug_field, slug)
        return slug
