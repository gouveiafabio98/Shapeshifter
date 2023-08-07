import bpy
import bmesh

def selected_verts(obj):
    bpy.ops.object.mode_set(mode='OBJECT')
    selectedVerts = [v for v in obj.data.vertices if v.select]
    return selectedVerts

def is_clockwise(vertices):
    cross_product_sum = 0
    for i in range(len(vertices)):
        current_vertex = [vertices[i].co.x, vertices[i].co.y, vertices[i].co.z]
        next_vertex = [
            vertices[(i + 1) % len(vertices)].co.x,
            vertices[(i + 1) % len(vertices)].co.y,
            vertices[(i + 1) % len(vertices)].co.z,
        ]
        cross_product_sum += (next_vertex[0] - current_vertex[0]) * (
            next_vertex[1] + current_vertex[1]
        )
    return cross_product_sum > 0

def reorder_vertex(vg, obj):
    data = obj.data
    edges = data.edges
    vertices_reorder = []
    vertices_reorder.append(vg[0])
    vg.pop(0)
    while len(vg) > 1:
        for edge in edges:
            if vertices_reorder[-1] == data.vertices[edge.vertices[0]] and data.vertices[edge.vertices[1]] in vg:
                vertices_reorder.append(data.vertices[edge.vertices[1]])
                vg.remove(data.vertices[edge.vertices[1]])
                break
            elif vertices_reorder[-1] == data.vertices[edge.vertices[1]] and data.vertices[edge.vertices[0]] in vg:
                vertices_reorder.append(data.vertices[edge.vertices[0]])
                vg.remove(data.vertices[edge.vertices[0]])
                break
    vertices_reorder.append(vg[0])
    vg.pop(0)
    return vertices_reorder

def check_loop(selected, obj):
    return any(edge for edge in obj.data.edges if (selected[0].index in edge.vertices) and (selected[-1].index in edge.vertices))

def loop_cut():
    mode = bpy.context.active_object.mode
    obj = bpy.context.object

    selected = set_loop(selected_verts(obj), obj)

    if check_loop(selected, obj):
        new_selected = next_loop(selected, obj)
    
    bpy.ops.object.mode_set(mode=mode)

def set_loop(select_verts, obj):
    selected = reorder_vertex(select_verts, obj)

    if not is_clockwise(selected):
        selected.reverse()
    return selected

def next_loop(loop, obj):
    mesh = obj.data
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(mesh)
    faces = []

    for face in mesh.polygons:
        i_face = face.vertices
        for i_range in range(len(loop)):
            p1=i_range
            if p1==len(loop)-1:
                p2=0
            else:
                p2=p1+1
            if loop[p1].index in i_face and loop[p2].index in i_face:
                i_face = reorder_vertex(i_face, obj)
                print(i_face.index)
    
    return faces

loop_cut()