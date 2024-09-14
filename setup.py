# setup.py

from setuptools import setup, find_packages

setup(
    name='folium_wrapper',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'folium',
        'pandas',
        'geopandas',
    ],
    author='Your Name',
    author_email='your.email@example.com',
    description='A wrapper library for Folium to simplify adding markers from DataFrames.',
)
