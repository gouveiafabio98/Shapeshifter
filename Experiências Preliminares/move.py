import bpy
from mathutils import Vector, Matrix

obj1 = bpy.data.objects.get("Obj1")
obj2 = bpy.data.objects.get("Obj2")

empty = bpy.data.objects.get("Empty")

v1 = obj1.data.vertices[0]
v2 = obj2.data.vertices[0]

def toLocal(vertex, obj):
    return vertex @ obj.matrix_world.inverted()

def toGlobal(vertex, obj):
    return obj.matrix_world @ vertex

empty.location = toGlobal(v1.co, obj1)

# v2 => v1
# v1 global => local

print(toGlobal(v1.co, obj1) @ obj2.matrix_world)
print(obj1.matrix_world @ v1.co @ obj2.matrix_world)

#v2.co = toGlobal(v1.co, obj1) @ obj2.matrix_world

v2.co =  obj2.matrix_world.inverted() @ toGlobal(v1.co, obj1)

#v2.co = toLocal(toGlobal(v1.co, obj1) @ obj2.matrix_world - obj2.location, obj2)