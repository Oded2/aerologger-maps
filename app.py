import os

from flask import Flask, request
from flask_cors import cross_origin
from folium import Map, plugins, PolyLine, TileLayer, LayerControl, FeatureGroup
from geopy.distance import geodesic

from hooks import get_mid_point, add_arrow, add_wind

app = Flask(__name__)


def create_map(points: list[[float, float]], dep: str, des: str,
               weather: list[dict]) -> Map:
    start_coord = points[0]
    end_coord = points[-1]
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
    if distance == 0:
        return m
    add_arrow(end_coord, start_coord, des, m, True)
    plane_index = len(points) // 8
    if weather:
        for w in weather:
            add_wind(w,m)

    # Add the route based on the points received from the client
    PolyLine(points, color="red", opacity=0.5).add_to(m)
    tiny_line = PolyLine(points[:-plane_index][::-1], color="transparent").add_to(m)

    # Add plane to the line
    attr = {"fill": "red", "font-weight": "bold", "font-size": "30"}
    plugins.PolyLineTextPath(
        tiny_line,
        "\u2708", # Plane unicode symbol
        repeat=False,
        orientation=180,
        attributes=attr,
    ).add_to(m)

    # Set the height to 100% in order to avoid an unnecessary scrollbar
    m.get_root().height = "100%"
    m.get_root().width = "100%"
    return m


# Modified route to accept POST and JSON data
@app.route('/map', methods=['POST'])
@cross_origin()
def serve_map():
    data = request.get_json()
    if data is None:
        return "No JSON data provided", 400
    points = data.get("points", [])
    dep = data.get("dep", "KLAX")
    des = data.get("des", "KTLV")
    weather_data = data.get("weather_data", [])

    # Create the map using provided data
    m = create_map(points, dep, des, weather_data)
    # Return the HTML representation of the map
    map_html = m.get_root().render()
    return map_html


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))  # Render will set the PORT environment variable
    app.run(host='0.0.0.0', port=port)  # Bind to 0.0.0.0 to be accessible externally
