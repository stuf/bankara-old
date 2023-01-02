import bpy

NODETREE_NAME = 'RG_Normal_Map'

INPUT_IMAGE = 'Color'
INPUT_STRENGTH = 'Strength'
OUTPUT_NORMAL = 'Normal'

node_groups = bpy.data.node_groups

if NODETREE_NAME in node_groups:
    node_groups.remove(node_groups[NODETREE_NAME])

g = bpy.data.node_groups.new('RG_Normal_Map', 'ShaderNodeTree')
nodes = g.nodes
links = g.links

input_node = nodes.new('NodeGroupInput')
output_node = nodes.new('NodeGroupOutput')

g.inputs.new('NodeSocketColor', INPUT_IMAGE)
g.inputs.new('NodeSocketFloat', INPUT_STRENGTH)
g.outputs.new('NodeSocketVector', OUTPUT_NORMAL)

sepRGB = nodes.new('ShaderNodeSeparateColor')
combRGB = nodes.new('ShaderNodeCombineColor')
normal_map = nodes.new('ShaderNodeNormalMap')

input_node.location = (-200, 0)
sepRGB.location = (0, 0)
combRGB.location = (200, 0)
combRGB.inputs[2].default_value = 1.0
normal_map.location = (400, 0)
output_node.location = (600, 0)

###
# Node group links
###

# Node group input
links.new(input_node.outputs[INPUT_IMAGE], sepRGB.inputs[0])
links.new(input_node.outputs[INPUT_STRENGTH], normal_map.inputs['Strength'])

# Node group output
links.new(normal_map.outputs['Normal'], output_node.inputs['Normal'])

#

links.new(sepRGB.outputs[0], combRGB.inputs[0])
links.new(sepRGB.outputs[1], combRGB.inputs[1])
links.new(combRGB.outputs[0], normal_map.inputs['Color'])
