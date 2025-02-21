# # import pandas as pd

# # #1 Generate brick model of wurth shops and connect to the database
# # '''
# # info: 
# # BCG7;Darfo Boario Terme;439;10,17052;45,87047;4
# # "BCG7": {
# #     "Internal temperature area 1 (Celsius degree)": "83e3cf9b-1ca7-4012-bc6e-23d69d7a9091",
# #     "Internal temperature area 2 (Celsius degree)": "00a5ecf3-6998-4a1b-8468-8372ef5058fd",
# #     "Internal temperature area 3 (Celsius degree)": "3de8180c-b097-4dd4-8121-c7f05bc52381",
# #     "Internal temperature area 4 (Celsius degree)": "997957af-b760-4e70-af57-f2f0b2ccd3b2",
# #     "External temperature (Celsius degree)": "ce0c61b5-7be0-4da1-ab5c-b6fc6ef7e548",
# #     "HVAC power (kW)": "b8b2e35d-b83e-4130-b4c7-20c1ea9815b3",
# #     "Global power (kW)": "a117160d-3417-4c4a-86e1-092b4f12877c",
# #     "Internal temperature area 5 (Celsius degree)": "f9cd9006-8d68-43a8-ad09-8bfd37d7a706",
# #     "Internal temperature area 6 (Celsius degree)": "8e6258a6-6819-4250-bdac-17072dda0392",
# #     "Internal temperature area 7 (Celsius degree)": "b1d6ebb7-b91e-4316-910e-e9d4a24efee1"
# # }
# # '''
# # # =============================================================================================
# # # GENERATE BRICK MODEL using brick llm 
# # # =============================================================================================


from brickllm.graphs import BrickSchemaGraph
from langchain_openai import ChatOpenAI


def generate_brick_ttl(text, path_save_file, api_key_client):
    '''
    Generate brick ttl file
    '''

    custom_model = ChatOpenAI(temperature=0, model="gpt-4o", api_key=api_key_client)
    brick_graph = BrickSchemaGraph(model=custom_model)

    # Prepare input data
    input_data = {"user_prompt": text}

    # Run the graph without streaming
    result = brick_graph.run(
        input_data=input_data,
        stream=True
    )
    print(result)
    # save the result to a file
    brick_graph.save_ttl_output(path_save_file)


# # # # =============================================================================================
# # # # CREATE TEXT PROMPT
# # # # =============================================================================================

# # stores = pd.read_csv("/Users/dantonucci/Library/CloudStorage/OneDrive-ScientificNetworkSouthTyrol/00_GitHubProject/benchmarking_geoapp/data/iot_wuerth_stores_data/stores.csv", sep=";", decimal=",")
# # points = pd.read_json("/Users/dantonucci/Library/CloudStorage/OneDrive-ScientificNetworkSouthTyrol/00_GitHubProject/benchmarking_geoapp/metadata.json")

# # # # DESCRIBE SENSORS
# # df_sensors_uuid=pd.DataFrame(points[stores['Store identifier']].loc[:,stores['Store identifier'][0]]).reset_index()
# # df_sensors_uuid.columns = ['Param', 'uuid']

# # df = df_sensors_uuid[~df_sensors_uuid['Param'].isin(['External temperature (Celsius degree)', 'HVAC power (kW)', 'Global power (kW)'])]

# # # Funzione per selezionare gli UUID e descriverli
# # def get_uuids_and_describe(n):
# #     '''
# #     Select specific uuids and describe them 
# #     '''
# #     if n < 1 or n > 7:
# #         return "Numero fuori intervallo. Seleziona un numero tra 1 e 7."

# #     # Selezionare i primi n elementi e costruire la descrizione
# #     selected_data = df.head(n)
# #     descriptions = []
# #     for index, row in selected_data.iterrows():
# #         zone_number = index + 1  # Assumendo che 'Param' sia ordinato correttamente
# #         descriptions.append(f"Sensore di temperatura dell'aria nella zona {zone_number} con uuid {row['uuid']}")

# #     return ", ".join(descriptions)


# # # # =============================================================================================
# # # # CREATE RDF FILES
# # # # =============================================================================================


# # api_key_client="s"
# # for i, name in enumerate(stores["Store identifier"]):
# #     # Extract store-specific data
# #     store_name = stores["Store name"][i]
# #     area = stores["Store surface (mq)"][i]
# #     latitude = stores["Store latitude (decimal degrees)"][i]
# #     longitude = stores["Store longitude (decimal degrees)"][i]
# #     num_hvac_zones = stores["Num HVAC/temperature areas"][i]
    
# #     # Extract meter UUIDs
# #     global_power_uuid = points[stores["Store identifier"]].loc["Global power (kW)", name]
# #     hvac_power_uuid = points[stores["Store identifier"]].loc["HVAC power (kW)", name]
# #     external_temp_uuid = points[stores["Store identifier"]].loc["External temperature (Celsius degree)", name]
    
# #     # Generate HVAC description
# #     hvac_description = get_uuids_and_describe(num_hvac_zones)
    
# #     # Compose the text
# #     text = (
# #         f"I manage a building located at {store_name} with coordinates latitude {latitude} "
# #         f"and longitude {longitude}. In the building, there is my shop identified by name: {name}. "
# #         f"The building's electrical power is monitored by a meter with UUID: {global_power_uuid}. "
# #         f"The shop's HVAC system electricity consumption is tracked by a meter with UUID: {hvac_power_uuid}. "
# #         f"The shop comprises {num_hvac_zones} HVAC zones, each equipped with an air temperature sensor: {hvac_description}. "
# #         f"There is also an external air temperature sensor with UUID: {external_temp_uuid}."
# #         f"The building has an area of {area} square meter"
# #     )
    
# #     # Print the generated text
# #     print(text)
    
# #     # Generate the file
# #     generate_brick_ttl(text, name, api_key_client)




# # # =============================================================================================
# # # STORE RDF FILES in a rdf.lib
# # # =============================================================================================
# # import rdflib
# # import os 

# # # Initialize an RDF graph
# # g = rdflib.Graph()

# # # Specify the directory containing TTL files
# # directory_path = '/Users/dantonucci/Library/CloudStorage/OneDrive-ScientificNetworkSouthTyrol/00_GitHubProject/benchmarking_geoapp/BENTOML_service/Data_synth/ttl_files'

# # # Loop through each file in the directory
# # for file_name in os.listdir(directory_path):
# #     file_path = os.path.join(directory_path, file_name)
# #     if os.path.isfile(file_path) and file_path.endswith('.ttl'):
# #         # Load the TTL file into the graph
# #         g.parse(file_path, format='turtle')

# # print(f"Loaded {len(g)} triples from TTL files.")

# #
# import pandas as pd

# class BrickModelGenerator:
#     def __init__(self, stores_path, points_path, path_save, api_key):
#         self.stores = pd.read_csv(stores_path, sep=";", decimal=",")
#         self.points = pd.read_json(points_path)
#         self.path_save = path_save
#         self.api_key = api_key

#     def _prepare_sensors_dataframe(self, store_identifier):
#         """
#         Prepare a DataFrame for sensors UUIDs and parameters for a specific store.
#         """
#         df_sensors_uuid = pd.DataFrame(
#             self.points[self.stores["Store identifier"]].loc[:, store_identifier]
#         ).reset_index()
#         df_sensors_uuid.columns = ["Param", "uuid"]
#         return df_sensors_uuid[
#             ~df_sensors_uuid["Param"].isin(
#                 ["External temperature (Celsius degree)", "HVAC power (kW)", "Global power (kW)"]
#             )
#         ]

#     def get_uuids_and_describe(self, df, n):
#         """
#         Select specific UUIDs and describe them.
#         :param df: DataFrame of UUIDs for a specific store
#         :param n: Number of HVAC zones to describe
#         :return: Description string for the selected zones
#         """
#         if n < 1 or n > 7:
#             return "Numero fuori intervallo. Seleziona un numero tra 1 e 7."

#         selected_data = df.head(n)
#         descriptions = [
#             f"Sensore di temperatura dell'aria nella zona {index + 1} con uuid {row['uuid']}"
#             for index, row in selected_data.iterrows()
#         ]
#         return ", ".join(descriptions)

    # def generate_brick_ttl(self, text, path_save_file):
    #     """
    #     Generate a Brick .ttl file using the provided text.
    #     :param text: Input prompt for generating the Brick model
    #     :param path_save_file: File path to save the .ttl file
    #     """
    #     custom_model = ChatOpenAI(temperature=0, model="gpt-4o", api_key=self.api_key)
    #     brick_graph = BrickSchemaGraph(model=custom_model)

    #     input_data = {"user_prompt": text}
    #     result = brick_graph.run(input_data=input_data, stream=True)
    #     print(result)

    #     # Save the generated Brick model to a file
    #     brick_graph.save_ttl_output(path_save_file)

#     def create_rdf_files(self):
#         """
#         Generate RDF files for each store in the dataset.
#         """
#         for i, name in enumerate(self.stores["Store identifier"]):
#             # Extract store-specific data
#             store_name = self.stores["Store name"][i]
#             area = self.stores["Store surface (mq)"][i]
#             latitude = self.stores["Store latitude (decimal degrees)"][i]
#             longitude = self.stores["Store longitude (decimal degrees)"][i]
#             num_hvac_zones = self.stores["Num HVAC/temperature areas"][i]

#             # Extract meter UUIDs
#             global_power_uuid = self.points[self.stores["Store identifier"]].loc["Global power (kW)", name]
#             hvac_power_uuid = self.points[self.stores["Store identifier"]].loc["HVAC power (kW)", name]
#             external_temp_uuid = self.points[self.stores["Store identifier"]].loc[
#                 "External temperature (Celsius degree)", name
#             ]

#             # Prepare the DataFrame for the specific store
#             df_store_sensors = self._prepare_sensors_dataframe(name)

#             # Generate HVAC description
#             hvac_description = self.get_uuids_and_describe(df_store_sensors, num_hvac_zones)
#             # print(hvac_description)
#             # Compose the text
#             text = (
#                 f"I manage a building located at {store_name} with coordinates latitude {latitude} "
#                 f"and longitude {longitude}. In the building, there is my shop identified by name: {name}. "
#                 f"The building's electrical power is monitored by a meter with UUID: {global_power_uuid}. "
#                 f"The shop's HVAC system electricity consumption is tracked by a meter with UUID: {hvac_power_uuid}. "
#                 f"The shop comprises {num_hvac_zones} HVAC zones, each equipped with an air temperature sensor: {hvac_description}. "
#                 f"There is also an external air temperature sensor with UUID: {external_temp_uuid}. "
#                 f"The building has an area of {area} square meter."
#             )

#             # Print the generated text
#             print(text)

#             # Generate the .ttl file
#             self.generate_brick_ttl(text, f"{self.path_save}/{name}")

# # Usage example
# if __name__ == "__main__":
#     # Define file paths and API key
#     stores_path = "/Users/dantonucci/Library/CloudStorage/OneDrive-ScientificNetworkSouthTyrol/00_GitHubProject/benchmarking_geoapp/data/iot_wuerth_stores_data/stores.csv"
#     points_path = "/Users/dantonucci/Library/CloudStorage/OneDrive-ScientificNetworkSouthTyrol/00_GitHubProject/benchmarking_geoapp/metadata.json"
#     path_save = "/Users/dantonucci/Library/CloudStorage/OneDrive-ScientificNetworkSouthTyrol/00_GitHubProject/dashboard_analytics/backend/data/ttl_files"
#     api_key_client = ""

#     # Create an instance of the generator
#     generator = BrickModelGenerator(stores_path, points_path, path_save, api_key_client)

#     # Generate RDF files for the dataset
#     generator.create_rdf_files()




