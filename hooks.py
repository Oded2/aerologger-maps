from folium import Map, Marker, Icon, CustomIcon



def avg(i: float, j: float) -> float:
    return (i + j) / 2


def get_mid_point(start: tuple[float, float], end: tuple[float, float]):
    return avg(start[0], end[0]), avg(start[1], end[1])


def add_arrow(coord: tuple[float, float], relative_coord: tuple[float, float], tooltip: str, m: Map,
              flipped: bool = False) -> None:
    """
    Adds an arrow marker to a map at a specified location, pointing in the direction of a relative coordinate.

    Parameters:
        coord (tuple[float, float]): The base (latitude, longitude) where the arrow will be placed.
        relative_coord (tuple[float, float]): Another (latitude, longitude) used to determine the arrow's direction.
        tooltip (str): A tooltip to show when hovering over the arrow.
        m (Map): The Folium map object to which the marker is added.
        flipped (bool): If True, the arrow is flipped 180 degrees.
    """

    # Default angle pointing northeast (used if direction is north and east)
    angle: int = 45

    # Determine if the relative coordinate is north and/or west of the base coordinate
    is_north: bool = relative_coord[0] - coord[0] > 0
    is_west: bool = relative_coord[1] - coord[1] < 0

    # Set the arrow's angle based on relative position
    if is_north and is_west:
        angle = 315  # Northwest
    elif is_north and not is_west:
        angle = 45  # Northeast
    elif not is_north and is_west:
        angle = 225  # Southwest
    elif not is_north and not is_west:
        angle = 135  # Southeast

    # Flip the arrow if requested
    if flipped:
        angle = (angle + 180) % 360

    # Create and add the marker with the appropriate icon and angle to the map
    Marker(
        location=coord,
        tooltip=tooltip,
        icon=Icon(prefix="fa", color="green", icon="arrow-up", angle=angle)
    ).add_to(m)


def add_wind(wind, m: Map):
    custom_icon = CustomIcon(icon_image="images/wind.png", icon_size=(50, 50), icon_anchor=(25, 25))
    Marker(location=wind["coord"][::-1], icon=custom_icon, tooltip=f"{wind["wind_direction"]}/{wind["wind_speed"]}KN").add_to(m)