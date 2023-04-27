import bpy
import bmesh

def meshData(obj, name, value, domain, default):
    mesh = obj.data

    # Create a new custom attribute on the mesh
    mesh.attributes.new(name=name, domain='POINT', type='FLOAT')

    # Set the attribute values based on the input
    attribute_values = []
    for vert in mesh.vertices:
        if vert in domain:
            attribute_values.append(value)
        else:
            attribute_values.append(default)

    mesh.attributes[name].data.foreach_set("value", attribute_values)

def newNodeGroup(material):
    name = "node_"+material.name
    
    # Get all nodes from material
    nodes = material.node_tree.nodes
    
    # Create new node group
    group = bpy.data.node_groups.new(name=name, type="ShaderNodeTree")

    # Copy nodes and links to group
    node_mapping = {}
    material_output_node = None
    for node in nodes:
        if node.type == "OUTPUT_MATERIAL":
            material_output_node = node
            continue
        if node.bl_idname.startswith('ShaderNode'):
            new_node = group.nodes.new(node.bl_idname)
            for prop in node.bl_rna.properties:
                if not prop.identifier.startswith(('rna_', 'bl_', 'type', 'dimensions', 'inputs', 'outputs', 'internal_links', 'select')):
                    try:
                        setattr(new_node, prop.identifier, getattr(node, prop.identifier))
                    except:
                        pass
            node_mapping[node] = new_node
        else:
            # Add built-in node as group input
            group_input = group.nodes.new("NodeGroupInput")
            group_input.name = node.name
            group_input.label = node.label
            group_input.location = node.location
            node_mapping[node] = group_input

    for node in nodes:
        if node == material_output_node:
            continue
        new_node = node_mapping[node]
        for i, inp in enumerate(node.inputs):
            for link in inp.links:
                connected_node = node_mapping[link.from_node]
                group.links.new(connected_node.outputs[link.from_socket.name], new_node.inputs[i])

    # Add group output node
    group_input = group.nodes.new("NodeGroupInput")
    group_output = group.outputs.new("NodeSocketShader", "Shader")
    output_node = group.nodes.new("NodeGroupOutput")
    
    for i, inp in enumerate(material_output_node.inputs):
        for link in inp.links:
            connected_node = node_mapping[link.from_node]
            group.links.new(connected_node.outputs[link.from_socket.name], output_node.inputs[0])

    # Position group input and output nodes
    if len(group.nodes) > 0:
        min_pos = min(node.location[0] for node in group.nodes if node.type != "NodeGroupOutput")
        max_pos = max(node.location[0] + node.width for node in group.nodes if node.type != "NodeGroupOutput")
        group_input.location = (min_pos - 250, 0)
        output_node.location = (max_pos + 250, 0)

    return group

def getMaterial(obj):
    if obj.material_slots:
        material = obj.material_slots[0].material
    else:
        material = None
    return material

def createMaterial(nodes, name):
    newMaterial = bpy.data.materials.new(name)
    newMaterial.use_nodes = True
    nodeTree = newMaterial.node_tree
    nodeTree.nodes.clear()
    for name, node in nodes.items(): 
        group_node = nodeTree.nodes.new("ShaderNodeGroup")
        group_node.node_tree = node
        #group_node1.location = (-100, 0)
    
    return newMaterial

def storeUV():
    # TO DO
    return None