import random
from datetime import *
from avatar_core.geometry import *
from avatar_map_matching.shortest_path import *

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

def initial_point(road_set):
    ini_road = road_set[random.randint(0, len(road_set) - 1)]
    while len(ini_road.p.all()) <= 2:
	ini_road = road_set[random.randint(0, len(road_set) - 1)]
    p_set = ini_road.p.all()
    ini_location = random.randint(1, len(p_set) - 2)
    if ini_location < len(p_set) - 1:
	ini_bias = random.random()
	ini_lat = p_set[ini_location].lat + ini_bias * (p_set[ini_location + 1].lat - p_set[ini_location].lat)
	ini_lng = p_set[ini_location].lng + ini_bias * (p_set[ini_location + 1].lng - p_set[ini_location].lng)
	ini_p = Point(lat=ini_lat, lng=ini_lng)
    else:
	ini_p = p_set[ini_location]
    print "Initial point is between " + str(ini_location) + "th shape point(" + str(p_set[ini_location].lat) + "," + str(p_set[ini_location].lng) + ") and " + str(ini_location + 1) + "th shape point(" + str(p_set[ini_location + 1].lat) + "," + str(p_set[ini_location + 1].lng) + ") on road " + str(ini_road.id) + "..."
    print "Point location is (" + str(ini_p.lat) + "," + str(ini_p.lng) + ")"
    return [ini_p, ini_road, ini_location]

def travel_direction(road, sec):
    if sec.p.lat == road.p.all()[0].lat and sec.p.lng == road.p.all()[0].lng:
	return -1
    elif sec.p.lat == road.p.all()[len(road.p.all()) - 1].lat and sec.p.lng == road.p.all()[len(road.p.all()) - 1].lng:
	return 1
    else:
	print "Input intersection not on input road!"
	return 0

def next_point(road_network, point, road, location, speed, next_sec, time):
    path = [road.id]
    if speed == 0:
	next_p = point
	d = travel_direction(road, next_sec)
	next_l = location + int(0.5 * d + 0.5)
	print "Same as previous point..."
    else:
	total_dis = float(time * speed)
	p_set = road.p.all()
	d = travel_direction(road, next_sec)
	print d
	next_l = location + int(0.5 * d + 0.5)
	remain_dis = total_dis
	while remain_dis > 0:
	    print "Current location is (" + str(point.lat) + "," + str(point.lng) + ")..."
	    # Will not reach the next shape point
	    if remain_dis <= Distance.earth_dist(point, p_set[next_l]):
		k = remain_dis / Distance.earth_dist(point, p_set[next_l])
            	next_lat = point.lat + k * (p_set[next_l].lat - point.lat)
            	next_lng = point.lng + k * (p_set[next_l].lng - point.lng)
		remain_dis = 0
		print "Finally stays between " + str(location) + "th shape point(" + str(p_set[location].lat) + "," + str(p_set[location].lng) + ") and " + str(next_l) + "th shape point(" + str(p_set[next_l].lat) + "," + str(p_set[next_l].lng) + ") on road " + str(road.id) + "..."
	    else:
		remain_dis -= Distance.earth_dist(point, p_set[next_l])
		point = p_set[next_l]
		# Should move to another road
		if point.lat == next_sec.p.lat and point.lng == next_sec.p.lng:
		    print "Reached to " + str(next_l) + "th shape point(" + str(p_set[next_l].lat) + "," + str(p_set[next_l].lng) + ") on road " + str(road.id) + "..."
		    road_set = road_network.roads.filter(intersection__id__exact=next_sec.id)
		    if len(road_set) == 1:
			print "No other road to switch, turning back..."
		    else:
		        r_index = random.randint(0, len(road_set) - 1)
		        while road.id == road_set[r_index].id:
			    r_index = random.randint(0, len(road_set) - 1)
		        road = road_set[r_index]
		        path.append(road.id)
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
    return [next_p, road, location, next_sec, path]

def add_noise(point, delta_lat, delta_lng):
    noised_lat = point.lat + random.gauss(0, delta_lat * 0.5)
    noised_lng = point.lng + random.gauss(0, delta_lng * 0.5)
    noised_p = Point(lat=noised_lat, lng=noised_lng)
    return noised_p
	
def traj_generator(road_network, num_traj, num_sample, stop_rate, sample_rate, delta_lat, delta_lng):
    print "Loading road network..."
    road_set = road_network.roads.all()
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
	# Generate the first sample
	print "Generating the first sample..."
	ini_sample_id = 100000000 + i
	ini_time = time_generator()
	ini_p = initial_point(road_set)
	# Add Guassian noise to each sample point
	noised_p = add_noise(ini_p[0], delta_lat, delta_lng)
#	noised_p = ini_p[0]
	noised_p.save()
	ini_stop = random.random()
	if ini_stop < stop_rate:
	    ini_stop = 0
	else:
	    ini_stop = 1
	ini_speed = random.randint(5, 25) * ini_stop	# m/s
	ini_sample = Sample(id=str(ini_sample_id), p=noised_p, t=ini_time, speed=ini_speed, angle=0, occupy=0, src=0)
	ini_sample.save()
	traj.trace.p.add(ini_sample)
	traj_rids.append(ini_p[1].id)
	# Save the current information for generating the next sample
	prev_sample = ini_sample
	prev_p = ini_p[0]
	prev_road = ini_p[1]
	prev_secset = prev_road.intersection.all()
	prev_sec = prev_secset[random.randint(0, len(prev_secset) - 1)]
	d = travel_direction(prev_road, prev_sec)
        print d
        prev_l = ini_p[2] + int(-0.5 * d + 0.5)
	for j in range(num_sample - 1):
	    print "Generating the " + str(j + 2) + "th sample..."
	    # Generate the next sample
	    time_interval = sample_rate + random.randint(-10, 10)
	    next_time = prev_sample.t + timedelta(seconds=time_interval)
	    next_stop = random.random()
	    if next_stop < stop_rate:
		next_stop = 0
	    else:
		next_stop = 1
	    next_speed = random.randint(5, 25) * next_stop
	    next_p = next_point(road_network, prev_p, prev_road, prev_l, prev_sample.speed, prev_sec, time_interval)
	    # Add Guassian noise to each sample point
	    noised_p = add_noise(next_p[0], delta_lat, delta_lng)
#	    noised_p = next_p[0]
	    noised_p.save()
	    next_sample_id = 100000000 + i + j + 1
	    next_sample = Sample(id=str(next_sample_id), p=noised_p, t=next_time, speed=next_speed, angle=0, occupy=0, src=0)
	    next_sample.save()
	    traj.trace.p.add(next_sample)
	    traj_rids.append(next_p[1].id)
	    prev_sample = next_sample
	    prev_p = next_p[0]
	    prev_road = next_p[1]
	    prev_l = next_p[2]
	    prev_sec = next_p[3]
	traj_set.append(traj)
	ground_truth.append(traj_rids)
    return [traj_set, ground_truth]
