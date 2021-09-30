import heapq
import math

import Rhino
import rhinoscriptsyntax as rs

"""
Pole of inaccessibility label script for Rhino 7
Finds the largest inscribed circle in any polygon or curve

This code is adopted for Rhino Python from the implementation by Toblerity
https://github.com/Toblerity/Shapely/blob/master/shapely/algorithms/polylabel.py

and based on an the original algorithm by Vladimir Agafonkin
https://github.com/mapbox/polylabel

Polylabel Mapbox Post
https://blog.mapbox.com/a-new-algorithm-for-finding-a-visual-center-of-a-polygon-7c77e6492fbc

The shortest distance between point and curve part is based on this post:
https://discourse.mcneel.com/t/confused-about-behavior-of-curve-closestpoint/79936/2
"""


class Cell:

    def __init__(self, x, y, h, polygon):
        """
        create object to store cell data
        :param x: 3d point
        :param y: 3d point
        :param h: height and with of the cell
        :param polygon: polygon or curve to test
        """
        self.x = x
        self.y = y
        self.h = h
        self.polygon = polygon
        self.centroid = [x + (h / 2.0), y + (h / 2.0), 0]
        self.radius_dist = (h * 1.4142135623730951) / 2.0  # "radius_dist" equals the diagonal times sqr(2) divided by 2
        self.distance = self.calc_cell_dist()
        self.max_distance = self.distance + self.radius_dist

    # rich comparison operators for sorting in minimum priority queue
    def __lt__(self, other):
        return self.max_distance > other.max_distance

    def __le__(self, other):
        return self.max_distance >= other.max_distance

    def __eq__(self, other):
        return self.max_distance == other.max_distance

    def __ne__(self, other):
        return self.max_distance != other.max_distance

    def __gt__(self, other):
        return self.max_distance < other.max_distance

    def __ge__(self, other):
        return self.max_distance <= other.max_distance

    def render_quad(self):
        """
        renders the recursive quads for visualisation purpose
        """
        pline = [[self.x, self.y, 0], [self.x + self.h, self.y, 0], [self.x + self.h, self.y + self.h, 0],
                 [self.x, self.y + self.h, 0], [self.x, self.y, 0]]
        rs.AddPolyline(pline)

    def render_circle(self):
        """
        renders the circle of inaccessibility
        """
        rs.addCircle(self.centroid, self.distance)

    def calc_cell_dist(self):
        """
        calculate the weight of the quad and return positive number if the centroid falls inside the polygon
        :return: float
        """
        param = rs.CurveClosestPoint(self.polygon, self.centroid)
        crv_pt = rs.EvaluateCurve(self.polygon, param)

        quad_weight = rs.Distance(self.centroid, crv_pt)

        in_out_check = rs.PointInPlanarClosedCurve(self.centroid, self.polygon)

        if in_out_check == 0:
            quad_weight = -quad_weight
        return quad_weight


def circle_of_inaccessibility(polygon, tolerance=1.0):
    """
    find largest inscribed circle of any polygon or closed curve
    :param polygon: polygon or curve object
    :param tolerance: float, default 1.0
    :return: 3d point that defines the center of the largest inscribed circle of the polygon
    """
    bbox = rs.BoundingBox(polygon)
    bbox_width = rs.Distance(bbox[0], bbox[1])
    bbox_height = rs.Distance(bbox[1], bbox[2])

    cell_size = min(bbox_width, bbox_height)

    cell_size = cell_size / 6

    minX = bbox[0].X
    minY = bbox[0].Y

    xcount = math.ceil(bbox_width / cell_size)
    ycount = math.ceil(bbox_height / cell_size)

    cell_queue = []

    # start with a comparison cell that is equal to the centroid of the polygon
    polygon_centroid = rs.CurveAreaCentroid(polygon)
    best_cell = Cell(polygon_centroid[0].X - (cell_size / 2), polygon_centroid[0].Y - (cell_size / 2), cell_size,
                     polygon)

    for i in range(0, int(xcount)):
        for j in range(0, int(ycount)):
            c = Cell(minX + (i * cell_size), minY + (j * cell_size), cell_size, polygon)
            heapq.heappush(cell_queue, c)

    while cell_queue:
        cell = heapq.heappop(cell_queue)

        if cell.distance > best_cell.distance:
            best_cell = cell

        if cell.max_distance - best_cell.distance <= tolerance:
            continue

        h = cell.h / 2.0
        heapq.heappush(cell_queue, Cell(cell.x, cell.y, h, polygon))
        heapq.heappush(cell_queue, Cell(cell.x + h, cell.y, h, polygon))
        heapq.heappush(cell_queue, Cell(cell.x, cell.y + h, h, polygon))
        heapq.heappush(cell_queue, Cell(cell.x + h, cell.y + h, h, polygon))

    return best_cell.centroid
