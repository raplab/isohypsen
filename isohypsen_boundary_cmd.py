import rhinoscriptsyntax as rs
import Rhino

__commandname__ = "isohypsen_boundary"

def check_z(curves, boundary):

    b_mid_pt = rs.CurveMidPoint(boundary)

    coplanar_list = []

    for c in curves:
        c_mid_pt = rs.CurveMidPoint(c)
        if c_mid_pt.Z == b_mid_pt.Z:
            coplanar_list.append(Coplanar([c],c_mid_pt,b_mid_pt.Z,boundary,False))
            #print "curve is coplanar"
        else:
            coplanar_list.append(Coplanar([c],c_mid_pt,b_mid_pt.Z,boundary,True))
            #print "curve is not coplanar"

    return coplanar_list

class Coplanar:
    
    def __init__(self, crv, mid_pt, boundary_z, boundary, moved):
        self.moved = moved
        self.crv = crv
        self.translate = ""
        self.mid_pt = mid_pt
        self.boundary_z = boundary_z
        self.boundary = boundary
        self.curve_list = []
        if moved:
            self.Z = self.mid_pt.Z*(-1)
        else:
            self.Z = self.boundary_z
        
        self.translate = rs.CreatePoint(0,0,self.Z)
        
        if self.moved:
            self.translate_z()

    def translate_z(self):
        rs.MoveObject(self.crv, self.translate)
        
    def ccx_split(self, curve, boundary):
        split_curves = []
        intersection = rs.CurveCurveIntersection(curve, boundary)
        if intersection:
            params = []
            for i in intersection:
                if i[0] == 1:
                    params.append(rs.CurveClosestPoint(curve,i[1]))
            split_result = rs.SplitCurve(curve, params)
            split_curves.append(split_result)
        else:
            split_curves.append(curve)

        crv_list = []
        for sp in split_curves:
            for s in sp:
                crv_list.append(s)

        self.curve_list = crv_list
        return True
            
    def del_crvs(self, in_or_out):
        tmp_crvs = []

        for c in self.curve_list:
            mid_pt = rs.CurveMidPoint(c)
            inside = rs.PointInPlanarClosedCurve(mid_pt,self.boundary)
            if inside == 1 and in_or_out == True:
                rs.DeleteObject(c)
            elif inside == 0 and in_or_out == False:
                rs.DeleteObject(c)
            else:
                tmp_crvs.append(c)
        self.curve_list = tmp_crvs

    def reset_z(self):
        if self.moved:
            for c in self.curve_list:
                start = rs.CurveStartPoint(c)
                end = rs.CurveStartPoint(c)
                end.Z = self.Z
                translate = start-end
                rs.MoveObject(c, translate)

def RunCommand( is_interactive ):
    
    #EXAMPLE
    crv_to_split = rs.GetObjects("select curves to split", 4)
    boundary = rs.GetObject("select boundary", 4)
    
    if crv_to_split and boundary:
        rs.EnableRedraw(False)
        coplanar_curves = check_z(crv_to_split, boundary)
        for c in coplanar_curves:
            split_result = c.ccx_split(c.crv, c.boundary)
            if split_result:
                c.del_crvs(False)
                c.reset_z()
        rs.EnableRedraw(True)
    else: 
        print "ERROR - no curves selected!"
    return 0
    

RunCommand(True)
