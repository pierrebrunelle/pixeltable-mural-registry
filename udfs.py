"""Pixeltable UDFs for the mural registry (recorded by module path, e.g. `udfs.aspect_band`)."""
import PIL.Image

import pixeltable as pxt


@pxt.udf
def aspect_band(photo: PIL.Image.Image) -> str:
    """tall / square / wide / panorama from width / height."""
    w, h = photo.size
    r = w / h if h else 0
    if r < 0.9:
        return 'tall'
    if r <= 1.1:
        return 'square'
    return 'wide' if r < 2.0 else 'panorama'


@pxt.udf
def dominant_channel(photo: PIL.Image.Image) -> str:
    """'red', 'green' or 'blue': the channel with the highest mean."""
    small = photo.convert('RGB').resize((16, 16))
    sums = [0, 0, 0]
    for px in small.getdata():
        for i in range(3):
            sums[i] += px[i]
    return ('red', 'green', 'blue')[sums.index(max(sums))]


@pxt.udf
def tone_tag(aspect: str, channel: str) -> str:
    """Chained on two computed columns, e.g. 'wide-warm'."""
    tone = {'red': 'warm', 'green': 'verdant', 'blue': 'cool'}[channel]
    return f'{aspect}-{tone}'
