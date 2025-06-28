# main.py
import json
from ipywidgets import AppLayout, Output, VBox
from ipyleaflet import Map, DrawControl, basemaps, basemap_to_tiles
from shapely.geometry import shape
from rasterio.mask import mask
import rasterio
import numpy as np
import geopandas as gpd
from collections import Counter

# Load landcover raster (assuming it's local)
LANDCOVER_PATH = "data/ESA_WorldCover_10m_2020_Map.tif"  # Must be downloaded separately

print("Hello World!")
# Create output panel
output = Output()

print("passed checkpoint 1")

# Create map
m = Map(center=(0, 0), zoom=2, basemap=basemaps.Esri.WorldImagery)

# Drawing control
draw_control = DrawControl(polyline={}, circlemarker={}, circle={}, marker={})
draw_control.polygon = {"shapeOptions": {"color": "#6bc2e5", "fillOpacity": 0.5}}
draw_control.rectangle = {"shapeOptions": {"color": "#fca45d", "fillOpacity": 0.5}}

# Handle drawing
@draw_control.on_draw
def handle_draw(target, action, geo_json):
    geom = shape(geo_json['geometry'])
    output.clear_output()
    with output:
        try:
            gdf = gpd.GeoDataFrame(index=[0], crs='EPSG:4326', geometry=[geom])
            gdf = gdf.to_crs('EPSG:3857')  # Project to metric CRS
            projected_geom = gdf.geometry[0]

            with rasterio.open(LANDCOVER_PATH) as src:
                clipped, transform = mask(src, [json.loads(gdf.to_json())['features'][0]['geometry']], crop=True)
                data = clipped[0].flatten()
                data = data[data != src.nodata]

                if data.size == 0:
                    print("No terrain data available in selected area.")
                    return

                total_pixels = data.size
                counts = Counter(data)
                percentages = {k: (v / total_pixels) * 100 for k, v in counts.items()}

                print("Terrain type distribution (%):")
                for code, percent in percentages.items():
                    terrain_name = LANDCOVER_CLASSES.get(code, f"Class {code}")
                    print(f"{terrain_name}: {percent:.2f}%")

        except Exception as e:
            print(f"Error: {e}")

m.add_control(draw_control)

# Layout the app
app = AppLayout(
    left_sidebar=None,
    center=m,
    right_sidebar=VBox([output]),
    pane_widths=[0, 2, 1]
)

# Only works in Jupyter Notebook
app
