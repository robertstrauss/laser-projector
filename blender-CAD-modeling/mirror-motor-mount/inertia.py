import bpy
import bmesh
import mathutils
import numpy as np

def compute_inertia_tensor(obj, density=1.0):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bm.verts.ensure_lookup_table()

    # Inertia tensor components
    Ixx = Iyy = Izz = Ixy = Ixz = Iyz = 0.0
    total_mass = 0.0

    origin = mathutils.Vector((0, 0, 0))
    
    
    basis = obj.matrix_world.to_3x3()
    

    for face in bm.faces:
        v0, v1, v2 = [basis @ (v.co - origin) for v in face.verts]
        
        centroid = (v0 + v1 + v2) / 3
        vol = v0.dot(v1.cross(v2)) / 6.0 # triangle pytramid volume by triple product
        if vol == 0.0:
            continue
#        if vol < 0:
#            print("<0!!!")

        mass = density * vol
        total_mass += mass

        # Tetrahedron vertices (object origin and triangle vertices)

        for i in range(3):
            p = [v0, v1, v2][i]
            x, y, z = p
            Ixx += mass * (y * y + z * z)
            Iyy += mass * (x * x + z * z)
            Izz += mass * (x * x + y * y)
            Ixy -= mass * x * y
            Ixz -= mass * x * z
            
            Iyz -= mass * y * z

    bm.free()
    
    
    inertia_tensor = mathutils.Matrix((
        (Ixx, Ixy, Ixz),
        (Ixy, Iyy, Iyz),
        (Ixz, Iyz, Izz)
    ))

    return inertia_tensor, total_mass




def combined_inertia_tensor(objects, densities):
    I_tot = mathutils.Matrix.Diagonal((0,0,0))
    masses = []
    rs = []
    
    for i, object in enumerate(objects):
        try:
            object.name
        except ReferenceError as e:
            print('invalid object in list, skipping')
            continue
        I, M = compute_inertia_tensor(object, density=densities[i])
        I_tot += I
        # save the mass and location to later compute combined COM, and parallel axis tensor contributions
        masses.append(M)
        rs.append(object.matrix_world.translation) # don't just use .location, could be parented.
    
    COM = np.sum(np.array(masses)[:,None]*np.array(rs), axis=0) / np.sum(np.array(masses))
    COM = mathutils.Vector(COM)
    
    for i in range(len(rs)):
        r = rs[i] - COM
        rxr = mathutils.Matrix([r[0]*r, r[1]*r, r[2]*r]) # matrix form of self outer product of r (projection onto r)
        I_tot += masses[i] * (r.length_squared * mathutils.Matrix.Identity(3) - rxr)
        
    return I_tot, COM


def visualize_tensor(inertia_tensor, location=(0, 0, 0), scale=1.0):
    # Create a new UV sphere
#    bpy.ops.mesh.primitive_uv_sphere_add(radius=scale, location=location)
#    sphere = bpy.context.active_object
#    mesh = sphere.data
#
#    # Apply the inertia tensor matrix to each vertex
#    for vert in mesh.vertices:
#        local = vert.co
#        transformed = inertia_tensor @ local
#        vert.co = transformed
#
#    sphere.name = "DistortedInertiaSphere"
#    return sphere

    axes_object = bpy.data.objects.new(name="Inertia-PrincipalAxes", object_data=None)
    axes_object.empty_display_type = 'ARROWS'
    
#    collection = bpy.data.collections.new("Inertia_Principal_Axes")
#    bpy.context.scene.collection.children.link(collection)
#    collection.objects.link(axes_object)
    bpy.context.scene.collection.objects.link(axes_object)
    
    set_transform(axes_object, inertia_tensor, location, scale)
    
    
    return axes_object
    
    
    
def set_transform(obj, tensor, location, scale):
    euler_mode = 'XYZ'
    
    i_t = np.array(tensor)
    evals, evecs = np.linalg.eig(i_t)
    R = mathutils.Matrix(evecs).to_euler(euler_mode)
#    _, quat, princ_moments = inertia_tensor.to_4x4().decompose()
#    obj.transform(inertia_tensor)
    obj.scale = mathutils.Vector(evals) * scale
    obj.rotation_mode = euler_mode
    obj.rotation_euler = R
    obj.location = location
    
#    bpy.context.view_layer.update()