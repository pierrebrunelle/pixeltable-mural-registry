"""Mural queries."""
import pixeltable as pxt

from models import Murals


@pxt.query
def in_neighborhood(neighborhood: str):
    """Murals in one neighborhood (neighborhood index)."""
    return Murals.where(Murals.neighborhood == neighborhood).select(
        Murals.id, Murals.title, Murals.artist, Murals.aspect, Murals.tone
    ).order_by(Murals.title)


@pxt.query
def mural_thumb(title: str):
    """The thumbnail for a mural title (served as an image file)."""
    return Murals.where(Murals.title == title).order_by(Murals.id, asc=False).limit(1).select(Murals.thumb)
