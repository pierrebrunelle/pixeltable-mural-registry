"""Mural Registry API built with Pixeltable.

    pxt schema update app.py murals
    pxt service run app.py murals
"""
from pixeltable.serving import FastAPIRouter

from models import Murals, TableModel  # noqa: F401  (TableModel lets `pxt schema` find the models)
from queries import in_neighborhood, mural_thumb

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
