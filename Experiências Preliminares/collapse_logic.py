import bpy
import math
from mathutils import Vector

obj1 = bpy.data.objects.get("Octagon")
obj2 = bpy.data.objects.get("Pentagon")

s1 = obj1.data.vertices
s2 = obj2.data.vertices

def to_local(vertex, obj):
    return obj.matrix_world.inverted() @ vertex

def to_global(vertex, obj):
    return obj.matrix_world @ vertex

def index_distance(first, second, length):
    if first >= second:
        return abs(first - second)
    else:
        return abs(length - first - second)

def collapse(s1, obj1, s2, obj2):
    if len(s1) > len(s2):
        s1, s2 = s2, s1
        
    s1_length = len(s1)
    s2_length = len(s2)
    
    collapsed_pairs = []
    
    s2_options = {i: set(range(len(s1))) for i in range(len(s2))}
    
    while len(s2_options)>0:
        min_dist = float('inf')
        closest_pair = None
        
        for v2 in s2_options.keys():
            for v1 in s2_options[v2].copy():
                dist = math.dist(s1[v1].co, s2[v2].co)
                if dist < min_dist:
                    min_dist = dist
                    closest_pair = [v1, v2]
        
        # Add best combination
        collapsed_pairs.append(closest_pair)
        s2[closest_pair[1]].co = to_local(to_global(s1[closest_pair[0]].co, obj1) - obj2.location + obj1.location, obj2)

        # Remove from the list of possible options
        del s2_options[closest_pair[1]]
        
        # Options adjustment
        for v2 in s2_options.copy().keys():

            s2_before, s2_after = None, None
            s2_before_dist, s2_after_dist = s2_length, s2_length

            for pair in collapsed_pairs:
                if s2_before_dist >= index_distance(v2, pair[1], s2_length):
                    s2_before_dist = index_distance(v2, pair[1], s2_length)
                    s2_before = pair
                if s2_after_dist >= index_distance(pair[1], v2, s2_length):
                    s2_after_dist = index_distance(pair[1], v2, s2_length)
                    s2_after = pair
            
            for v1 in s2_options[v2].copy():
                if len(collapsed_pairs) <= 1:
                    dist_min = min(index_distance(v1, s2_before[0], s1_length), index_distance(s2_after[0], v1, s1_length))
                    if dist_min > s2_before_dist or dist_min > s2_after_dist:
                        s2_options[v2].remove(v1)
                else:
                    if index_distance(v1, s2_before[0], s1_length) > s2_before_dist:
                        s2_options[v2].remove(v1)
                    elif index_distance(s2_after[0], v1, s1_length) > s2_after_dist:
                        s2_options[v2].remove(v1)
                if len(s2_options[v2]) == 0:
                    del s2_options[v2]
    
collapse(s1, obj1, s2, obj2)