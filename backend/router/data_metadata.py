# Import necessary modules and libraries
from fastapi import APIRouter, Depends, HTTPException, Response, Query
from fastapi.responses import JSONResponse
import brickschema
import os
import json 
from rdflib import Namespace
import shutil
import utils.functions as Fc

# Initialize the FastAPI router with a prefix for all routes
router = APIRouter(prefix='/moderate')

# Path to the folder containing .ttl files
folder_path_ = os.getcwd() + "/data/ttl_files"
os.makedirs(folder_path_, exist_ok=True)  # Create the folder if it doesn't exist

# Function to load .ttl files into a Brick structure
def generate_brick_structure(folder_path):
    """
    Loads all .ttl files from the specified folder into a Brick schema structure.
    Returns a dictionary where the keys are filenames and the values are Brick graphs.
    """
    graph_dict = {}

    # Iterate through the files in the folder
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".ttl"):  # Only process .ttl files
            full_path = os.path.join(folder_path, file_name)
            try:
                # Load each .ttl file into a Brick graph
                g = brickschema.Graph()
                g.load_file(full_path)
                graph_dict[file_name] = g  # Add the graph to the dictionary
                print(f"Loaded: {file_name}")
            except Exception as e:
                print(f"Error loading {file_name}: {e}")

    return graph_dict

# Initialize the Brick structure on server startup
bui_structure = generate_brick_structure(folder_path_)

# Endpoint: Retrieve a list of all buildings (files) in the structure
@router.get("/api/v1/building_list", tags=["Building"])
async def get_building_list():
    """
    Get the names of all buildings (TTL files) in the structure.
    Returns a JSON response containing the list of building names.
    """
    building_names = [key.replace('.ttl', '') for key in bui_structure.keys()]
    return JSONResponse(content=building_names)

# Endpoint: Reload the Brick structure by reloading .ttl files
@router.post("/api/v1/update_building_structure", tags=["Building"])
async def update_building_structure():
    """
    Reload the .ttl files in the folder and update the global bui_structure.
    """
    global bui_structure  # Use the global variable for the Brick structure
    try:
        bui_structure = generate_brick_structure(folder_path_)  # Reload structure
        return JSONResponse(content={"message": "Building structure updated successfully."}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating building structure: {str(e)}")

# Endpoint: Retrieve elements of a specified Brick type for a building
@router.get("/api/v1/building/{bui_name}&{type}", tags=["Building"])
def get_element(bui_name: str, type: str):
    """
    Get elements of a specified Brick type (e.g., Zone) for a specific building.
    Params:
        bui_name: Name of the building file
        type: Brick type (e.g., Zone)
    """
    BRICK = Namespace("https://brickschema.org/schema/Brick#")
    BLDG = Namespace("urn:Building#")

    g = bui_structure.get(f'{bui_name}.ttl')  # Get the graph for the building
    element = []

    # Query the graph for elements of the specified type
    for s, p, o in g.triples((None, None, BRICK[type])):
        element.append(s.split('#')[-1])  # Extract the element name

    return Response(json.dumps(element, indent=4), media_type="application/json")

# Endpoint: Upload a .ttl file and update the Brick structure
@router.post("/api/v1/upload_file", tags=["Building"])
async def upload_file(file_path: str):
    """
    Upload a .ttl file by specifying its path. The file is copied to the ttl_files folder
    and the building structure is updated.
    """
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=400, detail="File does not exist")

    if not file_path.endswith(".ttl"):
        raise HTTPException(status_code=400, detail="Only .ttl files are supported")

    dest_path = os.path.join(folder_path_, os.path.basename(file_path))
    try:
        shutil.copy(file_path, dest_path)  # Copy the file to the destination
        global bui_structure
        bui_structure = generate_brick_structure(folder_path_)  # Update the structure
        return {"message": f"File '{file_path}' copied and building structure updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

# Endpoint: Retrieve the TTL content of a building
@router.get("/api/v1/building_ttl", tags=["Building"])
async def get_building_ttl(file_name: str = Query(..., description="Name of the building (without .ttl extension)")):
    """
    Get the TTL content of a building by its name.
    """
    full_file_name = f"{file_name}.ttl"

    if full_file_name not in bui_structure:
        raise HTTPException(status_code=404, detail="File not found")

    try:
        graph = bui_structure[full_file_name]
        ttl_content = graph.serialize(format="turtle")  # Serialize graph to TTL format
        return Response(ttl_content, media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error serializing file: {str(e)}")

# Endpoint: Fetch nodes and edges of a building
@router.get("/api/v1/building_graph", tags=["Building"])
async def get_building_graph(file_name: str = Query(..., description="Name of the building (without .ttl extension)")):
    """
    Get the nodes and edges of a building graph.
    """
    full_file_name = f"{file_name}.ttl"

    if full_file_name not in bui_structure:
        raise HTTPException(status_code=404, detail="File not found")

    try:
        graph = bui_structure[full_file_name]
        elements, labels = Fc.get_nodes_and_edges(graph)  # Extract nodes and edges
        return JSONResponse(content={"elements": elements, "labels": labels})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

# Endpoint: Get temperature sensors in a building
@router.get("/api/v1/building_sensors", tags=["Building"])
async def get_temperature_sensors(file_name: str = Query(..., description="Name of the TTL file without extension")):
    """
    Extract UUIDs and labels of all temperature sensors for the specific building.
    """
    ttl_file_name = file_name + ".ttl"

    if ttl_file_name not in bui_structure:
        raise HTTPException(status_code=404, detail=f"Building file '{file_name}' not found.")

    try:
        graph = bui_structure[ttl_file_name]
        sensors = Fc.extract_temperature_sensors(graph)
        return sensors
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing sensors: {str(e)}")



# Endpoint to get outdoor temperature sensors
@router.get("/api/v1/outdoor_temperature", tags=["Building"])
async def get_outdoor_temperature_sensors(file_name: str = Query(..., description="Name of the TTL file without extension")):
    '''
    Extract UUID and label of outdoor temperature for the specific building.
    '''
    ttl_file_name = file_name + ".ttl"

    # Check if the file exists in the bui_structure
    if ttl_file_name not in bui_structure:
        raise HTTPException(status_code=404, detail=f"Building file '{file_name}' not found.")

    # Extract the graph for the given file
    graph = bui_structure[ttl_file_name]

    try:
        # Extract temperature sensors from the graph
        sensors = Fc.extract_outdoor_temperature(graph)
        return sensors
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing sensors: {str(e)}")



# Endpoint to get meter sensors
@router.get("/api/v1/meter_sensors", tags=["Building"])
async def get_meter_sensors(file_name: str = Query(..., description="Name of the TTL file without extension")):
    '''
    Extract UUID and label of all meters sensors for the specific building.
    '''
    ttl_file_name = file_name + ".ttl"

    # Check if the file exists in the bui_structure
    if ttl_file_name not in bui_structure:
        raise HTTPException(status_code=404, detail=f"Building file '{file_name}' not found.")

    # Extract the graph for the given file
    graph = bui_structure[ttl_file_name]

    try:
        # Extract temperature sensors from the graph
        sensors = Fc.extract_metering_sensors(graph)
        return sensors
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing sensors: {str(e)}")


# =============================================================================================
# GEt building coordinates
@router.get("/api/v1/building_location", tags=["Building"])
async def get_building_location(file_name: str = Query(..., description="Name of the TTL file")):
    """
    Get latitude and longitude of a building from a TTL file.
    """
    # Check if file exists in the structure
    if file_name not in bui_structure:
        raise HTTPException(status_code=404, detail=f"File '{file_name}' not found in the structure.")

    # Get the graph for the specified file
    graph = bui_structure[file_name]

    # Query the graph for building location
    query = """
    PREFIX brick: <https://brickschema.org/schema/Brick#>
    PREFIX bldg: <urn:Building#>
    SELECT ?building ?latitude ?longitude
    WHERE {
        ?building a brick:Building .

        # Case 1: Coordinates in hasCoordinates
        OPTIONAL {
            ?building brick:hasCoordinates ?coords .
            ?coords brick:latitude ?latitude ;
                    brick:longitude ?longitude .
        }

        # Case 2: Coordinates in hasLocation with latitude and longitude
        OPTIONAL {
            ?building brick:hasLocation ?loc .
            ?loc brick:latitude ?latitude ;
                brick:longitude ?longitude .
        }

        # Case 3: Separate hasLatitude and hasLongitude properties
        OPTIONAL {
            ?building brick:hasLatitude [ brick:value ?latitude ] ;
                    brick:hasLongitude [ brick:value ?longitude ] .
        }
    }
    """

    results = graph.query(query)

    # Extract the latitude and longitude
    for row in results:
        latitude = str(row.latitude)
        longitude = str(row.longitude)
        return JSONResponse(content={"latitude": latitude, "longitude": longitude})

    # If no building is found
    raise HTTPException(status_code=404, detail=f"No location found for building in file '{file_name}'.")



@router.post("/api/v1/energy_meters/")
async def generate_dataframe():
    """
    Generate a DataFrame from the TTL files in the specified folder.
    """
    # Generate DataFrame
    try:
        df = Fc.extract_uuids_and_labels_to_df(bui_structure)
        # List of keywords to exclude
        keywords = ["Meter_1", "Building_Meter", "..Meter_Building", "Main", "Electric_Power_Meter", "Building_"]

        # Filter out rows containing the keywords in the "label" column
        filtered_df = df[~df["label"].str.contains('|'.join(keywords), case=False, na=False)]

        # Remove 'bui_' prefix and '.ttl' suffix from the 'file_name' column
        filtered_df['file_name'] = filtered_df['file_name'].str.replace("bui_", "").str.replace(".ttl", "")

        # filter df only with uuid and name
        final_df = filtered_df.loc[:,['file_name','uuid']]
        final_df.columns = ['shops','uuid']

        # return df_results.to_dict(orient="records")  # Return DataFrame as a list of dictionaries
        return json.dumps(final_df.to_dict(orient="records"))  # Return DataFrame as a list of dictionaries
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating DataFrame: {e}")
    


@router.get("/api/v1/building_area", tags=["Building"])
async def get_building_area(file_name: str = Query(..., description="Name of the TTL file without extension")):
    """
    Extract the area information of the building in the specified TTL file.
    """
    ttl_file_name = file_name + ".ttl"

    # Check if the file exists in the bui_structure
    if ttl_file_name not in bui_structure:
        raise HTTPException(status_code=404, detail=f"Building file '{file_name}' not found.")

    # Extract the graph for the given file
    graph = bui_structure[ttl_file_name]

    try:
        # Extract area information from the graph
        areas = Fc.extract_area(graph)
        if not areas:
            raise HTTPException(status_code=404, detail="No area information found in the specified file.")
        return areas
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing area information: {str(e)}")