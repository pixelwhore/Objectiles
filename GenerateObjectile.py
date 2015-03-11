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
        self.X_spacing = 20
        self.Y_spacing = 20
        self.Z_spacing = 20
        
        self.objects = {}
       
    def generate(self):
        for m in range (3):
            for i in range(0, self.rotation_steps):
                for j in range(0, self.scale_steps):
                    for k in range(1, self.height_steps):
                        temp = self.base_geo.DuplicateCurve()
                        temp = OObject(temp, (self.rotation_max/self.rotation_steps)*i, (self.scale_max/self.scale_steps)*j, (self.height_max/self.height_steps)*k, self.height_max, m)
                        self.objects[(m, i,j,k)] = temp
                        self.objects[(m, i, j, k)].MakeTag(str((m, i, j, k)))
                        self.objects[(m, i, j, k)].Move(self.X_spacing * i + m * (self.X_spacing * self.rotation_steps + self.X_spacing * 2), self.Y_spacing * j, self.Z_spacing * k)
        
        for k, object in self.objects.iteritems():
            object.Bake(str((m, i, j, k)))
       
        
class OObject():
    
    def __init__(self, geo, r_step, s_step, h_step, h_max, type):
        
        self.rotation = r_step
        self.scale = s_step
        self.height = h_step
        
        self.tag = None
        self.show_curves = True
        
        #draw curve 1
        if type == 0:
            #generates loft curves where bottom curve scales/rotates
            self.c1 = geo.Duplicate()
            if self.scale > 0: self.c1.Scale(self.scale)
            if self.rotation > 0: self.c1.Rotate(Rhino.RhinoMath.ToRadians(self.rotation),Rhino.Geometry.Vector3d(0,0,1),Rhino.Geometry.Point3d(0,0,0))
        else:
            self.c1 = geo

        #draw curve 2
        if type == 1:
            self.c2 = geo.Duplicate()
            if self.scale > 0: self.c2.Scale(self.scale)
            if self.rotation > 0: self.c2.Rotate(Rhino.RhinoMath.ToRadians(self.rotation),Rhino.Geometry.Vector3d(0,0,1),Rhino.Geometry.Point3d(0,0,0))
            self.c2.Translate(0,0,self.height)
        else:
            self.c2 = geo.Duplicate()
            self.c2.Translate(0,0,self.height)
        
        #draw curve 3
        if type == 2:
            self.c3 = geo.Duplicate()
            if self.scale > 0: self.c3.Scale(self.scale)
            if self.rotation > 0: self.c3.Rotate(Rhino.RhinoMath.ToRadians(self.rotation),Rhino.Geometry.Vector3d(0,0,1),Rhino.Geometry.Point3d(0,0,0))
            self.c3.Translate(0,0,h_max)
        else:
            self.c3 = geo.Duplicate()
            self.c3.Translate(0,0,h_max)
            
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
            self.c1.Translate(x, y, z)
            self.c2.Translate(x, y, z)
            self.c3.Translate(x, y, z)
        
    def Bake(self, group_name):
        group = scriptcontext.doc.Groups.Add(group_name)
        
        if self.surf:
            layer = Rhino.DocObjects.Layer()
            layer.Name = "Surface"
            layer.Color = System.Drawing.Color.Goldenrod
            layer = scriptcontext.doc.Layers.Add(layer)
            
            attr = Rhino.DocObjects.ObjectAttributes()
            attr.AddToGroup(group)
            attr.LayerIndex = scriptcontext.doc.Layers.Find("Surface", True)
            
            srf_guid = scriptcontext.doc.Objects.AddBrep(self.surf, attr)
            #scriptcontext.doc.Groups.AddToGroup(group, srf_guid)
        if self.tag:
            layer = Rhino.DocObjects.Layer()
            layer.Name = "Tag"
            layer.Color = System.Drawing.Color.Gray 
            layer = scriptcontext.doc.Layers.Add(layer)
            
            attr = Rhino.DocObjects.ObjectAttributes()
            attr.AddToGroup(group)
            attr.LayerIndex = scriptcontext.doc.Layers.Find("Tag", True)
            
            tag_guid = scriptcontext.doc.Objects.AddTextDot(self.tag, attr)
            #scriptcontext.doc.Groups.AddToGroup(group, tag_guid)
        if self.show_curves:
            layer = Rhino.DocObjects.Layer()
            layer.Name = "Curves"
            layer.Color = System.Drawing.Color.Magenta 
            layer = scriptcontext.doc.Layers.Add(layer)
            
            attr = Rhino.DocObjects.ObjectAttributes()
            attr.AddToGroup(group)
            attr.LayerIndex = scriptcontext.doc.Layers.Find("Curves", True)
            
            c1_guid = scriptcontext.doc.Objects.AddCurve(self.c1, attr)
            c2_guid = scriptcontext.doc.Objects.AddCurve(self.c2, attr)
            c3_guid = scriptcontext.doc.Objects.AddCurve(self.c3, attr)
            #scriptcontext.doc.Groups.AddToGroup(group, (c1_guid, c2_guid, c3_guid))
        
if __name__=="__main__":
    test, base_geo = Rhino.Input.RhinoGet.GetOneObject("Select geo to generate objectile", False, None)
    if test == Rhino.Commands.Result.Success:
        my_objectile = Objectile(base_geo.Curve(), 45, 10, 2)
        my_objectile.generate()
    else:
        print("Selection failed...") 