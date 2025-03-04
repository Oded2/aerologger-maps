import os

from flask import Flask, request
from folium import Map, plugins, PolyLine, TileLayer, LayerControl, FeatureGroup
from folium.plugins import AntPath
from geopy.distance import geodesic
from flask_cors import cross_origin
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

    add_arrow(start_coord, end_coord, dep, m)
    if distance==0:
        return m
    add_arrow(end_coord, start_coord, des, m, True)
    curve_points = great_circle_points(start_coord, end_coord)
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
    for i in range(len(weather)-1):
        coord: [float, float] = weather[i]["coord"]
        next_coord : [float, float] = weather[i+1]["coord"]
        points = great_circle_points(coord, next_coord, 10)
        speed : float = weather[i]["wind_speed"]
        # direction: float = data["wind_direction"]
        # speed: float = data["wind_speed"]
        # locations = geodesic(kilometers=10).destination(coord, bearing=direction * 180)
        # AntPath(locations=[coord, [locations.longitude, locations.latitude]]).add_to(m)
        AntPath(
            locations=points, dash_array=[20, 30], delay=speed*20
        ).add_to(m)


# Modified route to accept POST and JSON data
@app.route('/map', methods=['POST'])
@cross_origin()
def serve_map():
    data = request.get_json()
    if data is None:
        return "No JSON data provided", 400

    start_lat = data.get('start_lat', 34.0522)
    start_lon = data.get('start_lon', -118.2437)
    end_lat = data.get('end_lat', 32.0853)
    end_lon = data.get('end_lon', 34.7818)
    dep = data.get("dep", "KLAX")
    des = data.get("des", "KTLV")
    weather_data = data.get("weather_data", [])

    # Create the map using provided data
    m = create_map((start_lat, start_lon), (end_lat, end_lon), dep, des, weather_data)
    # Return the HTML representation of the map
    map_html = m._repr_html_()
    return map_html


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Render will set the PORT environment variable
    app.run(host='0.0.0.0', port=port)  # Bind to 0.0.0.0 to be accessible externally
