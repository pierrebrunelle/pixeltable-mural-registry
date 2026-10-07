"""The murals table: an uploaded image, two generated images and a chain of tags."""
import pixeltable as pxt
import pixeltable.functions as pxtf

from udfs import aspect_band, dominant_channel, tone_tag

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
