import Rhino
import scriptcontext
import System.Drawing


class Objectile():
    
    def __init__(self, geo, r_max, h_max, s_max):
        
        #set user-input values
        self.base_geo = geo
        self.rotation_max = r_max
        self.height_max = h_max
        self.scale_max = s_max
        
        #set default values
        self.rotation_steps = 5
        self.height_steps = 5
        self.scale_steps = 5
        
        self.rotation_min = 10
        self.scale_min = 1
        
        self.X_spacing = 20
        self.Y_spacing = 20
        self.Z_spacing = 20
        
        self.objects = {}
    
    def Generate(self):
        for m in range (6):
            for i in range(0, self.rotation_steps + 1):
                for j in range(0, self.scale_steps + 1):
                    for k in range(1, self.height_steps):
                        self.objects[(m, i-1, j-1, k-1)] = OObject(self.base_geo, (((self.rotation_max - self.rotation_min)/self.rotation_steps)*i)+self.rotation_min, (((self.scale_max - self.scale_min)/self.scale_steps)*j)+self.scale_min, (self.height_max/self.height_steps)*k, self.height_max, m)
                        self.objects[(m, i-1, j-1, k-1)].Generate()
                        self.objects[(m, i-1, j-1, k- 1)].MakeTag(str((m, i-1, j-1, k-1)))
                        self.objects[(m, i-1, j-1, k-1)].Move(self.X_spacing * i + m * (self.X_spacing * self.rotation_steps + self.X_spacing * 2), self.Y_spacing * (j+1), self.Z_spacing * (k-1))
        
        for k, object in self.objects.iteritems():
            object.Bake(str((m, i, j, k)))


class OObject():
    
    def __init__(self, geo, r_step, s_step, h_step, h_max, type):
        self.geometry = geo.Duplicate()
        
        self.rotation = r_step
        self.scale = s_step
        self.height = h_step
        self.max_height = h_max
        
        self.type = type
        
        self.tag = None
        self.show_curves = True
        
    def Generate(self):
        #draw curve 1
        if self.type == 0 or self.type == 3 or self.type == 5:
            self.c1 = self.geometry.Duplicate()
            if self.scale > 0: self.c1.Scale(self.scale)
            if self.rotation > 0: self.c1.Rotate(Rhino.RhinoMath.ToRadians(self.rotation),Rhino.Geometry.Vector3d(0,0,1),Rhino.Geometry.Point3d(0,0,0))
        else:
            self.c1 = self.geometry

        #draw curve 2
        if self.type == 1 or self.type == 3 or self.type == 4:
            self.c2 = self.geometry.Duplicate()
            if self.scale > 0: self.c2.Scale(self.scale)
            if self.rotation > 0: self.c2.Rotate(Rhino.RhinoMath.ToRadians(self.rotation),Rhino.Geometry.Vector3d(0,0,1),Rhino.Geometry.Point3d(0,0,0))
            self.c2.Translate(0,0,self.height)
        else:
            self.c2 = self.geometry.Duplicate()
            self.c2.Translate(0,0,self.height)
        
        #draw curve 3
        if self.type == 2 or self.type == 4 or self.type == 5:
            self.c3 = self.geometry.Duplicate()
            if self.scale > 0: self.c3.Scale(self.scale)
            if self.rotation > 0: self.c3.Rotate(Rhino.RhinoMath.ToRadians(self.rotation),Rhino.Geometry.Vector3d(0,0,1),Rhino.Geometry.Point3d(0,0,0))
            self.c3.Translate(0,0,self.max_height)
        else:
            self.c3 = self.geometry.Duplicate()
            self.c3.Translate(0,0,self.max_height) 
            
        self.surf = Rhino.Geometry.Brep.CreateFromLoft([self.c1, self.c2, self.c3], Rhino.Geometry.Point3d.Unset, Rhino.Geometry.Point3d.Unset, Rhino.Geometry.LoftType.Straight, False)[0]
        self.surf.Flip()
    
    def MakeTag(self, label_text):
        self.tag = Rhino.Geometry.TextDot(label_text + "\nRotation: " + str(self.rotation) + "\nScale: " + str(self.scale) + "\nHeight: " + str(self.height), Rhino.Geometry.Point3d.Origin)
    
    def Move(self, x, y, z):
        if self.surf: 
            self.surf.Translate(x, y, z)
        
        if self.tag:
            self.tag.Translate(x, y, z)
        
        if self.show_curves:
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
        
        if self.show_curves:
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

if __name__=="__main__":
    test, base_geo = Rhino.Input.RhinoGet.GetOneObject("Select geo to generate objectile", False, None)
    if test == Rhino.Commands.Result.Success:
        my_objectile = Objectile(base_geo.Curve(), 45, 10, 2)
        my_objectile.Generate()
    else:
        print("Selection failed...") 