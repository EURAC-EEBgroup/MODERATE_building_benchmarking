from fastapi import FastAPI
from router.data_metadata import router as data_metadata_router


# ====================================================================================
#                   WURTH API
# ====================================================================================

description_API = """
API to retrieve data from wurth datasets
"""

tags_metadata = [
    {
        "name": "Admin",
        "description": "create user, login, logiut"
    },
    {
        "name": "Building",
        "description": "retrieve buildings list according to specific features"
    },
    {
        "name": "Brickllm",
        "description": "rgenerate brickllm models"
    },
    {
        "name": "Analysis",
        "description": "rgenerate brickllm models"
    }
]

# ====================================================================================
#                   INIZIALIZE FAST API 
# ====================================================================================

app = FastAPI(
    title = "WURTH - MODERATE ",
    description = description_API,
    version = "0.0.1",
    contact = {
        "name" : 'Daniele Antonucci',
        "email" : "daniele.antonucci@eurac.edu",
    },
    license_info = {
        "name" : "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html"
    },
    openapi_tags=tags_metadata
)

app.include_router(data_metadata_router)
