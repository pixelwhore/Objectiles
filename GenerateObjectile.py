import Rhino
import scriptcontext
import System.Drawing


class Objectile():
    #todo make a function which writes all the Objectile data to a spreadsheet...
    
    def __init__(self, geo, s_max, r_max, h_max, height):
        
        self.base_geo = geo
        self.height = float(height)
        
        self.scale_min = 1.0
        self.rotation_min = 15.0
        self.height_min = 0.0
        
        self.scale_max = float(s_max)
        self.rotation_max = float(r_max)
        self.height_max = float(h_max)
        
        self.scale_stepcount = 5
        self.rotation_stepcount = 5
        self.height_stepcount = 5
        
        self.scale_stepval = (self.scale_max - self.scale_min)/float(self.scale_stepcount)
        self.rotation_stepval = (self.rotation_max - self.rotation_min)/float(self.rotation_stepcount)
        self.height_stepval = (self.height_max - self.height_min)/float(self.height_stepcount)
        
        if self.height_min == 0.0:
            self.height_min = self.height_stepval
            self.height_stepcount = self.height_stepcount - 1
        if self.height_max == self.height:
            self.height_max = self.height - self.height_stepval
            self.height_stepcount = self.height_stepcount - 1
        
        self.X_spacing = 20
        self.Y_spacing = 20
        self.Z_spacing = 20
        
        self.objects = {}
    
    def Generate(self):
        for f in range (1):
            for s in frange(self.scale_min, self.scale_stepval * (self.scale_stepcount + 1) + self.scale_min, self.scale_stepval):
                for r in frange(self.rotation_min, self.rotation_stepval * (self.rotation_stepcount + 1) + self.rotation_min, self.rotation_stepval):
                    for h in frange(self.height_min, self.height_stepval * (self.height_stepcount + 1) + self.height_min, self.height_stepval):
                        tag = (f, int((s-self.scale_min)/self.scale_stepval), int(r/self.rotation_stepval), int((h/self.height_stepval) - 1))
                        #tag = (f, s, r, h)
                        self.objects[tag] = OObject(self.base_geo, s, r, h, self.height, f)
                        self.objects[tag].Generate()
                        self.objects[tag].MakeTag(str(tag))
                        self.objects[tag].Move(self.X_spacing * tag[1] + tag[0] * (self.X_spacing * self.scale_stepcount + self.X_spacing * 2), self.Y_spacing * (tag[2] + 1), self.Z_spacing * tag[3])
        for key, object in self.objects.iteritems():
            object.Bake(str(tag))
    



class OObject():
    
    def __init__(self, geo, s_val, r_val, h_val, h_max, type):
        self.geometry = geo.Duplicate()
        
        self.scale = s_val
        self.rotation = r_val
        self.height = h_val
        self.max_height = h_max
        
        self.type = type
        
        self.tag = None
        
    def Generate(self):
        #draw curve 1
        if self.type == 0 or self.type == 3 or self.type == 5:
            self.c1 = self.geometry.Duplicate()
            self.c1.Scale(self.scale)
            self.c1.Rotate(Rhino.RhinoMath.ToRadians(self.rotation),Rhino.Geometry.Vector3d(0,0,1),Rhino.Geometry.Point3d(0,0,0))
        else:
            self.c1 = self.geometry

        #draw curve 2
        self.c2 = self.geometry.Duplicate()
        if self.type == 1 or self.type == 3 or self.type == 4:
            self.c2.Scale(self.scale)
            self.c2.Rotate(Rhino.RhinoMath.ToRadians(self.rotation),Rhino.Geometry.Vector3d(0,0,1),Rhino.Geometry.Point3d(0,0,0))
            self.c2.Translate(0,0,self.height)
        else:
            self.c2.Translate(0,0,self.height)
        
        #draw curve 3
        self.c3 = self.geometry.Duplicate()
        if self.type == 2 or self.type == 4 or self.type == 5:
            self.c3.Scale(self.scale)
            self.c3.Rotate(Rhino.RhinoMath.ToRadians(self.rotation),Rhino.Geometry.Vector3d(0,0,1),Rhino.Geometry.Point3d(0,0,0))
            self.c3.Translate(0,0,self.max_height)
        else:
            self.c3.Translate(0,0,self.max_height) 
            
        self.surf = Rhino.Geometry.Brep.CreateFromLoft([self.c1, self.c2, self.c3], Rhino.Geometry.Point3d.Unset, Rhino.Geometry.Point3d.Unset, Rhino.Geometry.LoftType.Straight, False)[0]
        self.surf.Flip()
    
    def MakeTag(self, label_text):
        self.tag = Rhino.Geometry.TextDot(label_text + "\nScale: " + str(self.scale) + "\nRotation: " + str(self.rotation) + "\nHeight: " + str(self.height), Rhino.Geometry.Point3d.Origin)
    
    def Move(self, x, y, z):
        if self.surf: 
            self.surf.Translate(x, y, z)
        
        if self.tag:
            self.tag.Translate(x, y, z)
        
        if self.c1 and self.c2 and self.c3:
            self.c1.Translate(x, y, z)
            self.c2.Translate(x, y, z)
            self.c3.Translate(x, y, z)
    
    def Bake(self, group_name):
        group = scriptcontext.doc.Groups.Add(group_name)
        
        if self.surf:
            attr = GenerateAttributes("Surface", System.Drawing.Color.Goldenrod, group)
            srf_guid = scriptcontext.doc.Objects.AddBrep(self.surf, attr)
        
        if self.tag:
            attr = GenerateAttributes("Tag", System.Drawing.Color.Gray, group)
            tag_guid = scriptcontext.doc.Objects.AddTextDot(self.tag, attr)
        
        if self.c1 and self.c2 and self.c3:
            attr = GenerateAttributes("Curves", System.Drawing.Color.Magenta, group)
            c1_guid = scriptcontext.doc.Objects.AddCurve(self.c1, attr)
            c2_guid = scriptcontext.doc.Objects.AddCurve(self.c2, attr)
            c3_guid = scriptcontext.doc.Objects.AddCurve(self.c3, attr)

def GenerateAttributes(layer_name, color, group):
    layer = Rhino.DocObjects.Layer()
    layer.Name = layer_name
    layer.Color = color 
    layer = scriptcontext.doc.Layers.Add(layer)
    
    attribute = Rhino.DocObjects.ObjectAttributes()
    attribute.AddToGroup(group)
    attribute.LayerIndex = scriptcontext.doc.Layers.Find(layer_name, True)
    
    return attribute
    
def frange(start, stop, step):
    #val = start
    while start < stop:
        yield start
        start += step

if __name__ ==  "__main__":
    #todo add more user inputs...
    Rhino.RhinoApp.ClearCommandHistoryWindow()
    test, base_geo = Rhino.Input.RhinoGet.GetOneObject("Select geo to generate objectile", False, None)
    if test == Rhino.Commands.Result.Success:
        my_objectile = Objectile(base_geo.Curve(), 2.0, 45.0, 10.0, 10.0)
        my_objectile.Generate()
    else:
        print("Selection failed...")
    print("Complete!")