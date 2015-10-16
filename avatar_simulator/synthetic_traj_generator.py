import random
from datetime import *
from avatar_core.geometry import *
from avatar_map_matching.shortest_path import *
from avatar_core.common import *
import networkx as nx

def time_generator():
    year = 2014
    month = random.randint(1, 12)
    if month in [1, 3, 5, 7, 8, 10, 12]:
	day = random.randint(1, 31)
    elif month in [4, 6, 9, 11]:
	day = random.randint(1, 30)
    else:
	day = random.randint(1, 28)
    hour = random.randint(6, 22)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return datetime(year, month, day, hour, minute, second)

def initial_point(ini_road):
    p_set = ini_road.p.all()
    ini_location = random.randint(0, len(p_set) - 2)
    ini_bias = random.random()
    ini_lat = p_set[ini_location].lat + ini_bias * (p_set[ini_location + 1].lat - p_set[ini_location].lat)
    ini_lng = p_set[ini_location].lng + ini_bias * (p_set[ini_location + 1].lng - p_set[ini_location].lng)
    ini_p = Point(lat=ini_lat, lng=ini_lng)
    print "Initial point is between " + str(ini_location) + "th shape point(" + str(p_set[ini_location].lat) + "," + str(p_set[ini_location].lng) + ") and " + str(ini_location + 1) + "th shape point(" + str(p_set[ini_location + 1].lat) + "," + str(p_set[ini_location + 1].lng) + ") on road " + str(ini_road.id) + "..."
    print "Point location is (" + str(ini_p.lat) + "," + str(ini_p.lng) + ")"
    return [ini_p, ini_location]

def travel_direction(road, sec):
    if sec.p.lat == road.p.all()[0].lat and sec.p.lng == road.p.all()[0].lng:
	return -1
    elif sec.p.lat == road.p.all()[len(road.p.all()) - 1].lat and sec.p.lng == road.p.all()[len(road.p.all()) - 1].lng:
	return 1
    else:
	print "Input intersection not on input road!"
	return 0

def next_point(path, point, road, location, next_sec, path_index, distance):
    move_path = [road.id]
    p_set = road.p.all()
    d = travel_direction(road, next_sec)
    print d
    next_l = location + int(0.5 * d + 0.5)
    while distance > 0:
	print "Current location is (" + str(point.lat) + "," + str(point.lng) + ")..."
	# Will not reach the next shape point
	if distance <= Distance.earth_dist(point, p_set[next_l]):
	    # Randomly decide the remaining distance of the last road segment	    
	    remain_dis = random.randint(0, distance)
	    k = remain_dis / Distance.earth_dist(point, p_set[next_l])
            next_lat = point.lat + k * (p_set[next_l].lat - point.lat)
            next_lng = point.lng + k * (p_set[next_l].lng - point.lng)
	    distance = 0
	    print "Finally stays between " + str(location) + "th shape point(" + str(p_set[location].lat) + "," + str(p_set[location].lng) + ") and " + str(next_l) + "th shape point(" + str(p_set[next_l].lat) + "," + str(p_set[next_l].lng) + ") on road " + str(road.id) + "..."
	else:
	    distance -= Distance.earth_dist(point, p_set[next_l])
	    point = p_set[next_l]
	    # Should move to the next road
	    if point.lat == next_sec.p.lat and point.lng == next_sec.p.lng:
		print "Reached to " + str(next_l) + "th shape point(" + str(p_set[next_l].lat) + "," + str(p_set[next_l].lng) + ") on road " + str(road.id) + "..."
		path_index += 1
		road = path[path_index]
		move_path.append(road.id)
		p_set = road.p.all()
		for sec in road.intersection.all():
		    if sec.id != next_sec.id:
			next_sec = sec
			break
		d = travel_direction(road, next_sec)
		print d
		if d == 1:
		    next_l = 1
		else:
		    next_l = len(p_set) - 2
		print "Switching to " + str(next_l - d) + "th shape point(" + str(p_set[next_l - d].lat) + "," + str(p_set[next_l - d].lng) + ") on road " + str(road.id) + "..."
		print "Traveling towards " + str(next_l) + "th shape point(" + str(p_set[next_l].lat) + "," + str(p_set[next_l].lng) + ") on road " + str(road.id) + "..."
	    # Stick to the current road
	    else:
		next_l += d
		print "Traveling towards " + str(next_l) + "th shape point(" + str(p_set[next_l].lat) + "," + str(p_set[next_l].lng) + ") on road " + str(road.id) + "..."
	    location = next_l - d
    next_p = Point(lat=next_lat, lng=next_lng)
    print "Point location is (" + str(next_p.lat) + "," + str(next_p.lng) + ")" 
    return [next_p, road, location, path_index, next_sec, path]

def add_noise(point, delta_lat, delta_lng):
    noised_lat = point.lat + random.gauss(0, delta_lat * 0.5)
    noised_lng = point.lng + random.gauss(0, delta_lng * 0.5)
    noised_p = Point(lat=noised_lat, lng=noised_lng)
    return noised_p

def synthetic_traj_generator(road_network, num_traj, num_sample, sample_rate, start, end, num_edge, delta_lat, delta_lng, missing_rate):
    print "Building road network graph..."
    graph = build_road_network_graph(road_network)
    traj_set = []
    ground_truth = []
    for i in range(num_traj):
	print "Generating the " + str(i + 1) + "th trajectory..."
	traj_rids = []
	# Generate trajectory information
        taxi_id = random.randint(1, 20000)
        trace = Trace(id=str(i))
        trace.save()
        traj = Trajectory(id=str(i), taxi=str(taxi_id), trace=trace)
        traj.save()
	# Generate a shortest path
	if start is not None and end is not None:
	    path = ShortestPath.check_shortest_path_from_db(road_network, graph, start, end)
	else:
	    source = None
	    if start is not None:
		source = start.id
	    elif end is not None:
		source = end.id
	    else:
		intersections = road_network.intersections.all()
		source = intersections[random.randint(0, len(intersections) - 1)].id
	    # Select the target intersections with the right path length to source
	    target_set = []
	    path_set = nx.single_source_shortest_path(graph, source, num_edge)
	    for path_index in path_set:
		if len(path_set[path_index]) == length + 1:
		    target_set.append(path_index)
	    # Randomly choose a target along with its path to source
	    target_index = random.randint(0, len(target_set) - 1)
	    sequence = path_set[target_set[target_index]]
	    path = []
	    length = 0
	    for i in range(len(sequence) - 1):
                rid = graph.get_edge_data(sequence[i], sequence[i+1])["id"]
                path.append(rid)
		length += graph.get_edge_data(sequence[i], sequence[i+1])["weight"]
	    path = [length, path]
	    if start is None:
		path[1].reverse()
	# Generate the first sample
	print "Generating the first sample..."
        ini_sample_id = 100000000 + i
        ini_time = time_generator()
	ini_road = road_network.roads.get(id=path[1][0])
        ini_p = initial_point(ini_road)
        # Add Guassian noise to each sample point
        noised_p = add_noise(ini_p[0], delta_lat, delta_lng)
	noised_p.save()
	ini_sample = Sample(id=str(ini_sample_id), p=noised_p, t=ini_time, speed=0, angle=0, occupy=0, src=0)
	ini_sample.save()
	traj.trace.p.add(ini_sample)
	traj_rids.append([ini_p[1].id, [0]])
	# Save the current information for generating the next sample
	prev_p = ini_p[0]
	prev_road = ini_road
	prev_secset = prev_road.intersection.all()
	second_road = road_network.roads.get(id=path[1][1])
	second_secset = second_road.intersection.all()
	if prev_secset[0].id == second_secset[0].id or prev_secset[0].id != second_secset[1].id:
	    prev_sec = prev_secset[0]
	else:
	    prev_sec = prev_secset[1]
	d = travel_direction(prev_road, prev_sec)
	prev_l = ini_p[1] + int(-0.5 * d + 0.5)
	prev_path_index = 0
	prev_time = ini_time
	ini_dis = abs(Distance.length_to_start(ini_p[0], ini_road) - Distance.length_to_start(prev_sec.p, ini_road))
	avg_length = int((path[0] - ini_dis) / num_sample)
	for j in range(num_sample - 1):
            print "Generating the " + str(j + 2) + "th sample..."
            # Generate the next sample
	    next_p = next_point(path, prev_p, prev_road, prev_l, prev_sec, prev_path_index, avg_length)
	    miss = random.random()
	    if miss > missing_rate:
	        # Add Guassian noise to each sample point
                noised_p = add_noise(next_p[0], delta_lat, delta_lng)
                noised_p.save()
                next_sample_id = 100000000 + i + j + 1
	        time_interval = sample_rate + random.randint(-10, 10)
                next_time = prev_time + timedelta(seconds=time_interval)
                next_sample = Sample(id=str(next_sample_id), p=noised_p, t=next_time, speed=0, angle=0, occupy=0, src=0)
            	next_sample.save()
            	traj.trace.p.add(next_sample)
	    if len(next_p[5]) == 1:
		if miss > missing_rate:
		    traj_rids[len(traj_rids) - 1][1].append(j + 1)
	    else:
		for ii in range(1, len(next_p[5]) - 1):
		    traj_rids.append([next_p[5][ii].id], [])
		if miss > missing_rate:
		    traj_rids.append([next_p[5][len(next_p[5] - 1)].id, [j + 1]])
		else:
		    traj_rids.append([next_p[5][len(next_p[5] - 1)].id, []])
            prev_p = next_p[0]
            prev_road = next_p[1]
            prev_l = next_p[2]
	    prev_path_index = next_p[3]
            prev_sec = next_p[4]
	    prev_time = next_time
	traj_set.append(traj)
        ground_truth.append(traj_rids)
    return [traj_set, ground_truth]
