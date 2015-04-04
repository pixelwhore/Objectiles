import Rhino
import scriptcontext
import System.Drawing


class Objectile():
    def __init__(self, geo, s_max, r_max, h_max, height):
        
        self.base_geo = geo
        self.height = float(height)
        
        self.scale_max = float(s_max)
        self.rotation_max = float(r_max)
        self.height_max = float(h_max)
        
        self.scale_min = 1
        self.rotation_min = 15.25
        self.height_min = 0.0
        
        self.scale_stepcount = 4
        self.rotation_stepcount = 4
        self.height_stepcount = 4
        
        self.X_spacing = 500
        self.Y_spacing = 500
        self.Z_spacing = 500
        
        self.objects = {}
        self.export = False
    
    def Generate(self):
        #generate steps
        self.scale_stepval = (self.scale_max - self.scale_min)/float(self.scale_stepcount)
        self.rotation_stepval = (self.rotation_max - self.rotation_min)/float(self.rotation_stepcount)
        self.height_stepval = (self.height_max - self.height_min)/float(self.height_stepcount)
        
        #check shift heights before generating
        if self.height_min == 0.0:
            self.height_min = self.height_stepval
            self.height_stepcount = self.height_stepcount - 1
        if self.height_max == self.height:
            self.height_max = self.height - self.height_stepval
            self.height_stepcount = self.height_stepcount - 1
            
        #generate
        for f in range(6):
            for s in frange(self.scale_min, self.scale_stepval * (self.scale_stepcount + 1) + self.scale_min, self.scale_stepval):
                for r in frange(self.rotation_min, self.rotation_stepval * (self.rotation_stepcount + 1) + self.rotation_min, self.rotation_stepval):
                    for h in frange(self.height_min, self.height_stepval * (self.height_stepcount + 1) + self.height_min, self.height_stepval):
                        matrix_position = (f, int(round((s-self.scale_min)/self.scale_stepval)), int(round((r-self.rotation_min)/self.rotation_stepval)), int(round((h-self.height_min)/self.height_stepval)))
                        self.objects[matrix_position] = OObject(self.base_geo, s, r, h, self.height, f)
                        self.objects[matrix_position].Generate()
                        self.objects[matrix_position].MarkProperties(str(matrix_position))
                        self.objects[matrix_position].Move(self.X_spacing * matrix_position[1] + matrix_position[0] * (self.X_spacing * self.scale_stepcount + self.X_spacing * 2), self.Y_spacing * (matrix_position[2] + 1), self.Z_spacing * matrix_position[3])
        
    def Bake(self):
        for key, object in self.objects.iteritems():
            object.Bake(str(key))
    
    def ExportCSV(self, filename):
        if self.export:
            with open(filename + ".csv", 'w') as file:
                file.write("Matrix Family, Matrix X, Matrix Y, Matrix Z, Scale Value, Rotation Value, Height Value, Overall Height\n")
                for key, object in self.objects.iteritems():
                    file.write(str(key)[1:-1] + ", " + str(object.scale) + ", " + str(object.rotation) + ", " + str(object.height) + ", " + str(object.max_height) + "\n")


class OObject():
    
    def __init__(self, geo, s_val, r_val, h_val, h_max, type):
        self.geometry = geo.Duplicate()
        
        self.scale = s_val
        self.rotation = r_val
        self.height = h_val
        self.max_height = h_max
        
        self.type = type
        
        self.matrix_dot = None
        self.centroid_dot = None
        self.properties_dot = None
        self.shift_dot = None
        self.height_dot = None
        
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
    
    def MarkProperties(self, label_text):
        self.matrix_dot = Rhino.Geometry.TextDot(str(label_text)[1:-1], Rhino.Geometry.Point3d.Origin)
        self.centroid_dot = Rhino.Geometry.TextDot("Centroid", Rhino.Geometry.VolumeMassProperties.Compute(self.surf).Centroid)
        
        if self.type == 0 or self.type == 3 or self.type == 5:
            loc = self.c1.PointAtStart
        elif self.type == 1 or self.type == 3 or self.type == 4:
            loc = self.c2.PointAtStart
        elif self.type == 2 or self.type == 4 or self.type == 5:
            loc = self.c3.PointAtStart
        
        self.properties_dot = Rhino.Geometry.TextDot("Scale: " + str(self.scale) + "\nRotation: " + str(self.rotation), loc)
        self.shift_dot = Rhino.Geometry.TextDot("Shift: " + str(self.height), Rhino.Geometry.Point3d(0,0,self.height))
        self.height_dot = Rhino.Geometry.TextDot("Height: " + str(self.max_height), Rhino.Geometry.Point3d(0,0,self.max_height))
    
    def Move(self, x, y, z):
        if self.surf: 
            self.surf.Translate(x, y, z)
        
        if self.matrix_dot:
            self.matrix_dot.Translate(x, y, z)
            
        if self.centroid_dot:
            self.centroid_dot.Translate(x, y, z)
            
        if self.properties_dot:
            self.properties_dot.Translate(x, y, z)
        
        if self.shift_dot:
            self.shift_dot.Translate(x, y, z)
            
        if self.height_dot:
            self.height_dot.Translate(x, y, z)
        
        if self.c1 and self.c2 and self.c3:
            self.c1.Translate(x, y, z)
            self.c2.Translate(x, y, z)
            self.c3.Translate(x, y, z)
    
    def Bake(self, group_name):
        group = scriptcontext.doc.Groups.Add(group_name)
        
        if self.surf:
            attr = GenerateAttributes("Surface", System.Drawing.Color.Goldenrod, group)
            scriptcontext.doc.Objects.AddBrep(self.surf, attr)
            
        if self.centroid_dot:
            attr = GenerateAttributes("Centroid", System.Drawing.Color.Cyan, group)
            scriptcontext.doc.Objects.AddTextDot(self.centroid_dot, attr)
        
        if self.matrix_dot:
            attr = GenerateAttributes("Matrix ID", System.Drawing.Color.Gray, group)
            scriptcontext.doc.Objects.AddTextDot(self.matrix_dot, attr)
            
        if self.properties_dot:
            attr = GenerateAttributes("Properties", System.Drawing.Color.Chartreuse, group)
            scriptcontext.doc.Objects.AddTextDot(self.properties_dot, attr)
            
        if self.shift_dot:
            attr = GenerateAttributes("Shift", System.Drawing.Color.ForestGreen, group)
            scriptcontext.doc.Objects.AddTextDot(self.shift_dot, attr)
            
        if self.height_dot:
            attr = GenerateAttributes("Height", System.Drawing.Color.Plum, group)
            scriptcontext.doc.Objects.AddTextDot(self.height_dot, attr)
            
        if self.c1 and self.c2 and self.c3:
            attr = GenerateAttributes("Curves", System.Drawing.Color.Magenta, group)
            scriptcontext.doc.Objects.AddCurve(self.c1, attr)
            scriptcontext.doc.Objects.AddCurve(self.c2, attr)
            scriptcontext.doc.Objects.AddCurve(self.c3, attr)

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
    while start < stop:
        yield start
        start += step

if __name__ ==  "__main__":
    #make sure in proper units for robotics work
    if scriptcontext.doc.ModelUnitSystem != Rhino.UnitSystem.Millimeters:
        scriptcontext.doc.AdjustModelUnitSystem(Rhino.UnitSystem.Millimeters, True)

    #input geo & options
    get = Rhino.Input.Custom.GetObject()
    get.SetCommandPrompt("Select closed curve to generate objectile")
    
    export_bln = Rhino.Input.Custom.OptionToggle(False, "Off", "On")
    height_oal = Rhino.Input.Custom.OptionDouble(300.0, 150.0, 500.0)
    
    get.AddOptionDouble("Height", height_oal)
    get.AddOptionToggle("Export_CSV", export_bln)
    
    while True:
        result = get.Get()
        if result==Rhino.Input.GetResult.Option:
            continue
        break
    
    #shift options
    gh = Rhino.Input.Custom.GetOption()
    gh.SetCommandPrompt("Set shift options")
    
    shift_min = Rhino.Input.Custom.OptionDouble(0.0, 0.0, 250.0)
    shift_max = Rhino.Input.Custom.OptionDouble(125.0, 25.0, 250.0)
    shift_steps = Rhino.Input.Custom.OptionInteger(4, 2, 9)
    
    gh.AddOptionDouble("Shift_Min", shift_min)
    gh.AddOptionDouble("Shift_Max", shift_max)
    gh.AddOptionInteger("Shift_Steps", shift_steps)
    
    while True:
        result = gh.Get()
        if result==Rhino.Input.GetResult.Option:
            continue
        break
    
    #scale options
    gs = Rhino.Input.Custom.GetOption()
    gs.SetCommandPrompt("Set scale options")
    
    scale_min = Rhino.Input.Custom.OptionDouble(1.0, 1.0, 2.0)
    scale_max = Rhino.Input.Custom.OptionDouble(2.0, 2.0, 4.0)
    scale_steps = Rhino.Input.Custom.OptionInteger(4, 2, 9)
    
    gs.AddOptionDouble("Scale_Min", scale_min)
    gs.AddOptionDouble("Scale_Max", scale_max)
    gs.AddOptionInteger("Scale_Steps", scale_steps)
    
    while True:
        result = gs.Get()
        if result==Rhino.Input.GetResult.Option:
            continue
        break
    
    #rotation options
    gr = Rhino.Input.Custom.GetOption()
    gr.SetCommandPrompt("Set rotation options")
    
    rotation_min = Rhino.Input.Custom.OptionDouble(0.0, 0.0, 10.0)
    rotation_max = Rhino.Input.Custom.OptionDouble(45.0, 15.0, 90.0)
    rotation_steps = Rhino.Input.Custom.OptionInteger(4, 2, 9)
    
    gr.AddOptionDouble("Rotation_Min", rotation_min)
    gr.AddOptionDouble("Rotation_Max", rotation_max)
    gr.AddOptionInteger("Rotation_Steps", rotation_steps)
    
    while True:
        result = gr.Get()
        if result==Rhino.Input.GetResult.Option:
            continue
        break
    
    #do the work
    my_objectile = Objectile(get.Object(0).Curve(), scale_max.CurrentValue, rotation_max.CurrentValue, shift_max.CurrentValue, height_oal.CurrentValue)
    my_objectile.scale_min = scale_min.CurrentValue
    my_objectile.rotation_min = rotation_min.CurrentValue
    my_objectile.height_min = shift_min.CurrentValue
    my_objectile.scale_stepcount = scale_steps.CurrentValue - 1
    my_objectile.rotation_stepcount = rotation_steps.CurrentValue - 1
    my_objectile.height_stepcount = shift_steps.CurrentValue - 1
    my_objectile.export = export_bln.CurrentValue
    
    my_objectile.Generate()
    my_objectile.Bake()
    my_objectile.ExportCSV("test")