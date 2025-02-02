import numpy as np

def avg(i: float, j: float) -> float:
    return (i+j)/2

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
