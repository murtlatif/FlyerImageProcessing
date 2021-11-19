
from __future__ import annotations

from dataclasses import dataclass
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon


@dataclass
class Vertex:
    x: int
    y: int

    @staticmethod
    def from_dict(vertex_dict: dict[str, int]) -> Vertex:
        return Vertex(x=vertex_dict.x, y=vertex_dict.y)


Region = list[Vertex]


def distance_between_regions(region: Region, other_region: Region) -> float:
    polygon = _region_to_polygon(region)
    other_polygon = _region_to_polygon(other_region)

    return polygon.distance(other_polygon)


def get_region_area(region: Region) -> float:
    polygon = _region_to_polygon(region)
    return polygon.area


def is_vertex_in_region(region: Region, target_vertex: Vertex) -> bool:
    """
    Uses Shapely to determine if a vertex is inside a given region.

    Args:
        region (Region): Vertices of the polygon region
        target_vertex (Vertex): Target vertex to check

    Returns:
        bool: Whether the target vertex is in the region
    """
    polygon = _region_to_polygon(region)
    target_point = _vertex_to_point(target_vertex)
    return polygon.contains(target_point)


def does_region_intersect(region: Region, other_region: Region) -> bool:
    """
    Uses Shapely to determine if a region intersects another region.

    Args:
        region (Region): Target region
        other_region (Region): Other region

    Returns:
        bool: Whether the two given regions intersect
    """
    region_polygon = _region_to_polygon(region)
    other_region_polygon = _region_to_polygon(other_region)

    return region_polygon.intersects(other_region_polygon)


def _region_to_polygon(region: Region) -> Polygon:
    region_points = [(point.x, point.y) for point in region]
    polygon = Polygon(region_points)
    return polygon


def _vertex_to_point(vertex: Vertex) -> Point:
    point = Point(vertex.x, vertex.y)
    return point
