import Rhino
import scriptcontext


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
                        self.objects[(m, i, j, k)].MakeTag()
                        self.objects[(m, i,j,k)].Move(self.X_spacing * i + m * (self.X_spacing * self.rotation_steps + self.X_spacing * 2), self.Y_spacing * j, self.Z_spacing * k)
        
        for k, object in self.objects.iteritems():
            object.Bake()
       
        
class OObject():
    
    def __init__(self, geo, r_step, s_step, h_step, h_max, type):
        
        self.rotation = r_step
        self.scale = s_step
        self.height = h_step
        
        self.tag = None
        
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
        
    def MakeTag(self):
        self.tag = Rhino.Geometry.TextDot("Rotation: " + str(self.rotation) + "\nScale: " + str(self.scale) + "\nHeight: " + str(self.height), Rhino.Geometry.Point3d.Origin)
    
    def Move(self, x, y, z):
        if self.surf: self.surf.Translate(x, y, z)
        if self.tag: self.tag.Translate(x, y, z)
        
    def Bake(self):
        if self.surf: scriptcontext.doc.Objects.AddBrep(self.surf)
        if self.tag: scriptcontext.doc.Objects.AddTextDot(self.tag)
        
if __name__=="__main__":
    test, base_geo = Rhino.Input.RhinoGet.GetOneObject("Select geo to generate objectile", False, None)
    if test == Rhino.Commands.Result.Success:
        my_objectile = Objectile(base_geo.Curve(), 45, 10, 2)
        my_objectile.generate()
    else:
        print("Selection failed...") 