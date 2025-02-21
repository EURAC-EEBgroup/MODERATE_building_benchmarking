import pandas as pd
from brickllm.graphs import BrickSchemaGraph
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

class BrickModelGenerator:
    def __init__(self, stores_path, points_path, api_key):
        self.stores = pd.read_csv(stores_path, sep=";", decimal=",")
        self.points = pd.read_json(points_path)
        self.api_key = api_key
        self._prepare_sensors_dataframe()

    def _prepare_sensors_dataframe(self):
        """Prepare a DataFrame for sensors UUIDs and parameters."""
        df_sensors_uuid = pd.DataFrame(
            self.points[self.stores["Store identifier"]].loc[:, self.stores["Store identifier"][0]]
        ).reset_index()
        df_sensors_uuid.columns = ["Param", "uuid"]
        self.df = df_sensors_uuid[
            ~df_sensors_uuid["Param"].isin(
                ["External temperature (Celsius degree)", "HVAC power (kW)", "Global power (kW)"]
            )
        ]

    def get_uuids_and_describe(self, n):
        """
        Select specific UUIDs and describe them.
        :param n: Number of HVAC zones to describe
        :return: Description string for the selected zones
        """
        if n < 1 or n > 7:
            return "Numero fuori intervallo. Seleziona un numero tra 1 e 7."

        selected_data = self.df.head(n)
        descriptions = [
            f"Sensore di temperatura dell'aria nella zona {index + 1} con uuid {row['uuid']}"
            for index, row in selected_data.iterrows()
        ]
        return ", ".join(descriptions)

    def generate_brick_ttl(self, text, path_save_file):
        """
        Generate a Brick .ttl file using the provided text.
        :param text: Input prompt for generating the Brick model
        :param path_save_file: File path to save the .ttl file
        """
        custom_model = ChatOpenAI(temperature=0, model="gpt-4o", api_key=self.api_key)
        brick_graph = BrickSchemaGraph(model=custom_model)

        input_data = {"user_prompt": text}
        result = brick_graph.run(input_data=input_data, stream=True)
        print(result)

        # Save the generated Brick model to a file
        brick_graph.save_ttl_output(path_save_file)

    def create_rdf_for_store(self, store_identifier):
        """
        Generate RDF file for a specific store.
        :param store_identifier: Store identifier to process
        """
        # Find the index for the store
        store_index = self.stores[self.stores["Store identifier"] == store_identifier].index[0]

        # Extract store-specific data
        store_name = self.stores["Store name"][store_index]
        area = self.stores["Store surface (mq)"][store_index]
        latitude = self.stores["Store latitude (decimal degrees)"][store_index]
        longitude = self.stores["Store longitude (decimal degrees)"][store_index]
        num_hvac_zones = self.stores["Num HVAC/temperature areas"][store_index]

        # Extract meter UUIDs
        global_power_uuid = self.points[self.stores["Store identifier"]].loc["Global power (kW)", store_identifier]
        hvac_power_uuid = self.points[self.stores["Store identifier"]].loc["HVAC power (kW)", store_identifier]
        external_temp_uuid = self.points[self.stores["Store identifier"]].loc[
            "External temperature (Celsius degree)", store_identifier
        ]

        # Generate HVAC description
        hvac_description = self.get_uuids_and_describe(num_hvac_zones)

        # Compose the text
        text = (
            f"I manage a building located at {store_name} with coordinates latitude {latitude} "
            f"and longitude {longitude}. In the building, there is my shop identified by name: {store_identifier}. "
            f"The building's electrical power is monitored by a meter with UUID: {global_power_uuid}. "
            f"The shop's HVAC system electricity consumption is tracked by a meter with UUID: {hvac_power_uuid}. "
            f"The shop comprises {num_hvac_zones} HVAC zones, each equipped with an air temperature sensor: {hvac_description}. "
            f"There is also an external air temperature sensor with UUID: {external_temp_uuid}. "
            f"The building has an area of {area} square meter."
        )

        # Return the generated text
        return text


class FolderPath(BaseModel):
    folder_path: str