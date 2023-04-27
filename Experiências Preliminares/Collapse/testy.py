def index_distance(first, second, length):
    if first == second:
        return 0
    elif second > first:
        return second - first
    else:
        return length - first + second

s1_length = 10
s2_length = 10
collapsed_pairs = [[5, 5]]

before, after = None, None
s2_before_dist, s2_after_dist = s2_length, s2_length

v2 = 4

for pair in collapsed_pairs:
    if s2_after_dist >= index_distance(v2, pair[1], s2_length):
        s2_after_dist = index_distance(v2, pair[1], s2_length)
        after = pair
    if s2_before_dist >= index_distance(pair[1], v2, s2_length):
        s2_before_dist = index_distance(pair[1], v2, s2_length)
        before = pair

s2_total_dist = s2_after_dist + s2_before_dist

options = []

v1 = 6
#for v1 in range(s1_length):
if True:
    s1_before_dist, s1_after_dist = s1_length, s1_length
    if index_distance(v1, before[0], s1_length) > index_distance(v1, after[0], s1_length):
        print("HERE ONE")
        s1_after_dist = index_distance(v1, after[0], s1_length)
        s1_before_dist = index_distance(before[0], v1, s1_length)
    else:
        print("HERE TWO", after[0], before[0])
        s1_before_dist = index_distance(v1, before[0], s1_length)
        s1_after_dist = index_distance(after[0], v1, s1_length)
        if index_distance(v1, before[0], s1_length) == index_distance(v1, after[0], s1_length):
            if s1_after_dist > s1_before_dist:
                s1_after_dist, s1_before_dist = s1_before_dist, s1_after_dist

    print("TESTE", s1_before_dist, s1_after_dist)
    if v1 == after[0]:
        s1_before_dist = index_distance(v1, before[0], s1_length)
    if v1 == before[0]:
        s1_after_dist = index_distance(after[0], v1, s1_length)

    s1_total_dist = s1_after_dist + s1_before_dist

    deviation = s2_total_dist - s1_total_dist

    if True:
        #print("\nCURRENT V1", v1)
        print("TOTAL", s1_total_dist, s2_total_dist)
        print("V1", s1_after_dist, s1_before_dist)
        print("V2", s2_after_dist, s2_before_dist)
        print("DEVIATION", deviation)

    if not(s2_after_dist - s1_after_dist > deviation or s2_before_dist - s1_before_dist > deviation):
        #options.append(v1)
        print("YES", v1)
#print(v2, options)