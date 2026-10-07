<!-- pixeltable-example-app: 20261005-mural-registry -->
# Mural Registry API built with Pixeltable

[![Built with Pixeltable](https://img.shields.io/badge/built%20with-Pixeltable-5b4bff)](https://pixeltable.com)
[![PyPI - pixeltable](https://img.shields.io/pypi/v/pixeltable?label=pixeltable)](https://pypi.org/project/pixeltable/)
[![GitHub stars](https://img.shields.io/github/stars/pixeltable/pixeltable?style=social)](https://github.com/pixeltable/pixeltable)
[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE)

A registry of a city's murals. Upload a wall photo with the title, artist and neighborhood, and Pixeltable stores the image, then derives a **96x64 thumbnail** and a **grayscale copy** as media computed columns. A chain of PIL-based UDFs tags the aspect ratio, the dominant color channel and an overall tone. The API accepts multipart uploads (in parallel), lists murals by neighborhood, runs the analysis on an upload without storing it, and serves a mural's thumbnail as an image file.

[Pixeltable](https://pixeltable.com) is open-source, Python-native **multimodal AI data infrastructure**: tables, incremental computed columns, UDFs, indexes and serving in one library, running locally or on Pixeltable Cloud.

> ⭐ **Like this example?** Star [pixeltable/pixeltable](https://github.com/pixeltable/pixeltable) on GitHub. It helps other developers find it.

## What this example shows

- **Multimodal media columns** with configurable media destinations
- **Concurrent writes**: parallel HTTP clients inserting into and updating the same table
- **Incremental computed columns** powered by plain Python UDFs (`@pxt.udf`)
- **B-tree indexes** declared on the model (`__indexes__`) back the lookup queries
- **FastAPI serving**: one `FastAPIRouter` turns tables and `@pxt.query` functions into typed REST routes (insert, update, delete, compute and query) with OpenAPI docs
- **Importable UDF module**: UDFs in `udfs.py`, tables in `models.py`, queries in `queries.py`, routes in `app.py` (Pixeltable resolves UDFs by module path)
- **`pixeltable.toml`** declares a local database and a **Pixeltable Cloud** database, so the same code deploys with `pxt db update`

## Where the images go

| Column | Kind | Stored in |
|--------|------|-----------|
| `wall_photo` | uploaded input | the database's input media store |
| `thumb = wall_photo.resize((96, 64))` | generated | the database's output media store |
| `gray = wall_photo.convert('L')` | generated | the database's output media store |

Media placement is configuration, not code. By default everything stays in the local media store (or the database's home bucket on Pixeltable Cloud). To send generated files somewhere else, set it per database in `pixeltable.toml`:

```toml
settings = { output_media_dest = 's3://<your-bucket>/murals/' }
```

or give a single column its own `destination=` (a URI, or a `pxt.ConfigVar` whose value is set in `pixeltable.toml`, so local and hosted databases can write to different places with no code change).

## Parallel uploads

Generated media is created once on insert. The demo sends 8 multipart uploads at once, and each one gets its own row, thumbnail and grayscale copy.

## What's inside

| File | What it is |
|------|------------|
| `app.py` | The API: one `FastAPIRouter` wiring the tables and queries into REST routes |
| `client_demo.py` | Analyze, upload (in parallel), browse and download mural thumbnails through the API |
| `data/canopy.png` | Sample data |
| `data/harbor-wave.png` | Sample data |
| `data/long-mile.png` | Sample data |
| `data/sunflower-wall.png` | Sample data |
| `models.py` | Tables declared as Python classes: columns, computed columns, indexes |
| `pixeltable.toml` | Project config: the local database plus a Pixeltable Cloud database (sizing, deploy excludes) |
| `queries.py` | `@pxt.query` functions served as query routes |
| `seed.py` | Seed four murals with sample wall photos from data/ |
| `udfs.py` | Pixeltable UDFs (`@pxt.udf`) in their own importable module |
| `requirements.txt` / `pyproject.toml` | Dependencies (`pixeltable[serve]>=0.7.14`) |

**Tables**

| Table | Stored columns | Computed columns |
|-------|---------|------------------|
| `murals` | `title`, `artist`, `neighborhood`, `wall_photo` | `id`, `thumb`, `gray`, `aspect`, `channel`, `tone` |

**API routes** (service `mural_api`)

| Method | Path | Kind | Backed by | Notes |
|--------|------|------|-----------|-------|
| `POST` | `/murals` | insert | `Murals` |  |
| `POST` | `/analyze` | compute | `Murals` |  |
| `POST` | `/murals/delete` | delete | `Murals` |  |
| `GET` | `/murals/by-neighborhood` | query | `in_neighborhood` |  |
| `GET` | `/murals/thumb` | query | `mural_thumb` | one row (404 if none) |

## Quickstart

Requires Python 3.11+ and `pixeltable[serve]>=0.7.14`.

```bash
git clone https://github.com/pierrebrunelle/pixeltable-mural-registry.git
cd pixeltable-mural-registry
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Create the tables in a local catalog directory named `murals`
pxt schema update app.py murals

python seed.py murals
pxt service run app.py murals --port 8000   # open http://localhost:8000/docs
python client_demo.py                      # in another terminal
```

Try it:

```bash
curl -s -X POST localhost:8000/murals -F title='Night Market' -F artist='S. Iyer' -F neighborhood=eastside -F wall_photo=@data/harbor-wave.png
curl -s -X POST localhost:8000/analyze -F wall_photo=@data/canopy.png
curl -s -o thumb.png 'localhost:8000/murals/thumb?title=Night%20Market'
```

## Deploy to Pixeltable Cloud

The same `app.py` runs on [Pixeltable Cloud](https://pixeltable.com). Sign in (or get a free trial database with `pxt new`), point the second database entry in `pixeltable.toml` at your own database, then deploy:

```bash
pxt login                       # or: export PIXELTABLE_API_KEY=<your-api-key>
# edit pixeltable.toml: name = 'pxt://<your-org>:<your-db>'
pxt db update pxt://<your-org>:<your-db>                 # build the image and upload the project
pxt schema update app.py pxt://<your-org>:<your-db>/murals   # create the tables in the hosted database
pxt service update app.py pxt://<your-org>:<your-db>/murals  # start the API there
pxt service list pxt://<your-org>:<your-db>              # list hosted services
```

Hosted routes require an API key: send it in the `X-api-key` header (for example `-H "X-api-key: $PIXELTABLE_API_KEY"`). Keep keys in environment variables or `pxt secret set`, never in code.

## Code walkthrough

**1. Business logic is plain Python, in `udfs.py`.** A `@pxt.udf` function can be used as a column expression. Pixeltable records UDFs by module path (`udfs.aspect_band`), so they live in their own importable module rather than inline in the app: the daemon, serving workers and Pixeltable Cloud import it again by that path.

```python
# udfs.py
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
```

**2. Tables are Python classes (`models.py`).** Annotated attributes are stored columns; attributes assigned an expression are **computed columns** (`id`, `thumb`, `gray`, `aspect`, `channel`, `tone`), evaluated incrementally on every insert or update and recomputed when their inputs change. Indexes live next to the columns.

```python
# models.py
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
```

**3. Queries are functions (`queries.py`).** `@pxt.query` wraps a Pixeltable query so it can be called from Python or exposed as a route:

```python
# queries.py
@pxt.query
def in_neighborhood(neighborhood: str):
    """Murals in one neighborhood (neighborhood index)."""
    return Murals.where(Murals.neighborhood == neighborhood).select(
        Murals.id, Murals.title, Murals.artist, Murals.aspect, Murals.tone
    ).order_by(Murals.title)
```

**4. One router, a full REST API.** `FastAPIRouter` generates request/response models from the column types, validates input, and publishes OpenAPI docs at `/docs`:

```python
# app.py
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
```

## Learn more

- 🌐 Website: https://pixeltable.com
- 📚 Docs: https://docs.pixeltable.com
- 💻 Source: https://github.com/pixeltable/pixeltable (⭐ star it if Pixeltable is useful to you)
- 📦 PyPI: https://pypi.org/project/pixeltable/

---

<sub>Built as part of a daily series of Pixeltable example apps · Pixeltable 0.7.14 · Python, FastAPI, incremental computed columns · Licensed under Apache-2.0.</sub>
