import rhinoscriptsyntax as rs

__commandname__ = "isphypsen_init"


def curves_rebuild(curves, reduction):
    """
    Reduce the point count of a given set of curves
    :param curves: list of curves
    :param reduction: float between 0.1 and 0.9
    """
    if red < 1.0:
        for c in curves:
            p_reduction = rs.CurvePointCount(c) * reduction
            rs.RebuildCurve(c, 3, p_reduction)


def create_isohypsen_srf(curves, boundary, layer):
    """
    creates contour surface from open contour lines and a boundary
    :param curves: open contour lines
    :param boundary: closed curve
    :param boundary: layer name
    """
    for i in range(0, len(curves)):
        temp_str = ""
        for j in range(0, len(curves[i])):
            temp_str += " SelID " + str(curves[i][j])
        surface = rs.AddPlanarSrf(boundary)
        end = rs.CurveStartPoint(curves[i][0])
        start = rs.CurveStartPoint(boundary)
        end_pt = rs.CreatePoint(start[0], start[1], end[2])
        translation = end_pt - start
        rs.MoveObject(surface, translation)
        rs.Command("_Trim " + str(temp_str) + " _Enter")
        srf = rs.LastCreatedObjects()
        rs.ObjectLayer(srf, layer)


def sort_z(obj, dir):
    """
    sort curves by Z value 
    :param obj: list of curves distributed in Z
    :param obj: True = low to high, False = high to low
    :return: list of curves sorted by their c value
    """
    unsorted_obj = []
    unsorted_z = []
    for o in obj:
        centroid = rs.CurveMidPoint(o)
        z_value = round(centroid.Z, 1)
        unsorted_obj.append([z_value, o])
        unsorted_z.append(z_value)
    if dir:
        sorted_z = sorted(set(unsorted_z), reverse=False)
    else:
        sorted_z = sorted(set(unsorted_z), reverse=True)

    sorted_obj = []

    for i in range(0, len(sorted_z)):
        temp = []
        for j in range(0, len(unsorted_z)):
            if unsorted_obj[j][0] == sorted_z[i]:
                temp.append(unsorted_obj[j][1])
                del unsorted_obj[j][1]
        sorted_obj.append(temp)
    return sorted_obj

# RunCommand is the called when the user enters the command name in Rhino.
# The command name is defined by the filename minus "_cmd.py"
def RunCommand( is_interactive ):
    crv = rs.GetObjects("select contour lines", 4)
    per = rs.GetObject("select boundary", 4)
    red = rs.GetReal("Reduce point count to:", 0.5, 0.1, 1.0)  # 0.5 equals 50% of initial point count
    
    if crv and per:

        layer_contours = "Contour Surfaces"
        rs.AddLayer(layer_contours)
        contours_color = rs.CreateColor(255,0,0)
        rs.LayerColor(layer_contours, contours_color)
        
        layer_ocontours = "Original Contour Curves"
        rs.AddLayer(layer_ocontours)
        ocontours_color = rs.CreateColor(255,255,255)
        rs.LayerColor(layer_ocontours, ocontours_color)
        
        dup_curves = rs.CopyObjects(crv)
        rs.ObjectLayer(dup_curves, layer_ocontours)
        
        old_layer = rs.ObjectLayer(crv)

        curves_rebuild(crv, red)
        outline = sort_z(crv, True)
        create_isohypsen_srf(outline, per , layer_contours)
        
        rs.DeleteLayer(old_layer)
    
    else: 
        print "ERROR - no selection was made!"

    return 0
    
#RunCommand(True)

