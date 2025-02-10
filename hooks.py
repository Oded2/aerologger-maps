import numpy as np
from folium import Map, Marker, Icon

def avg(i: float, j: float) -> float:
    return (i + j) / 2


def get_mid_point(start: tuple[float, float], end: tuple[float, float]):
    return avg(start[0], end[0]), avg(start[1], end[1])


# Function to calculate the intermediate points along the great-circle route
def great_circle_points(start_lat_lon: tuple, end_lat_lon: tuple, n_points=100):
    """
    Calculate intermediate points along the great-circle route between two geographic coordinates.

    Parameters:
    - start_lat_lon: A tuple (latitude, longitude) for the starting point in degrees.
    - end_lat_lon: A tuple (latitude, longitude) for the ending point in degrees.
    - n_points: The number of intermediate points to generate along the path.

    Returns:
    - A list of [latitude, longitude] pairs representing points along the great-circle path.
    """
    # Convert starting and ending points from degrees to radians.
    start_lat_rad, start_lon_rad = np.radians(start_lat_lon)
    end_lat_rad, end_lon_rad = np.radians(end_lat_lon)

    # Calculate the central angle between the two points on the sphere using the spherical law of cosines.
    central_angle = np.arccos(
        np.sin(start_lat_rad) * np.sin(end_lat_rad) +
        np.cos(start_lat_rad) * np.cos(end_lat_rad) * np.cos(end_lon_rad - start_lon_rad)
    )

    # Generate an array of interpolation fractions from 0 (start) to 1 (end).
    interpolation_fractions =(np.linspace(0, 1, n_points))
    intermediate_points = np.zeros((n_points, 2))


    # Calculate each intermediate point using spherical linear interpolation (SLERP).
    for index in range(len(interpolation_fractions)):
        fraction = interpolation_fractions[index]
        # Compute the SLERP coefficients for the starting and ending points.
        coefficient_start = np.sin((1 - fraction) * central_angle) / np.sin(central_angle)
        coefficient_end = np.sin(fraction * central_angle) / np.sin(central_angle)

        # Convert the interpolated point from spherical to Cartesian coordinates.
        cartesian_x = (coefficient_start * np.cos(start_lat_rad) * np.cos(start_lon_rad) +
                       coefficient_end * np.cos(end_lat_rad) * np.cos(end_lon_rad))
        cartesian_y = (coefficient_start * np.cos(start_lat_rad) * np.sin(start_lon_rad) +
                       coefficient_end * np.cos(end_lat_rad) * np.sin(end_lon_rad))
        cartesian_z = (coefficient_start * np.sin(start_lat_rad) +
                       coefficient_end * np.sin(end_lat_rad))

        # Convert the Cartesian coordinates back to spherical (latitude, longitude) coordinates.
        interpolated_lat_rad = np.arctan2(cartesian_z, np.sqrt(cartesian_x ** 2 + cartesian_y ** 2))
        interpolated_lon_rad = np.arctan2(cartesian_y, cartesian_x)

        # Convert the result from radians back to degrees and store it.
        intermediate_points[index] = np.degrees([interpolated_lat_rad, interpolated_lon_rad])

    return intermediate_points.tolist()


def add_arrow(coord: tuple[float, float], relative_coord: tuple[float, float], tooltip: str, m: Map) -> None:
    angle: int = 0
    is_north: bool = relative_coord[0]-coord[0] > 0
    is_west: bool = relative_coord[1]-coord[1] < 0
    if is_north and is_west:
        angle = 315
    elif is_north and not is_west:
        angle = 45
    elif not is_north and is_west:
        angle = 225
    elif not is_north and not is_west:
        angle = 135
    Marker(location=coord, tooltip=tooltip, icon=Icon(prefix="fa", color="green", icon="arrow-up", angle=angle)).add_to(
        m)
