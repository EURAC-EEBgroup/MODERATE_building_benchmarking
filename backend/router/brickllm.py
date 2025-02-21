from models.brickMod import BrickModelGenerator
from pydantic import BaseModel
from fastapi import  HTTPException,  APIRouter, Depends
# Define input and generator
stores_path = "/path/to/stores.csv"
points_path = "/path/to/metadata.json"
api_key_client = "your_api_key_here"
generator = BrickModelGenerator(stores_path, points_path, api_key_client)

router = APIRouter(prefix='/moderate')

# Define input model for FastAPI
class StoreRequest(BaseModel):
    store_identifier: str


@router.post("/generate_rdf/", tags=["Brickllm"])
def generate_rdf(request: StoreRequest):
    """
    Endpoint to generate RDF for a given store identifier.
    """
    store_identifier = request.store_identifier

    # Validate the store identifier
    if store_identifier not in generator.stores["Store identifier"].values:
        raise HTTPException(status_code=404, detail="Store identifier not found")

    try:
        # Generate RDF text
        rdf_text = generator.create_rdf_for_store(store_identifier)

        # Return the RDF text
        return {"message": "RDF generated successfully", "rdf_text": rdf_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))