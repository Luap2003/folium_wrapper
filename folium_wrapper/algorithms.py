import folium
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from typing import Union, Optional
from importlib.resources import files
import os

from .helper_functions import _extract_coordinates

class Geo_Algorithms:
    """
    A class containing geographical algorithms for processing geospatial data,
    particularly for removing points that are within tunnel areas.
    """

    def __init__(self):
        pass

    def _create_buffers(self, buffer_size: float = 0.0005):
        """
        Creates buffer zones around tunnel entry and exit points.

        Parameters:
        buffer_size (float): The size of the buffer around each tunnel point.
                             Defaults to 0.0005 degrees (~50 meters, depending on latitude).

        Returns:
        Tuple[GeoDataFrame, GeoDataFrame]: Two GeoDataFrames containing buffered geometries
                                           around the tunnel entry and exit points, respectively.
        """
        # Load tunnel data from a CSV file within the 'folium_wrapper.data' package
        csv_path = files('folium_wrapper.data') / 'tunnel_karte_angle_big.csv'
        with csv_path.open('r') as f:
            df_tunnel = pd.read_csv(f)

        # Create geometry points for tunnel entry and exit points
        geometry_entry = [Point(xy) for xy in zip(df_tunnel.lat, df_tunnel.lon)]
        geometry_exit = [Point(xy) for xy in zip(df_tunnel.lat_n, df_tunnel.lon_n)]

        # Create GeoDataFrames for entry and exit points
        gdf_tunnel_entry = gpd.GeoDataFrame(df_tunnel, geometry=geometry_entry)  # type: ignore
        gdf_tunnel_exit = gpd.GeoDataFrame(df_tunnel, geometry=geometry_exit)    # type: ignore

        # Create buffer zones around the entry and exit points
        gdf_tunnel_entry['buffer'] = gdf_tunnel_entry.buffer(buffer_size)  # Adjust buffer size as needed
        gdf_tunnel_exit['buffer'] = gdf_tunnel_exit.buffer(buffer_size)    # Adjust buffer size as needed

        return gdf_tunnel_entry, gdf_tunnel_exit

    def remove_tunnel_points(self, df: Union[pd.DataFrame, gpd.GeoDataFrame],
                             lat_col: Optional[str], lon_col: Optional[str]):
        """
        Removes data points from the DataFrame that are within tunnel areas based on proximity
        to tunnel entry and exit buffer zones.

        Parameters:
        df (Union[pd.DataFrame, gpd.GeoDataFrame]): The input DataFrame containing GPS data.
        lat_col (Optional[str]): The name of the latitude column in df.
        lon_col (Optional[str]): The name of the longitude column in df.

        Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: A tuple containing:
            - A DataFrame of points that were removed because they are within tunnel areas.
            - The original DataFrame with those points removed.
        """
        # Create buffer zones around tunnel entry and exit points
        gdf_tunnel_entry, gdf_tunnel_exit = self._create_buffers()

        # Ensure that the DataFrame has 'latitude' and 'longitude' columns
        df, lat_col, lon_col = _extract_coordinates(df, lat_col, lon_col)

        # Create geometry points for the DataFrame
        geometry = [Point(x,y) for x,y in zip(df[lat_col], df[lon_col])] #type: ignore
        gdf = gpd.GeoDataFrame(df, geometry=geometry)  # type: ignore

        # Initialize a set to keep track of indices to remove
        indices_to_remove = set()
        entered_tunnel_entry = {}
        entered_tunnel_exit = {}

        # Iterate over each point in the DataFrame
        for i, row in gdf.iterrows():
            point = row.geometry

            # Check if the point is within any tunnel entry or exit buffer zones
            in_buffer_entry = gdf_tunnel_entry['buffer'].contains(point)  # type: ignore
            in_buffer_exit = gdf_tunnel_exit['buffer'].contains(point)    # type: ignore

            if in_buffer_entry.any() or in_buffer_exit.any():
                for j in range(len(in_buffer_entry)):
                    if in_buffer_entry[j] or in_buffer_exit[j]:
                        # If the point is in the entry buffer and not already recorded
                        if in_buffer_entry[j] and j not in entered_tunnel_exit:
                            entered_tunnel_exit[j] = i
                        # If the point is in the exit buffer and not already recorded
                        if in_buffer_exit[j] and j not in entered_tunnel_entry:
                            entered_tunnel_entry[j] = i
                        # Remove points between entry and exit
                        if in_buffer_entry[j] and j in entered_tunnel_entry:
                            for k in range(entered_tunnel_entry[j], i + 1):  # type: ignore
                                indices_to_remove.add(k)
                            entered_tunnel_entry.pop(j)
                        if in_buffer_exit[j] and j in entered_tunnel_exit:
                            for k in range(entered_tunnel_exit[j], i + 1):  # type: ignore
                                indices_to_remove.add(k)
                            entered_tunnel_exit.pop(j)

        indices_to_remove = sorted(set(indices_to_remove))  # Remove duplicates and sort
        print(f"Number of indices to remove: {len(indices_to_remove)}")

        # Return the removed points and the cleaned DataFrame
        return df.iloc[indices_to_remove], df.drop(index=indices_to_remove)
