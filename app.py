"""Mural Registry API built with Pixeltable.

    pxt schema update app.py murals
    pxt service run app.py murals
"""
import pixeltable as pxt
import pixeltable.functions as pxtf
from pixeltable.serving import FastAPIRouter

from udfs import aspect_band, dominant_channel, tone_tag

# ---- tables ----
TableModel = pxt.model_base()


class Murals(TableModel, name='murals', has_default_idxs=False):
    id = pxt.Column(value=pxtf.uuid.uuid7(), primary_key=True)
    title: pxt.String
    artist: pxt.String
    neighborhood: pxt.String
    wall_photo: pxt.Image

    thumb = wall_photo.resize((96, 64))      # generated media
    gray = wall_photo.convert('L')           # generated media
    aspect = aspect_band(wall_photo)
    channel = dominant_channel(wall_photo)
    tone = tone_tag(aspect, channel)         # chained on two computed columns

    __indexes__ = [pxt.BtreeIndex(neighborhood)]


# ---- queries ----
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


# ---- routes ----
mural_api = FastAPIRouter(name='mural_api')
mural_api.add_insert_route(
    Murals, path='/murals',
    inputs=[Murals.title, Murals.artist, Murals.neighborhood],
    uploadfile_inputs=[Murals.wall_photo],
    outputs=[Murals.id, Murals.aspect, Murals.channel, Murals.tone],
)
mural_api.add_compute_route(Murals, path='/analyze', inputs=[], uploadfile_inputs=[Murals.wall_photo],
                            outputs=[Murals.aspect, Murals.channel, Murals.tone])
mural_api.add_delete_route(Murals, path='/murals/delete')
mural_api.add_query_route(path='/murals/by-neighborhood', query=in_neighborhood, method='get')
mural_api.add_query_route(path='/murals/thumb', query=mural_thumb, method='get', one_row=True,
                          return_fileresponse=True)
