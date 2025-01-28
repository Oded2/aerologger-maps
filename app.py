from flask import Flask, request
import folium
from folium import Map, plugins
import numpy as np
from geopy.distance import geodesic
import os


app = Flask(__name__)


def create_map(start_coord: tuple[float,float], end_coord: tuple[float, float]):
    mid_coord = ((start_coord[0]+end_coord[0]/2), (start_coord[1]+end_coord[1])/2)
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
    m = Map(mid_coord, zoom_start=zoom_level)

    curve_points = great_circle_points(
        start_coord, end_coord
    )

    # Adding Bézier curve to the map
    curve_line = folium.PolyLine(curve_points[::-1], color="red", opacity=0.5).add_to(m)

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
    return m


# Convert degrees to radians
def deg_to_rad(deg):
    return deg * np.pi / 180


# Convert radians to degrees
def rad_to_deg(rad):
    return rad * 180 / np.pi


# Function to calculate the intermediate points along the great-circle route
def great_circle_points(start_lat_lon: tuple, end_lat_lon: tuple, n_points=100):
    # Convert latitude and longitude from degrees to radians
    start_lat_lon_rad = np.radians(start_lat_lon)
    end_lat_lon_rad = np.radians(end_lat_lon)

    # Calculate the central angle between the two points
    delta_sigma = np.arccos(np.sin(start_lat_lon_rad[0]) * np.sin(end_lat_lon_rad[0]) +
                            np.cos(start_lat_lon_rad[0]) * np.cos(end_lat_lon_rad[0]) *
                            np.cos(end_lat_lon_rad[1] - start_lat_lon_rad[1]))

    # Interpolate points along the great-circle path
    t = np.linspace(0, 1, n_points)
    intermediate_points = np.zeros((n_points, 2))

    for i, _t in enumerate(t):
        # Calculate the spherical linear interpolation (SLERP) between the two points
        A = np.sin((1 - _t) * delta_sigma) / np.sin(delta_sigma)
        B = np.sin(_t * delta_sigma) / np.sin(delta_sigma)

        x = A * np.cos(start_lat_lon_rad[0]) * np.cos(start_lat_lon_rad[1]) + \
            B * np.cos(end_lat_lon_rad[0]) * np.cos(end_lat_lon_rad[1])
        y = A * np.cos(start_lat_lon_rad[0]) * np.sin(start_lat_lon_rad[1]) + \
            B * np.cos(end_lat_lon_rad[0]) * np.sin(end_lat_lon_rad[1])
        z = A * np.sin(start_lat_lon_rad[0]) + B * np.sin(end_lat_lon_rad[0])

        # Convert the Cartesian coordinates back to latitude and longitude
        lat = np.arctan2(z, np.sqrt(x ** 2 + y ** 2))
        lon = np.arctan2(y, x)

        intermediate_points[i] = np.degrees([lat, lon])

    return intermediate_points.tolist()

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

