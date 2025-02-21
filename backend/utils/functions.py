from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
from rdflib import URIRef
import pandas as pd 
import json 
import requests
from global_inputs import url_api_login, url_shops

def extract_uuids_and_labels_to_df(graph_dict):
    """
    Extract UUIDs, labels, and associated shop names from graphs, returning a DataFrame.
    """
    # Brick schema URIs for Meter and Electric_Power_Sensor
    BRICK_METER = URIRef("https://brickschema.org/schema/Brick#Meter")
    BRICK_ELECTRIC_POWER_SENSOR = URIRef("https://brickschema.org/schema/Brick#Electric_Power_Sensor")
    BRICK_HAS_UUID = URIRef("https://brickschema.org/schema/Brick#hasUUID")
    BRICK_FEEDS = URIRef("https://brickschema.org/schema/Brick#feeds")
    data = []

    # Iterate through each graph in the dictionary
    for file_name, g in graph_dict.items():
        # Find all resources that are Meters or Electric_Power_Sensors
        for subject in g.subjects(None, BRICK_METER):
            uuid = None
            label = str(subject)
            shop_name = None

            # Extract UUID
            for _, _, obj in g.triples((subject, BRICK_HAS_UUID, None)):
                uuid = str(obj)

            # Extract Shop name (if the Meter feeds a Shop)
            for _, _, obj in g.triples((subject, BRICK_FEEDS, None)):
                if isinstance(obj, URIRef) and "Shop" in str(obj):
                    shop_name = str(obj).split(":")[-1]  # Extract the Shop name
            
            data.append({
                "label": label,
                "uuid": uuid,
                "shop_name": shop_name,
                "file_name": file_name
            })

        for subject in g.subjects(None, BRICK_ELECTRIC_POWER_SENSOR):
            uuid = None
            label = str(subject)
            shop_name = None

            # Extract UUID
            for _, _, obj in g.triples((subject, BRICK_HAS_UUID, None)):
                uuid = str(obj)

            # Extract Shop name (if the Sensor feeds a Shop)
            for _, _, obj in g.triples((subject, BRICK_FEEDS, None)):
                if isinstance(obj, URIRef) and "Shop" in str(obj):
                    shop_name = str(obj).split(":")[-1]  # Extract the Shop name
            
            data.append({
                "label": label,
                "uuid": uuid,
                "file_name": file_name
            })

    # Convert the results to a DataFrame
    df = pd.DataFrame(data, columns=["label", "uuid", "shop_name", "file_name"])
    return df


# ===================================================================
#                   ANALYSIS FUNCTIONS
# ===================================================================
def extract_area(graph):
    """
    Extracts the area information from a given Brick graph.
    """
    area_property = URIRef("https://brickschema.org/schema/Brick#hasArea")
    value_property = URIRef("https://brickschema.org/schema/Brick#value")
    unit_property = URIRef("https://brickschema.org/schema/Brick#unit")

    areas = []
    for area_node in graph.objects(predicate=area_property):
        value = graph.value(area_node, value_property, default=None)
        unit = graph.value(area_node, unit_property, default=None)

        if value:
            areas.append({
                "value": str(value),
                "unit": str(unit) if unit else "unknown"
            })

    return areas


# Simplify URI helper function
def simplify_uri(uri):
    return uri.split('#')[-1] if isinstance(uri, URIRef) else str(uri)

# Helper function to extract metering sensors
def extract_metering_sensors(graph):
    # Define the classes to extract
    metering_classes = [
        URIRef("https://brickschema.org/schema/Brick#Meter"),
        URIRef("https://brickschema.org/schema/Brick#Electric_Energy_Sensor"),
        URIRef("https://brickschema.org/schema/Brick#Electric_Power_Sensor"),
        URIRef("https://brickschema.org/schema/Brick#Electrical_Meter"),
    ]
    uuid_property = URIRef("https://brickschema.org/schema/Brick#hasUUID")

    sensors = []
    for metering_class in metering_classes:
        for sensor in graph.subjects(predicate=None, object=metering_class):
            uuid = graph.value(sensor, uuid_property)
            if uuid:
                sensors.append({"value": str(uuid), "label": simplify_uri(sensor)})

    return sensors


# Function to extract nodes and edges
def get_nodes_and_edges(graph):
    # Extract nodes and edges
    nodes = set()
    edges = []
    for s, p, o in graph:  # Iterate over triples in the graph
        nodes.add(simplify_uri(s))
        nodes.add(simplify_uri(o))
        edges.append({'data': {'source': simplify_uri(s), 'target': simplify_uri(o), 'label': simplify_uri(p)}})

    # Prepare Cytoscape elements
    cyto_nodes = [{'data': {'id': node, 'label': node}} for node in nodes]
    cyto_edges = edges
    elements = cyto_nodes + cyto_edges
    labels = [item['data']['label'] for item in cyto_nodes]
    return elements, labels


# Helper function to extract temperature sensors
def extract_temperature_sensors(graph):
    temp_sensor_class = URIRef("https://brickschema.org/schema/Brick#Zone_Air_Temperature_Sensor")
    temp_sensor_class_outside = URIRef("https://brickschema.org/schema/Brick#Outside_Air_Temperature_Sensor")
    uuid_property = URIRef("https://brickschema.org/schema/Brick#hasUUID")

    sensors = []
    for sensor in graph.subjects(predicate=None, object=temp_sensor_class):
        uuid = graph.value(sensor, uuid_property)
        if uuid:
            sensors.append({"value": str(uuid), "label": simplify_uri(sensor)})

    for sensor in graph.subjects(predicate=None, object=temp_sensor_class_outside):
        uuid = graph.value(sensor, uuid_property)
        if uuid:
            sensors.append({"value": str(uuid), "label": simplify_uri(sensor)})

    return sensors


# Helper function to extract outdoor temperature sensors
def extract_outdoor_temperature(graph):
    temp_sensor_class_outside = URIRef("https://brickschema.org/schema/Brick#Outside_Air_Temperature_Sensor")
    uuid_property = URIRef("https://brickschema.org/schema/Brick#hasUUID")

    sensors = []
    for sensor in graph.subjects(predicate=None, object=temp_sensor_class_outside):
        uuid = graph.value(sensor, uuid_property)
        if uuid:
            sensors.append({"value": str(uuid), "label": simplify_uri(sensor)})

    return sensors
