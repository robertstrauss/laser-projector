#objs = bpy.context.selected_objects

#densities = []
#for obj in objs:
#    if 'inertia-density' in bpy.data.objects[obj.name]:
#        densities.append(bpy.data.objects[obj.name]['inertia-density'])
#    else:
#        densities.append(1)
#    print(obj, densities[-1])
#    

#inertia = bpy.data.texts[0].as_module()

#I_tot, COM = inertia.combined_inertia_tensor(objs, densities)
#axes_viz = inertia.visualize_tensor(I_tot, location=COM, scale=1e-6)

import bpy
import mathutils

class activeInertiaViz():
    def __init__(self):
        objs = bpy.context.selected_objects

        densities = []
        for obj in objs:
            if 'inertia-density' in bpy.data.objects[obj.name]:
                densities.append(bpy.data.objects[obj.name]['inertia-density'])
            else:
                densities.append(1)
            print(obj, densities[-1])
            

        inertia = bpy.data.texts[0].as_module()

        I_tot, COM = inertia.combined_inertia_tensor(objs, densities)
        axes_viz = inertia.visualize_tensor(I_tot, location=COM, scale=1e-6)
        
        self.inertia = inertia
        self.objs = objs
        self.densities = densities
        self.axes_viz = axes_viz
        
    def update(self):
        I_tot, COM = self.inertia.combined_inertia_tensor(self.objs, self.densities)
        self.inertia.set_transform(self.axes_viz, I_tot, COM, scale=1e-6)
        print('new COM', COM)
        print('upd', self.axes_viz.rotation_euler)
    

inertiaviz = activeInertiaViz()

bpy.app.driver_namespace['inertiaviz'] = inertiaviz

#bpy.app.handlers.frame_change_post.append(inertiaviz.update)

#bpy.app.handlers.frame_change_post.remove(update_av)

#for obj in bpy.context.selected_objects:
#    I, M = inertia.compute_inertia_tensor(obj)
#    axes_viz = inertia.visualize_tensor(I, location=obj.location, scale=1e-3)

