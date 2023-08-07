import bpy
import bmesh
from mathutils import Vector

import combination

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
    group.outputs.new("NodeSocketShader", "Shader")
    output_node = group.nodes.new("NodeGroupOutput")
    group.inputs.new("NodeSocketVector", "UV")
    
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
        uv_name = nodes[i]["uv"]
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
        uv_map_node.uv_map = uv_name
        uv_map_node.location = (group_node.location.x-200, group_node.location.y+150)
        
    return newMaterial

def adjacent_faces(obj, main_face):
    faces = obj.data.polygons
    main_vertices = main_face.vertices
    adjacent_faces = []

    for face in faces:
        if face != main_face and any(vertex_index in main_vertices for vertex_index in face.vertices):
            adjacent_faces.append(face)

    return adjacent_faces

def associate_faces(faces1, faces2, pairs):
    faces_pairs = []

    # Associate faces from faces2 with faces from faces1
    for face2 in faces2:
        face_pairs = [pair for pair in pairs if pair[0] in face2.vertices]
        remaining_v2 = [v for v in face2.vertices if not any(v == v2 for v2, _ in face_pairs)]

        faces_pairs.append({
            'f1': None,
            'f2': face2,
            'pairs': face_pairs,
            'remaining_v1': [],
            'remaining_v2': remaining_v2
        })

    # Associate faces from faces1 with faces from faces2
    new_faces_pairs = []
    for face_pair in faces_pairs:
        best_f1 = None
        best_remaining_v1 = []
        best_n = -1
        for face1 in faces1:
            if all(vert in face1.vertices for _, vert in face_pair["pairs"]) and len(face_pair["pairs"])>best_n:
                best_f1 = face1
                best_remaining_v1 = [v for v in face1.vertices if not any(v == v1 for _, v1 in face_pair["pairs"])]
                best_n = len(face_pair["pairs"])
        if best_f1 is not None:
            face_pair["f1"] = best_f1
            face_pair["remaining_v1"] = best_remaining_v1
            new_faces_pairs.append(face_pair)

    faces_pairs = [face_pair for face_pair in new_faces_pairs if face_pair["f1"] is not None]

    return faces_pairs

def associate_vertices(association, obj1, obj2):
    for assoc in association:
        list_v1 = assoc["remaining_v1"]
        list_v2 = assoc["remaining_v2"]
        greater = 0
        if len(list_v1) > len(list_v2):
            greater = 1
        elif len(list_v1) < len(list_v2):
            greater = -1

        best = closest_vertex(list_v1, obj1, list_v2, obj2)
        while best != None:
            if greater == 1 or greater == 0:
                list_v1.remove(best['v1'])
            if greater == -1 or greater == 0:
                list_v2.remove(best['v2'])
            assoc["pairs"].append([best['v2'], best['v1']])
            best = closest_vertex(list_v1, obj1, list_v2, obj2)

    return association

def closest_vertex(list_v1, obj1, list_v2, obj2):
    best = None
    best_dist = float("inf")
    for v1 in list_v1:
        for v2 in list_v2:
            v1g = combination.to_global(obj1.data.vertices[v1].co, obj1)
            v2g = combination.to_global(obj2.data.vertices[v2].co, obj2)
            dist = (v1g - v2g).length
            if dist < best_dist:
                best_dist = dist
                best = {'v1': v1, 'v2': v2}
    return best

def storeUV(obj1, face1, obj2, face2, tag, pairs):
    obj1.data.update()
    obj2.data.update()
    # face1 and face2 are the vgFaces
    # The pairs are the already joined vertices

    print(obj1.name, obj2.name)

    # Get the surrounding faces
    sf1 = adjacent_faces(obj1, face1)
    sf2 = adjacent_faces(obj2, face2)

    # Associate each face to another
    association = associate_faces(sf1, sf2, pairs)

    association = associate_vertices(association, obj1, obj2)

    active_uv1 = obj1.data.uv_layers.active
    active_uv2 = obj2.data.uv_layers.active

    new_uv1 = obj1.data.uv_layers.new(name=tag)
    new_uv2 = obj2.data.uv_layers.new(name=tag)
    
    for assoc in association:
        for f1_loop in assoc['f1'].loop_indices:
            l1 = obj1.data.loops[f1_loop]
            i1 = l1.vertex_index
            for f2_loop in assoc['f2'].loop_indices:
                l2 = obj2.data.loops[f2_loop]
                i2 = l2.vertex_index
                if [i2, i1] in assoc['pairs']:
                    new_uv1.data[l1.index].uv = active_uv2.data[l2.index].uv.copy()
                    new_uv2.data[l2.index].uv = active_uv1.data[l1.index].uv.copy()
    
    obj1.data.update()
    obj2.data.update()
import time