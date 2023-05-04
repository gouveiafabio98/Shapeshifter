# ---- LIBRARIES ----

import textures

import bpy
from random import randint
import math
import mathutils
from mathutils import Matrix, Vector
from mathutils.geometry import tessellate_polygon
from mathutils import Vector

# ---- FUNCTIONS ----
# Get the vertices that belong to the vertex group
def getVG(obj, vgname):
    vg = obj.vertex_groups.get(vgname)
    if vg is not None:
        vertices = [v for v in obj.data.vertices if vg.index in [vg.group for vg in v.groups]]
        return vertices
    else:
        return None

# Calculate the centroid of the vertices
def vgCentroid(vertices):
    centroid = Vector()
    for v in vertices:  
        centroid += v.co
    centroid /= len(vertices)
    return centroid

# Calculate the normal of the vertices
def vgNormal(vertices):
    normal = mathutils.Vector((0, 0, 0))
    for v in vertices:
        normal += v.normal
    normal.normalize()
    return normal

# Check the object faces who had all the vertices received
def getVGFaces(obj, vertices):
    polygons = obj.data.polygons
    area = 0
    for face in polygons:
        face_in_vertices = True
        for vert in face.vertices:
            if vert not in [v.index for v in vertices]:
                face_in_vertices = False
                break
        if face_in_vertices:
            area+=face.area
    return area

def joinVG(obj1, tag1, obj2, tag2):
    # Set obj2 matrix world equal to obj1
    obj2.matrix_world = obj1.matrix_world

    # Get vertex group
    vg1 = getVG(obj1, tag1)
    vg2 = getVG(obj2, tag2)

    # Get vertex group face area
    avg1 = getVGFaces(obj1, vg1)
    avg2 = getVGFaces(obj2, vg2)

    # Calcualte the scale matrix and apply it to obj2
    scale = math.sqrt(avg1/avg2)
    scale_matrix = mathutils.Matrix.Scale(scale, 4)
    obj2.matrix_world = scale_matrix @ obj2.matrix_world

    # Get vertex group normal
    nvg1 = obj1.matrix_world @ vgNormal(vg1)
    nvg2 = obj2.matrix_world @ vgNormal(vg2)

    # Calculate the cross value between normals
    axis = nvg1.cross(nvg2)

    # Calculate angle between normals
    angle = math.radians(180) - nvg1.angle(nvg2)

    # Calculate rotation matrix and apply it to obj2
    rot_matrix = mathutils.Matrix.Rotation(angle, 4, axis)
    obj2.matrix_world = rot_matrix @ obj2.matrix_world

    # Calculate and apply the obj2 position
    trans_matrix = Matrix.Translation(to_global(vgCentroid(vg1), obj1) - to_global(vgCentroid(vg2), obj2))
    obj2.matrix_world = trans_matrix @ obj2.matrix_world

    # Save texture data
    textures.meshData(obj1, "texture_"+tag1, 0.5, vg1, 1)
    textures.meshData(obj2, "texture_"+tag2, 0.5, vg2, 1)

    # Collapse the faces
    vertices_collapse(vg1, obj1, vg2, obj2)

    # Store the UV Map nearest oposite face inside it to use it later
    #textures.storeUV(obj1, vg1, obj2, vg2, tag1)

def index_distance(first, second, length):
    if first == second:
        return 0
    elif second > first:
        return second - first
    else:
        return length - first + second

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

def vertices_collapse(s1, obj1, s2, obj2):
    s1 = reorder_vertex(s1, obj1)
    s2 = reorder_vertex(s2, obj2)

    if len(s1) > len(s2):
        s1, s2 = s2, s1
        obj1, obj2 = obj2, obj1
        
    s1_length = len(s1)
    s2_length = len(s2)
    
    collapsed_pairs = []
    
    s2_options = {i: set(range(s1_length)) for i in range(s2_length)}
    
    while len(s2_options)>0:
        min_dist = float('inf')
        closest_pair = None
        
        for v2 in s2_options.keys():
            for v1 in s2_options[v2]:
                dist = math.dist(to_global(s1[v1].co, obj1), to_global(s2[v2].co, obj2))
                if dist < min_dist:
                    min_dist = dist
                    closest_pair = [v1, v2]
        
        # Add best combination
        collapsed_pairs.append(closest_pair)
        s2[closest_pair[1]].co = to_local(to_global(s1[closest_pair[0]].co, obj1), obj2)

        # Remove from the list of possible options
        del s2_options[closest_pair[1]]
        
        # Options adjustment
        for v2 in s2_options.copy().keys():

            before, after = None, None
            s2_before_dist, s2_after_dist = s2_length, s2_length

            for pair in collapsed_pairs:
                if s2_after_dist >= index_distance(v2, pair[1], s2_length):
                    s2_after_dist = index_distance(v2, pair[1], s2_length)
                    after = pair
                if s2_before_dist >= index_distance(pair[1], v2, s2_length):
                    s2_before_dist = index_distance(pair[1], v2, s2_length)
                    before = pair

            s2_total_dist = s2_after_dist + s2_before_dist
            
            for v1 in s2_options[v2].copy():
                
                s1_before_dist, s1_after_dist = s1_length, s1_length

                if index_distance(v1, before[0], s1_length) > index_distance(v1, after[0], s1_length):
                    s1_after_dist = index_distance(v1, after[0], s1_length)
                    s1_before_dist = index_distance(before[0], v1, s1_length)
                else:
                    s1_before_dist = index_distance(v1, before[0], s1_length)
                    s1_after_dist = index_distance(after[0], v1, s1_length)

                if v1 == after[0] and v1 == before[0]:
                    True
                else:
                    if v1 == after[0]:
                        s1_before_dist = index_distance(v1, before[0], s1_length)
                    if v1 == before[0]:
                        s1_after_dist = index_distance(after[0], v1, s1_length)

                s1_total_dist = s1_after_dist + s1_before_dist
                
                deviation = s2_total_dist - s1_total_dist
                    
                if s2_after_dist - s1_after_dist > deviation or s2_before_dist - s1_before_dist > deviation:
                    s2_options[v2].remove(v1)

def to_local(vertex, obj):
    return obj.matrix_world.inverted() @ vertex

def to_global(vertex, obj):
    return obj.matrix_world @ vertex