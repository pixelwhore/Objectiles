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
        self.X_spacing = 10
        self.Y_spacing = 10
        self.Z_spacing = 20
        
        #todo this should be a dictionary w/ a tuple as the key for the OObject value
        self.objects = []
       
    def generate(self):
        for i in range(1, self.rotation_steps):
            for j in range(1, self.scale_steps):
                for k in range(1, self.height_steps-1):
                    temp = self.base_geo.DuplicateCurve()
                    temp = OObject(temp, (self.rotation_max/self.rotation_steps)*i, (self.scale_max/self.scale_steps)*j, (self.height_max/self.height_steps)*k, self.height_max)
                    self.objects.append(temp)
                    self.objects[-1].Move(self.X_spacing * i, self.Y_spacing * j, self.Z_spacing * k)
        
        for object in self.objects:
            object.Bake()
       
        
class OObject():
    
    def __init__(self, geo, r_step, s_step, h_step, h_max):
        self.c1 = geo
        
        self.c2 = geo.Duplicate()
        self.c2.Scale(s_step)
        self.c2.Translate(0,0,h_step)
        self.c2.Rotate(Rhino.RhinoMath.ToRadians(r_step),Rhino.Geometry.Vector3d(0,0,1),Rhino.Geometry.Point3d(0,0,0))
 
        
        self.c3 = geo.Duplicate()
        self.c3.Translate(0,0,h_max)
        
        self.surf = Rhino.Geometry.Brep.CreateFromLoft([self.c1, self.c2, self.c3], Rhino.Geometry.Point3d.Unset, Rhino.Geometry.Point3d.Unset, Rhino.Geometry.LoftType.Straight, False)[0]
        self.surf.Flip()
        
    def Move(self, x, y, z):
        self.surf.Translate(x, y, z)
        
    def Bake(self):
        scriptcontext.doc.Objects.AddBrep(self.surf)
        
if __name__=="__main__":
    test, base_geo = Rhino.Input.RhinoGet.GetOneObject("Select geo to generate objectile", False, None)
    if test == Rhino.Commands.Result.Success:
        my_objectile = Objectile(base_geo.Curve(), 45, 10, 2)
        my_objectile.generate()
    else:
        print("Selection failed...") 