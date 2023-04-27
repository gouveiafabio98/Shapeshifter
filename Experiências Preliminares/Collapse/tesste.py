def index_distance(first, second, length):
    if first == second:
        return 0
    elif second > first:
        return second - first
    else:
        return length - first + second

tv1 = 10
tv2 = 10
collapsed_pairs = [[5, 5]]
v2 = 4

print("\n")

s2_before, s2_after = None, None
s2_before_dist, s2_after_dist = tv2, tv2

for pair in collapsed_pairs:
    if s2_after_dist >= index_distance(v2, pair[1], tv2):
        s2_after_dist = index_distance(v2, pair[1], tv2)
        s2_after = pair
    if s2_before_dist >= index_distance(pair[1], v2, tv2):
        s2_before_dist = index_distance(pair[1], v2, tv2)
        s2_before = pair

if s2_before[1] == s2_after[1]:
    v2_total_dist = tv2
else:
    v2_total_dist = index_distance(s2_before[1], s2_after[1], tv2)


options = []

for v1 in range(tv1):
    if index_distance(v1, s2_before[0], tv1) < index_distance(v1, s2_after[0], tv1):
        s1_before_dist = index_distance(v1, s2_before[0], tv1)
        s1_after_dist = index_distance(s2_after[0], v1, tv1)
        if s2_before[0] == s2_after[0]:
            v1_total_dist = tv1
            s1_before_dist = tv1 - s1_after_dist
        else:
            v1_total_dist = index_distance(s2_after[0], s2_before[0], tv1)
    else:
        s1_before_dist = index_distance(s2_before[0], v1, tv1)
        s1_after_dist = index_distance(v1, s2_after[0], tv1)
        if s2_before[0] == s2_after[0]:
            v1_total_dist = tv1
            s1_after_dist = tv1 - s1_before_dist
        else:
            v1_total_dist = index_distance(s2_before[0], s2_after[0], tv1)

    if len(collapsed_pairs) == 1:
        #if s1_after_dist < s1_before_dist and s2_before_dist < s2_after_dist:
        if (s1_after_dist < s1_before_dist and s2_after_dist > s2_before_dist) or (s1_after_dist > s1_before_dist and s2_after_dist < s2_before_dist):
            s1_before_dist, s1_after_dist = s1_after_dist, s1_before_dist
            
        #s2_before_dist = min(s2_before_dist, s2_after_dist)
        #s2_after_dist = s2_before_dist

    deviation = v2_total_dist - v1_total_dist
    #if v1 == 9:
    #    print("V2", s2_after_dist, s2_before_dist)
    #    print("V1", s1_after_dist, s1_before_dist)
    #    print("TOTAL", v1_total_dist, v2_total_dist)
    #    print("DESVIO", deviation)

    if not (s2_after_dist - s1_after_dist > deviation or s2_before_dist - s1_before_dist > deviation):
        #print("REMOVER", v1, "DE", v2)
    #else:
        #print("OK", v1, "DE", v2)
        options.append(v1)

print(v2, options)