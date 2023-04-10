# ---- LIBRARIES ----

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

# Return object rotation matrix
def getObjRot(obj):
    return obj.rotation_euler.to_matrix().to_4x4()

# Check the object faces who had all the vertices send
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
    nvg1 = getObjRot(obj1) @ vgNormal(vg1)
    nvg2 = getObjRot(obj2) @ vgNormal(vg2)

    # Calculate the cross value between normals
    axis = nvg1.cross(nvg2)

    # Calculate angle between normals
    #if nvg1==nvg2:
        #angle = 0
    #else:
    angle = math.radians(180) - nvg1.angle(nvg2)

    # Calculate rotation matrix and apply it to obj2
    rot_matrix = mathutils.Matrix.Rotation(angle, 4, axis)
    obj2.matrix_world = rot_matrix @ obj2.matrix_world

    # Calculate and apply the obj2 position
    obj2.location = (obj1.matrix_world @ vgCentroid(vg1)) + obj2.location - (obj2.matrix_world @ vgCentroid(vg2))