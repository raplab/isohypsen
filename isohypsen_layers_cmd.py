import rhinoscriptsyntax as rs
import scriptcontext


__commandname__ = "isohypsen_layers"

# RunCommand is the called when the user enters the command name in Rhino.
# The command name is defined by the filname minus "_cmd.py"
def RunCommand( is_interactive ):
    
    rs.EnableRedraw(False)
    
    parent_layer = rs.AddLayer("CADASTRE_DATA")
    
    layers_to_keep = { "01211":"Buildings", "01221":"Streets", "01229":"Street_Names", "01311":"Building_Details", "01316":"Bridges", "01611":"Plot", "01241":"Stretch_Of_Water", "01334":"Train_Tracks"}
    
    layers = rs.LayerNames()
    
    for l in layers:
        
        if l[0]=='0':
            
            keep = False

            for k, v in layers_to_keep.items():
                if l == k:
                    if not rs.IsLayerEmpty(l):
                        name = l+" "+v
                        rs.RenameLayer(l, name)
                        rs.ParentLayer(name,parent_layer)
                        keep = True
            if keep == False:
                removed = rs.PurgeLayer(l)
                if not removed:
                    objects = rs.ObjectsByLayer(l, False)
                    print(l, " ", objects)
                
    font = ["SLF-RHN Architect", "RhSS"]
    
    text =scriptcontext.doc.Objects.FindByLayer("01229 Street_Names")
    
    if text:
        for t in text:
            rs.TextObjectFont(t, font[0])
            rs.ExplodeText(t, True)
            rs.DeleteObject(t)
    
    rs.EnableRedraw(True)

    return 0
