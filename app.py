from flask import Flask, request
from folium import Map, plugins, Marker, Icon, PolyLine
from geopy.distance import geodesic
import os
from hooks import avg, great_circle_points


app = Flask(__name__)


def create_map(start_coord: tuple[float,float], end_coord: tuple[float, float]) -> Map:
    distance = geodesic(start_coord, end_coord).kilometers

    # Determine zoom level based on distance
    if distance < 500:
        zoom_level = 10
    elif distance < 1000:
        zoom_level = 8
    elif distance < 2000:
        zoom_level = 7
    else:
        zoom_level = 3

    mid_point = [avg(start_coord[0], end_coord[0]), avg(start_coord[1], end_coord[1])]
    m = Map(mid_point, zoom_start=zoom_level)

    curve_points = great_circle_points(
        start_coord, end_coord
    )
    Marker(location=start_coord, tooltip="Departure Airport", icon=Icon(prefix="fa", color="green", icon="arrow-up", angle=45)).add_to(m)

    # Adding Bézier curve to the map
    curve_line = PolyLine(curve_points[::-1], color="red", opacity=0.5).add_to(m)

    # Add plane to the line
    attr = {"fill": "red", "font-weight": "bold", "font-size": "30"}

    plugins.PolyLineTextPath(
        curve_line,
        "\u2708",  # Plane unicode symbol
        repeat=False,
        offset=14.5,
        orientation=180,
        attributes=attr,
    ).add_to(m)
    m.get_root().height="100%"
    return m

# Route to render the map with dynamic coordinates
@app.route('/map', methods=['GET'])
def serve_map():
    # Get the latitude and longitude from the request's query parameters (default to some coordinates if not provided)
    start_lat = request.args.get('start_lat', default=37.7749, type=float)  # Default to San Francisco latitude
    start_lon = request.args.get('start_lon', default=-122.4194, type=float)  # Default to San Francisco longitude
    end_lat = request.args.get('end_lat', default=32.0853, type=float)  # Default to Tel Aviv latitude
    end_lon = request.args.get('end_lon', default=34.7818, type=float)  # Default to Tel Aviv longitude

    # Create the map centered on the start coordinates
    m = create_map((start_lat, start_lon), (end_lat, end_lon))
    # Generate the HTML representation of the map
    map_html = m._repr_html_()
    return map_html


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Render will set the PORT environment variable
    app.run(host='0.0.0.0', port=port)  # Bind to 0.0.0.0 to be accessible externally

