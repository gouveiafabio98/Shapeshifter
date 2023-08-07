import bpy
import bmesh

def reorder_vertex(vg, obj):
    data = obj.data
    edges = data.edges
    vertices_reorder = []
    vertices_reorder.append(vg[0])
    vg.pop(0)

    while len(vg) > 1:
        found = False
        for edge in edges:
            if vertices_reorder[-1] == data.vertices[edge.vertices[0]] and data.vertices[edge.vertices[1]] in vg:
                vertices_reorder.append(data.vertices[edge.vertices[1]])
                vg.remove(data.vertices[edge.vertices[1]])
                found = True
                break
            elif vertices_reorder[-1] == data.vertices[edge.vertices[1]] and data.vertices[edge.vertices[0]] in vg:
                vertices_reorder.append(data.vertices[edge.vertices[0]])
                vg.remove(data.vertices[edge.vertices[0]])
                found = True
                break
        if not found:
            break
        
    vertices_reorder.append(vg[0])
    vg.pop(0)
    return vertices_reorder

def is_clockwise(vertices, obj):
    cross_product_sum = 0
    for i in range(len(vertices)):
        current_vertex = to_global(vertices[i].co, obj)
        next_vertex = to_global(vertices[(i + 1) % len(vertices)].co, obj)

        cross_product_sum += (next_vertex.x - current_vertex.x) * (next_vertex.y + current_vertex.y) * (next_vertex.z + current_vertex.z)

    return cross_product_sum > 0

def to_global(vertex, obj):
    return obj.matrix_world @ vertex



def select_first_loop(selection, remaining_faces, exclusion = []):
    loop_check = True
    updated = False
    
    while loop_check:
        loop_check = False
        for loop_face in remaining_faces.copy():
            if loop_face["face"].index not in [exclusion_face["face"].index for exclusion_face in exclusion]: # Verificar excluídos
                shared_edge = [edge for edge in loop_face["edges"] if edge.index in [select_edge.index for select_edge in selection[-1]["edges"]]]
                if shared_edge:
                    selection.append(loop_face)
                    remaining_faces.pop(remaining_faces.index(loop_face))
                    loop_check = True
                    updated = True
                    break
    
    return selection, remaining_faces, updated

def select_loop(selection, remaining_faces, exclusion = []):
    updated = False
    selection_copy = selection.copy()

    
    for loop_face in remaining_faces.copy():
        if loop_face["face"].index not in [exclusion_face["face"].index for exclusion_face in exclusion]: # Verificar excluídos
            for select in selection_copy:
                shared_edge = [edge for edge in loop_face["edges"] if edge.index in [select_edge.index for select_edge in select["edges"]]]
                if shared_edge:
                    selection.append(loop_face) # Adiciono nova face que partilha edge com o selection copy
                    remaining_faces.pop(remaining_faces.index(loop_face)) # Removo a nova face da lista de faces a verificar
                    updated = True
                    break

    return selection, remaining_faces, updated

def separate_object(bm, selection_one):
    # Ensure the lookup table is up-to-date
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    # Enter edit mode to modify the mesh
    bpy.ops.object.mode_set(mode='EDIT')

    # Deselect all faces
    for face in bm.faces:
        face.select = False

    # Select the faces from selection_one
    for face_info in selection_one:
        bm.faces[face_info["face"].index].select = True

    # Separate the selected faces into the new object for selection_one
    bpy.ops.mesh.separate(type='SELECTED')

    # Deselect all faces again
    for face in bm.faces:
        face.select = False

    # Return to object mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # Return new objects
    return bpy.context.selected_objects

def create_vertex_group(obj, vertices, group_name):
    bpy.ops.object.mode_set(mode='OBJECT')
    # Create a new vertex group
    vertex_group = obj.vertex_groups.new(name=group_name)

    # Add the vertices to the vertex group
    vertex_group.add(vertices, 1.0, 'ADD')

    return vertex_group.name

def create_face_using_vertex_group(obj, group_name):
    bpy.ops.object.mode_set(mode='EDIT')
    
    # Get the vertex group
    vertex_group = obj.vertex_groups.get(group_name)

    if vertex_group:
        # Get the vertex indices from the vertex group
        vert_indices = [v.index for v in obj.data.vertices if vertex_group.index in [g.group for g in v.groups]]

        # Check if there are enough vertices to create a face
        if len(vert_indices) >= 3:
            # Get the BMesh
            bm = bmesh.from_edit_mesh(obj.data)
            
            # Ensure the lookup table is up-to-date
            bm.verts.ensure_lookup_table()
            bm.edges.ensure_lookup_table()
            bm.faces.ensure_lookup_table()

            # Select the vertices from the vertex group
            bpy.ops.mesh.select_all(action='DESELECT')
            for v_index in vert_indices:
                bm.verts[v_index].select = True

            # Create the face using the selected edges
            bpy.ops.mesh.edge_face_add()

            # Update the BMesh and object data
            bmesh.update_edit_mesh(obj.data)

def select_faces_in_loop():
    current_mode = bpy.context.object.mode # Save the current mode

    bpy.ops.object.mode_set(mode='OBJECT') # Set to OBJ mode to get selected edges

    # Get obj data
    obj = bpy.context.object
    mesh = obj.data

    # Selected Vertices
    selected_verts = [v for v in mesh.vertices if v.select]
    if not selected_verts or len(selected_verts) <= 2:
        bpy.ops.object.mode_set(mode=current_mode)
        return "No Vertices Selected"
    selected_verts = reorder_vertex(selected_verts, obj)
    # Vertices Index List
    selected_verts_index = [v.index for v in selected_verts]

    # Selected Edges
    selected_edges = []
    for v in range(len(selected_verts_index)):
        next_index = (v + 1) % len(selected_verts_index)  # Use modulo to wrap around to the first vertex for the last vertex
        for edge in mesh.edges:
            if selected_verts_index[v] in edge.vertices and selected_verts_index[next_index] in edge.vertices:
                selected_edges.append({"edge": edge, "index": edge.index, "fv": v, "sv": next_index})

    # Check Loop
    loop_exists = any(edge for edge in selected_edges if (selected_verts[0].index in edge["edge"].vertices) and (selected_verts[-1].index in edge["edge"].vertices))
    
    selection = []
    remaining_faces = []

    selection_one = []
    if loop_exists:
        # Create Vertice Group
        vg_name = create_vertex_group(obj, selected_verts_index, "new_vg")

        # Get mesh data to EDIT
        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(mesh)
        for face in bm.faces:
            selected_edges_in_face = [edge for edge in face.edges if edge.index in [e["index"] for e in selected_edges]]
            if selected_edges_in_face:
                selection.append({"face": face,
                                  "edges": [edge for edge in face.edges if edge.index not in [e["index"] for e in selected_edges]]})
            else:
                remaining_faces.append({"face": face,
                                        "edges": face.edges})

        selection_two = selection
        # Select random first face in loop
        selection_one.append(selection_two[0])
        selection_two.pop(0)
        # Select first face loop
        selection_one, selection_two, updated = select_first_loop(selection_one, selection_two)
        
        # Select next loops
        while updated:
            selection_one, remaining_faces, updated = select_loop(selection_one, remaining_faces, selection_two)

        # Separate in two different objects by selection_one and selection_two
        objects = separate_object(bm, selection_one)
        
        for object in objects:
            create_face_using_vertex_group(object, vg_name)

        return "SUCCESS"
    else:
        return "No Loop"


print(select_faces_in_loop())