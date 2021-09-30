import quadSubdivision as qs
import rhinoscriptsyntax as rs
from Rhino.Geometry import *
from System.Drawing import Color

__commandname__ = "isohypsen_layout"


def layout_curves(surface_unsorted, perimeter, kadaster):
    """
    prepare cutting data by creating layers and distributing the curves/layers in X
    
    :param surface_unsorted:
    :param perimeter:
    :param kadaster:
    """
    surface = sort_by_z(surface_unsorted)
    # calculate offset
    bbox = rs.BoundingBox(perimeter)
    dist = rs.Distance(bbox[0], bbox[1])
    dist = dist + ((dist / 100) * 10)
    # create point start and end points to move lines back to Z0
    start_pt = rs.CreatePoint(0, 0, 0)
    end_pt = start_pt

    # Create layers to structure the output
    cut_layer = "Cutting"
    rs.AddLayer(cut_layer)
    engrave_layer = "Engraving"
    rs.AddLayer(engrave_layer)
    guides_layer = "Guides"
    rs.AddLayer(guides_layer)
    labels_layer = "Labels"
    rs.AddLayer(labels_layer)

    for i in range(0, len(surface)):

        # calculate increasing X-offset to translate all the objects
        end_pt.X = end_pt.X + (dist)
        end_pt.Z = -surface[i][0]
        translation = end_pt

        for j in range(1, len(surface[i])):
            projected_crvs = rs.ProjectCurveToSurface(kadaster, surface[i][j], (0, 0, -1))
            border = rs.DuplicateSurfaceBorder(surface[i][j])
            rs.MoveObject(projected_crvs, translation)

            rs.MoveObject(border, translation)
            rs.ObjectLayer(border, cut_layer)
            rs.ObjectColor(border, Color.Red)
            rs.ObjectPrintWidth(border, 0)

            # for everything but the top layer
            boundaries_to_trim = []
            if i >= 1:
                # duplicate and projected border from layer above
                for ij in range(1, len(surface[i - 1])):
                    top_border = rs.DuplicateSurfaceBorder(surface[i - 1][ij])
                    end_pt.Z = -surface[i - 1][0]
                    translation_a = end_pt
                    rs.MoveObject(top_border, translation_a)
                    boundaries_to_trim.append(top_border)

                    if top_border:
                        # add layer information and labels
                        id = str(i + 1) + "." + str(ij) + "/" + str(i) + "." + str(ij)
                        if len(top_border) >1:
                            top_border = largest_polygon(top_border)
                        label_point = qs.circle_of_inaccessibility(top_border[0], 5.0)

                        font = ["SLF-RHN Architect", "RhSS"]
                        label = rs.AddText(id, label_point, 1, font[0], 0, 2)
                        exploded_label_crvs = rs.ExplodeText(label, True)
                        rs.ObjectLayer(exploded_label_crvs, labels_layer)
                        rs.ObjectColor(exploded_label_crvs, Color.Black)
                        rs.ObjectPrintWidth(exploded_label_crvs, 0)

                        rs.ObjectLayer(top_border, guides_layer)
                        rs.ObjectColor(top_border, Color.Chartreuse)
                        rs.ObjectPrintWidth(top_border, 0)

                    if projected_crvs:
                        rs.ObjectLayer(projected_crvs, engrave_layer)
                        rs.ObjectColor(projected_crvs, Color.Black)
                        rs.ObjectPrintWidth(projected_crvs, 0)


            else:
                rs.ObjectLayer(projected_crvs, engrave_layer)
                rs.ObjectColor(projected_crvs, Color.Black)
                rs.ObjectPrintWidth(projected_crvs, 0)

            try:
                if projected_crvs and label:
                    c = ccx_split(projected_crvs, boundaries_to_trim, len(boundaries_to_trim))
                    inside_crv_del(c, boundaries_to_trim, True)

            except:
                pass

def largest_polygon(polygon):
    polygon_area = {}
    for p in polygon:
            area = rs.CurveArea(p)
            polygon_area[p] = area
    polygon = max(polygon_area, key=polygon_area.get)
    return [polygon]

def ccx_split(curves, boundary, last):
    """
    split all curves that intersect with a set of boundaries
    :param curves: curves to be split
    :param boundary: boundaries to split the curves with
    :param last: boundary list length for recursive function
    :return: list of curves
    """
    split_curves = []
    for c in curves:
        intersections = rs.CurveCurveIntersection(c, boundary[last - 1])
        if intersections:
            params = []
            for i in intersections:
                if i[0] == 1:
                    params.append(rs.CurveClosestPoint(c, i[1]))
            split_result = rs.SplitCurve(c, params)
            split_curves.append(split_result)
        else:
            split_curves.append(c)

    curve_list = []
    for i in range(0, len(split_curves)):
        if isinstance(split_curves[i], list):
            for j in range(0, len(split_curves[i])):
                curve_list.append(split_curves[i][j])
        else:
            curve_list.append(split_curves[i])
    next = last - 1
    
    if next >= 0:
        return ccx_split(curve_list, boundary, next)
    else:
        return curve_list


def inside_crv_del(split_curves, boundary, in_or_outside):
    """
    delete all curves in- or outside of a list of given boundaries
    :param split_curves: curves to be deleted
    :param boundary: boundaries to split the curves with
    :param in_or_outside: True = delete inside, False = delete outside
    """
    for crv in split_curves:
        mid_pt = rs.CurveMidPoint(crv)
        for bc in boundary:
            inside = rs.PointInPlanarClosedCurve(mid_pt, bc)
            # delete inside 
            if inside == 1 and in_or_outside == True:
                rs.DeleteObject(crv)
                break
            # delete outside 
            if inside == 0 and in_or_outside == False:
                rs.DeleteObject(crv)
                break


def sort_by_z(obj):
    """
    sorts curves by z-index

    :param obj: list of curves to be sorted
    :return:
    """
    unsorted_obj = []
    unsorted_z = []
    for o in obj:
        centroid = rs.SurfaceAreaCentroid(o)
        unsorted_obj.append([centroid[0].Z, o])
        unsorted_z.append(centroid[0].Z)
    sorted_z = sorted(set(unsorted_z), reverse=True)

    sorted_obj = []
    for i in range(0, len(sorted_z)):
        sorted_obj.append([sorted_z[i]])
        for j in range(0, len(unsorted_z)):
            if unsorted_obj[j][0] == sorted_z[i]:
                sorted_obj[i].append(unsorted_obj[j][1])
                del unsorted_obj[j][1]
    return sorted_obj


def RunCommand( is_interactive ):
    print "__commandname__"
    contours = rs.GetObjects("select contour surfaces", 8)
    kadaster = rs.GetObjects("select engraving data", 4)
    perimeter = rs.GetObject("select perimeter", 4)
    if contours and kadaster and perimeter:
        print "starting to generate layout..."
        print "processing..."

        rs.EnableRedraw(False)
        layout_curves(contours, perimeter, kadaster)
        rs.EnableRedraw(True)

        print "layout has been created!"
    else:
        print "ERROR - no selection was made!"
    
    return 0


#RunCommand(True)
