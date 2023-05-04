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

def newNodeGroup(material, name):
    name = "node_"+name+"_"+material.name
    
    # Get all nodes from material
    nodes = material.node_tree.nodes
    
    # Create new node group
    group = bpy.data.node_groups.new(name=name, type="ShaderNodeTree")

    # Copy nodes and links to group
    node_mapping = {}
    material_output_node = None
    image_nodes = []
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
            if node.bl_idname == 'ShaderNodeTexImage':
                image_nodes.append(new_node)
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
    group_output = group.inputs.new("NodeSocketVector", "UV")
    
    for i, inp in enumerate(material_output_node.inputs):
        for link in inp.links:
            connected_node = node_mapping[link.from_node]
            group.links.new(connected_node.outputs[link.from_socket.name], output_node.inputs[0])
    
    for node in image_nodes:
        group.links.new(group_input.outputs[0], node.inputs["Vector"])


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
    
    output_node = nodeTree.nodes.new("ShaderNodeOutputMaterial")
    output_node.location = (200, 200)

    nodes.reverse()

    lastMixNode = None
    for i in range(len(nodes)):
        node = nodes[i]["node"]
        name = nodes[i]["name"]
        group_node = nodeTree.nodes.new("ShaderNodeGroup")
        group_node.node_tree = node

        if i != len(nodes) - 1:
            mix_shader_node = nodeTree.nodes.new("ShaderNodeMixShader")
            mix_shader_node.location = (i * -200, i * -200)

            attr_node = nodeTree.nodes.new("ShaderNodeAttribute")
            attr_node.attribute_name = "texture_"+name
            attr_node.location = (mix_shader_node.location.x-200, mix_shader_node.location.y+200)
            
            nodeTree.links.new(attr_node.outputs["Fac"], mix_shader_node.inputs[0])
            
            if lastMixNode == None:
                nodeTree.links.new(mix_shader_node.outputs["Shader"], output_node.inputs["Surface"])
            else:
                nodeTree.links.new(mix_shader_node.outputs["Shader"], lastMixNode.inputs[2])
            
            nodeTree.links.new(group_node.outputs["Shader"], mix_shader_node.inputs[1])
            lastMixNode = mix_shader_node
            group_node.location = (lastMixNode.location.x-200, lastMixNode.location.y)
        else:
            nodeTree.links.new(group_node.outputs["Shader"], mix_shader_node.inputs[2])
            group_node.location = (lastMixNode.location.x-200, lastMixNode.location.y-200)
        
        uv_map_node = nodeTree.nodes.new(type="ShaderNodeUVMap")
        nodeTree.links.new(uv_map_node.outputs[0], group_node.inputs[0])
        uv_map_node.location = (group_node.location.x-200, group_node.location.y+150)

    return newMaterial

def storeUV(obj1, vg1, obj2, vg2, tag):
    obj1.data.uv_layers.new(name=tag)

    uv2 = obj2.data.uv_layers.active.data

    for i, uv_data in enumerate(obj1.data.uv_layers[1].data):
        uv_data.uv = uv2[i].uv
    return None