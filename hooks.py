from folium import Map, Marker, Icon


def avg(i: float, j: float) -> float:
    return (i + j) / 2


def get_mid_point(start: tuple[float, float], end: tuple[float, float]):
    return avg(start[0], end[0]), avg(start[1], end[1])


def add_arrow(coord: tuple[float, float], relative_coord: tuple[float, float], tooltip: str, m: Map,
              flipped: bool = False) -> None:
    angle: int = 45
    is_north: bool = relative_coord[0] - coord[0] > 0
    is_west: bool = relative_coord[1] - coord[1] < 0
    if is_north and is_west:
        angle = 315
    elif is_north and not is_west:
        angle = 45
    elif not is_north and is_west:
        angle = 225
    elif not is_north and not is_west:
        angle = 135
    if flipped:
        angle = (angle + 180) % 360
    Marker(location=coord, tooltip=tooltip, icon=Icon(prefix="fa", color="green", icon="arrow-up", angle=angle)).add_to(
        m)
