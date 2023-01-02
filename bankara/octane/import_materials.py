import bpy
import re
from typing import List, Dict
from os import listdir
from os.path import join, isfile

UNUSED_X = -600
UNUSED_Y = 0
NORMALMAP_NODE_GROUP = 'RG_Normal_Map'
NORMALMAP_STRENGTH = 0.3    # This needs to be fixed at some point

input = {
    'folder': r'X:\Assets\_Rip\_New\_Obj\RespawnPlatformLite',
    # 'folder': r'X:\Assets\_Rip\_New\_Fld\PlayerMake',
    # 'filename': 'Jyoheki03.fbx',  # Unused right now
    'image_format': 'png',
}

cleanup = {'images'
           }

defaults = {'mat_name_separator': '',
            'mat_name_prefix': '',
            }


def list_files(dir, fmt):
    return [f for f in listdir(dir) if isfile(join(dir, f)) and f.endswith(fmt)]


def collect_maps(dir, flist: List[str], fmt: str) -> Dict[str, Dict[str, str]]:
    pat = r'(\w+)_(\w{2,3})\.' + f'{fmt}$'
    mats: Dict[str, Dict[str, str]] = dict()

    for f in flist:
        print(f'-> {f}')
        ms = re.findall(pat, f)

        if len(ms) == 0:
            continue

        (base, kind) = ms[0]

        if not base in mats:
            mats[base] = dict()

        mdict = mats[base]
        mdict[kind] = f

    mats_res = dict()

    for (key, value) in mats.items():
        item = dict()

        for (mtype, filename) in value.items():
            cfg = None

            item[mtype] = {
                'maptype': mtype,
                'name': filename,
                'filepath': join(dir, filename),
            }

        mats_res[key] = item

    return mats_res


def _load_img(name, filepath):
    if name in bpy.data.images:
        bpy.data.images.remove(bpy.data.images[name])

    bpy.ops.image.open(filepath=filepath)

    return bpy.data.images[name]

#


def _make_img_tex(nodes, name, filepath, colorspace='sRGB'):
    """Create a generic Octane image node"""
    img_tex = nodes.new('OctaneRGBImage')
    img = _load_img(name, filepath)

    img_tex.image = img

    return img_tex

# Map handlers


def handle_alb(nodes, maptype=None, filepath=None, name=None):
    tex = _make_img_tex(nodes, name, filepath)
    tex.label = maptype
    tex.location = (-400, 600)
    tex.hide = True

    return [(tex.outputs['Texture out'], nodes['BSDF'].inputs['Base color'])]


def handle_ao(nodes, maptype=None, filepath=None, name=None):
    tex = _make_img_tex(nodes, name, filepath)
    tex.label = maptype
    tex.location = (UNUSED_X, UNUSED_Y)
    tex.hide = True

    return (None, None)


def handle_rgh(nodes, maptype=None, filepath=None, name=None):
    tex = _make_img_tex(nodes, name, filepath)
    tex.label = maptype
    tex.location = (-400, 400)
    tex.hide = True

    return [(tex.outputs['Texture out'], nodes['BSDF'].inputs['Specular roughness'])]


def handle_mtl(nodes, maptype=None, filepath=None, name=None):
    tex = _make_img_tex(nodes, name, filepath)
    tex.label = maptype
    tex.location = (-400, 500)
    tex.hide = True

    return (tex.outputs['Texture out'], nodes['BSDF'].inputs['Metalness'])


def handle_nrm(nodes, maptype=None, filepath=None, name=None):
    tex = _make_img_tex(nodes, name, filepath)
    tex.label = maptype
    tex.hide = True
    tex.location = (-400, 300)
    tex.inputs['Power'].default_value = 0.3

    return [(tex.outputs['Texture out'], nodes['BSDF'].inputs['Normal'])]


def handle_opa(nodes, maptype=None, filepath=None, name=None):
    tex = _make_img_tex(nodes, name, filepath)
    tex.label = maptype
    tex.hide = True
    tex.location = (-400, 200)

    return [(tex.outputs['Texture out'], nodes['BSDF'].inputs['Opacity'])]


def handle_emm(nodes, maptype=None, filepath=None, name=None):
    tex = _make_img_tex(nodes, name, filepath)
    tex.label = maptype
    tex.hide = True
    tex.location = (UNUSED_X, UNUSED_Y + 50)

    return [(None, None)]


def handle_emi(nodes, maptype=None, filepath=None, name=None):
    tex = _make_img_tex(nodes, name, filepath)
    tex.label = maptype
    tex.hide = True
    tex.location = (UNUSED_X, UNUSED_Y + 100)

    return [(None, None)]


def handle_tcl(nodes, maptype=None, filepath=None, name=None):
    tex = _make_img_tex(nodes, name, filepath)
    tex.label = maptype
    tex.hide = True
    tex.location = (UNUSED_X, UNUSED_Y + 200)

    return [(None, None)]

#


handlers = {
    'Alb': handle_alb,
    'Ao': handle_ao,
    'Rgh': handle_rgh,
    'Mtl': handle_mtl,
    'Nrm': handle_nrm,
    'Opa': handle_opa,
    'Emm': handle_emm,
    'Emi': handle_emi,
    'Tcl': handle_tcl,
}

#


def add_material(topname, maps):
    mprefix = '{}{}'.format(
        defaults['mat_name_prefix'], defaults['mat_name_separator'])

    mat_name = f'{mprefix}{topname}'  # -> "Prefix_MatName"

    if mat_name in bpy.data.materials:
        bpy.data.materials.remove(bpy.data.materials[mat_name])

    mat = bpy.data.materials.new(mat_name)
    mat.use_nodes = True

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    for node in nodes:
        nodes.remove(node)

    #

    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (540, 600)

    bsdf = nodes.new('OctaneStandardSurfaceMaterial')
    bsdf.name = 'BSDF'
    bsdf.location = (200, 600)

    links.new(bsdf.outputs[0], output.inputs['Surface'])

    for (mtype, mcfg) in maps.items():
        mfile = mcfg['filepath']
        mname = mcfg['name']

        if mtype in handlers:
            handler_func = handlers[mtype]

            res = handler_func(nodes,
                               maptype=mtype,
                               filepath=mfile,
                               name=mname)

            link_items = list()

            if type(res) is tuple:
                link_items.append(res)
            else:
                link_items = res

            for it in link_items:
                (a, b) = it

                if a is not None and b is not None:
                    links.new(a, b)


def add_materials(maps):
    for (k, v) in maps.items():
        add_material(k, v)

#


if __name__ == '__main__':
    fmt = input['image_format']
    files = list_files(input['folder'], fmt)
    maps = collect_maps(input['folder'], files, fmt)

    if 'images' in cleanup:
        image_keys = bpy.data.images.keys()

        for (mname, _) in maps.items():
            for k in image_keys:
                if mname in k:
                    bpy.data.images.remove(bpy.data.images[k])

    add_materials(maps)
