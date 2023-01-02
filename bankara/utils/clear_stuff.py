import bpy

cleanup = {'materials', 'images'}

if 'materials' in cleanup:
    [bpy.data.materials.remove(it) for it in bpy.data.materials]

if 'images' in cleanup:
    [bpy.data.images.remove(it) for it in bpy.data.images]
