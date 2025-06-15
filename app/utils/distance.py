from math import atan2, cos, radians, sin, sqrt


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the distance between two geographical points using the Haversine
    formula.

    Parameters:
        lat1 (float): Latitude of the first point (my location) in decimal degrees
        lon1 (float): Longitude of the first point (my location) in decimal degrees
        lat2 (float): Latitude of the second point (carpark location) in decimal
                     degrees
        lon2 (float): Longitude of the second point (carpark location) in decimal
                     degrees

    Returns:
        float: The distance between the two points in kilometers
    """

    R = 6371

    # Convert coordinates to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Haversine formula
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c

    return distance
