from fastapi import (
    FastAPI
)

from api.supa          import app as supa_auth_router
from api.file_manager  import app as file_manager_router



tags_metadata = [
    {
        "name": "users",
        "description": "Operations with users. The **login** logic is also here.",
    },
]

app = FastAPI(
    title="TaxProperty",
    tags_metadata = tags_metadata,
    docs_url="/p/",
    openapi_url="/p/openapi.json"
)

routes = [
    supa_auth_router, 
    file_manager_router,

]

for route in routes:
    app.include_router(route)
     




