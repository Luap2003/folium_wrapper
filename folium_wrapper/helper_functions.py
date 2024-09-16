import pandas as pd
import geopandas as gpd
from typing import Union, Optional
import os

def _extract_coordinates(df: Union[pd.DataFrame, gpd.GeoDataFrame], lat_col: Optional[str], lon_col: Optional[str]):
        """
        Private method to extract coordinates from a GeoDataFrame or DataFrame.
        """
        is_geodf = isinstance(df, gpd.GeoDataFrame)

        # If GeoDataFrame and lat_col/lon_col not provided, extract coordinates from geometry
        if is_geodf and lat_col is None and lon_col is None:
            if df.geometry.is_empty.any():
                raise ValueError("GeoDataFrame contains empty geometries.")
            if not all(df.geometry.geom_type == 'Point'):
                raise ValueError("All geometries must be of Point type.")

            df = df.copy()
            df['longitude'] = df.geometry.x
            df['latitude'] = df.geometry.y
            return df, 'latitude', 'longitude'

        elif lat_col is None or lon_col is None:
            raise ValueError("lat_col and lon_col must be provided unless df is a GeoDataFrame with Point geometries.")
        
        return df, lat_col, lon_col
    
def _separate_kwargs(df: Union[pd.DataFrame, gpd.GeoDataFrame], **kwargs):
    """
    Private method to separate scalar kwargs from those that are column-based.
    """
    scalar_kwargs = {}
    column_kwargs = {}
    for key, value in kwargs.items():
        if isinstance(value, str) and value in df.columns:
            column_kwargs[key] = value
        else:
            scalar_kwargs[key] = value

    return scalar_kwargs, column_kwargs