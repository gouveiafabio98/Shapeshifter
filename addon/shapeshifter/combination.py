# ---- LIBRARIES ----

from shapeshifter import textures

import bpy
import math
import bmesh
import mathutils
import random
import numpy as np

# ---- FUNCTIONS ----
# Get the vertices that belong to the vertex group
def getVG(obj, vgname):
    vg = obj.vertex_groups.get(vgname)
    if vg is not None:
        return [v for v in obj.data.vertices if vg.index in [vg.group for vg in v.groups]]
    else:
        return None


# Calculate the centroid of the vertices
def vgCentroid(vertices):
    centroid = mathutils.Vector()
    for v in vertices:
        centroid += v.co
    centroid /= len(vertices)
    return centroid

def faceNormal(face, obj):
    normal = mathutils.Vector((0, 0, 0))
    
    N = obj.matrix_world.to_3x3().normalized()
    
    normal = N @ face.normal
    
    normal.normalize()

    return normal

def getFace(vertices, obj):
    for polygon in obj.data.polygons:
        if all(v in vertices for v in (obj.data.vertices[i] for i in polygon.vertices)):
            return polygon
    return None

def joinVG(self, obj1, tag1, obj2, tag2, blend, delFace, collapse):
    vg1 = getVG(obj1, tag1)
    vg2 = getVG(obj2, tag2)

    if len(vg1)==0 or len(vg2)==0:
        if len(vg1)==0:
            self.report({'ERROR'}, (f"Vertex Group {tag1} Not Found in Object {obj1.name}"))
        if len(vg2)==0:
            self.report({'ERROR'}, (f"Vertex Group {tag2} Not Found in Object {obj2.name}"))
        return

    # Get vertex group
    vg1 = reorder_vertex(vg1, obj1)
    vg2 = reorder_vertex(vg2, obj2)

    face1 = getFace(vg1, obj1)
    face2 = getFace(vg2, obj2)
    face1_index = face1.index
    face2_index = face2.index

    # Get vertex group face area
    avg1 = face1.area * obj1.matrix_world.to_scale()[0]
    avg2 = face2.area * obj2.matrix_world.to_scale()[0]

    # Calcualte the scale matrix and apply it to obj2
    scale = math.sqrt(avg1 / avg2)
    scale_matrix = mathutils.Matrix.Scale(scale, 4)
    obj2.matrix_world = scale_matrix @ obj2.matrix_world
    
    # Get vertex group normal
    nvg1 = faceNormal(face1, obj1)
    nvg2 = faceNormal(face2, obj2)

    # Calculate angle between normalsb
    angle, axis = vector_angle(nvg1, nvg2)
    
    # Calculate rotation matrix and apply it to obj2b
    rot_matrix = mathutils.Matrix.Rotation(math.pi - angle, 4, axis)

    obj2.matrix_world = rot_matrix @ obj2.matrix_world

    # Calculate and apply the obj2 position
    trans_separate = nvg1 * math.sqrt(math.sqrt(avg1))
    trans_matrix = mathutils.Matrix.Translation(to_global(vgCentroid(vg1), obj1) - to_global(vgCentroid(vg2), obj2) + trans_separate)
    
    obj2.matrix_world = trans_matrix @ obj2.matrix_world

    # Save texture data
    textures.meshData(obj1, "texture_" + tag1, 0.5, vg1, 1)
    textures.meshData(obj2, "texture_" + tag2, 0.5, vg2, 1)

    if is_clockwise(vg1, obj1):
        vg1.reverse()
    if is_clockwise(vg2, obj2):
        vg2.reverse()

    if len(vg1) > len(vg2):
        vg1, vg2 = vg2, vg1
        obj1, obj2 = obj2, obj1
        face1, face2 = face2, face1
        face1_index, face2_index = face2_index, face1_index
    
    # Collapse the faces
    if collapse:
        pairs = vertices_collapse(vg1, obj1, vg2, obj2)

        if blend:
            obj1, obj2 = textures.storeUV(obj1, face1, obj2, face2, tag1+tag2, pairs)

        if delFace:
            delete_face(face1_index, obj1)
            delete_face(face2_index, obj2)
    
    bpy.context.view_layer.update()

def delete_face(face, obj):
    # Make sure the object is active and in object mode
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='OBJECT')

    # Create a BMesh from the object's mesh data
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    # Ensure the lookup table is up-to-date
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    # Get the BMesh face corresponding to the input face
    bmesh_face = bm.faces[face]

    # Delete the face from the BMesh
    bmesh.ops.delete(bm, geom=[bmesh_face], context='FACES_ONLY')

    # Update the object's mesh data with the modified BMesh
    bm.to_mesh(obj.data)
    bm.free()

    # Notify Blender that the object's data has changed
    obj.data.update()

def index_distance(i1, i2, len):
    if i1>len or i2>len:
        return -1
    dist = 0
    pointer = i1
    while pointer != i2:
        pointer += 1
        if pointer == len:
            pointer = 0
        dist += 1
    return dist

def reorder_vertex(vg, obj):
    data = obj.data
    edges = data.edges
    vertices_reorder = []
    vertices_reorder.append(vg[0])
    vg.pop(0)

    while len(vg) > 1:
        found = False # NEW IMPROVEMENT
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

def vertices_collapse(s1, obj1, s2, obj2):
    s1_length = len(s1)
    s2_length = len(s2)

    collapsed_pairs = [] # Guardar pares juntos
    collapsed_pairs_index = []

    s2_options = {i: set(range(s1_length)) for i in range(s2_length)} # Criar uma lista com as possibilidades de s2
    s2_used = {i: 0 for i in range(s2_length)} # Stores the number of connections

    while len(s2_options) > 0: # Enquanto houver opções
        min_dist = float("inf")
        connections = float("inf")
        closest_pair = None
        
        # Procurar par do conjunto de opções mais próximo
        for v2 in s2_options.keys():
            for v1 in s2_options[v2]:
                dist = math.dist(to_global(s1[v1].co, obj1), to_global(s2[v2].co, obj2))
                if s2_used[v2]<connections or dist < min_dist:
                    min_dist = dist
                    connections = s2_used[v2]
                    closest_pair = [v2, v1]
        
        if closest_pair == None: return collapsed_pairs_index

        s2_used[closest_pair[0]] += 1 # Number of vertices connected increase

        collapsed_pairs.append(closest_pair) # Guardar o novo par mais próximo
        collapsed_pairs_index.append([s2[closest_pair[0]].index, s1[closest_pair[1]].index])

        s2[closest_pair[0]].co = to_local(to_global(s1[closest_pair[1]].co, obj1), obj2)

        del s2_options[closest_pair[0]] # Apagar da lista de opções do s1
        
        # Atualizar lista de opções
        for v2 in s2_options.copy().keys():
            back, front = None, None
            s2_back_dist, s2_front_dist = s2_length, s2_length

            for pair in collapsed_pairs:
                if s2_front_dist >= index_distance(v2, pair[0], s2_length):
                    s2_front_dist = index_distance(v2, pair[0], s2_length)
                    front = pair
                if s2_back_dist >= index_distance(pair[0], v2, s2_length):
                    s2_back_dist = index_distance(pair[0], v2, s2_length)
                    back = pair
            
            for v1 in s2_options[v2].copy():
                if v1 == front[1]:
                    s1_front_dist = s1_length-1
                else:
                    s1_front_dist = index_distance(v1, front[1], s1_length)
                s1_back_dist = index_distance(back[1], v1, s1_length)
                
                if s2_front_dist >= s1_front_dist and s2_back_dist >= s1_back_dist:
                    True
                else:
                    s2_options[v2].remove(v1)
    return collapsed_pairs_index

def to_local(vertex, obj):
    return obj.matrix_world.inverted() @ vertex

def to_global(vertex, obj):
    return obj.matrix_world @ vertex

def vector_angle(vector1, vector2):
    # Normalize the input vectors
    v1 = vector1 / np.linalg.norm(vector1)
    v2 = vector2 / np.linalg.norm(vector2)

    # Calculate the dot product between the normalized vectors
    dot_product = np.clip(np.dot(v1, v2), -1, 1)

    # Calculate the angle using acos
    angle_radians = np.arccos(dot_product)

    # Calculate the axis of rotation
    axis = np.cross(v1, v2)
    axis_normalized = axis / np.linalg.norm(axis)

    return angle_radians, axis_normalized