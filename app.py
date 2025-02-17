import json
import os

from flask import Flask, request
from folium import Map, plugins, PolyLine, TileLayer, LayerControl, FeatureGroup
from folium.plugins import AntPath
from geopy.distance import geodesic

from hooks import get_mid_point, great_circle_points, add_arrow

app = Flask(__name__)


def create_map(start_coord: tuple[float, float], end_coord: tuple[float, float], dep: str, des: str,
               weather: list[dict]) -> Map:
    distance = geodesic(start_coord, end_coord).kilometers
    # Determine zoom level based on distance
    if distance < 500:
        zoom_level = 10
    elif distance < 1000:
        zoom_level = 8
    elif distance < 2000:
        zoom_level = 7
    elif distance < 5000:
        zoom_level = 5
    else:
        zoom_level = 3

    m = Map(get_mid_point(start_coord, end_coord), zoom_start=zoom_level, tiles="openstreetmap")
    satellite = TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Satellite"
    )
    borders = TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer"
              "/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Borders & Labels",
        overlay=True,
        control=False
    )
    satellite_group = FeatureGroup(name="Satellite + Borders", overlay=False, show=False).add_to(m)
    satellite_group.add_child(satellite)
    satellite_group.add_child(borders)
    LayerControl().add_to(m)
    curve_points = great_circle_points(
        start_coord, end_coord
    )
    add_arrow(start_coord, end_coord, dep, m)
    add_arrow(end_coord, start_coord, des, m, True)
    add_wind(weather, m)
    plane_index = len(curve_points) // 8

    # Adding Bézier curve to the map
    PolyLine(curve_points[::-1], color="red", opacity=0.5).add_to(m)
    tiny_line = PolyLine(curve_points[:-plane_index][::-1], color="transparent").add_to(m)

    # Add plane to the line
    attr = {"fill": "red", "font-weight": "bold", "font-size": "30"}
    plugins.PolyLineTextPath(
        tiny_line,
        "\u2708",  # Plane unicode symbol
        repeat=False,
        orientation=180,
        attributes=attr,
    ).add_to(m)

    # Set the height to 100% in order to avoid an unnecessary scrollbar
    m.get_root().height = "100%"
    m.get_root().width = "100%"
    return m


def add_wind(weather: list[dict], m: Map):
    return;
    for data in weather:
        print(data)
        coord: tuple[float,float] = data["coord"]
        direction : float = data["wind_direction"]
        speed : float = data["wind_speed"]
        locations = geodesic(kilometers=10).destination(coord[::-1], bearing=direction*180)
        AntPath(locations=[coord, [locations.longitude, locations.latitude]]).add_to(m)


# Route to render the map with dynamic coordinates
@app.route('/map', methods=['GET'])
def serve_map():
    # Get the latitude and longitude from the request's query parameters (default to some coordinates if not provided)
    start_lat = request.args.get('start_lat', default=34.0522, type=float)  # Default to Los Angeles latitude
    start_lon = request.args.get('start_lon', default=-118.2437, type=float)  # Default to Los Angeles longitude
    end_lat = request.args.get('end_lat', default=32.0853, type=float)  # Default to Tel Aviv latitude
    end_lon = request.args.get('end_lon', default=34.7818, type=float)  # Default to Tel Aviv longitude
    dep = request.args.get("dep", default="KLAX", type=str)
    des = request.args.get("des", default="KTLV", type=str)
    weather_data = json.loads(request.args.get("weather_data"))

    # Create the map centered on the start coordinates
    m = create_map((start_lat, start_lon), (end_lat, end_lon), dep, des, weather_data)
    # Generate the HTML representation of the map
    map_html = m._repr_html_()
    return map_html


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Render will set the PORT environment variable
    app.run(host='0.0.0.0', port=port)  # Bind to 0.0.0.0 to be accessible externally
