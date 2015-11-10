import json
import random
from datetime import *

from networkx.readwrite import json_graph

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


def shortest_path_generator(road_network, graph, start, end, num_edge):
    if start is not None and end is not None:
        path = ShortestPath.check_shortest_path_from_db(road_network, graph, start, end)
    else:
        if start is not None:
            source = start.id
        else:
            intersections = road_network.intersections.all()
            source = intersections[random.randint(0, len(intersections)) - 1].id
        # Select the target intersections with the right path length to source
        target_set = []
        path_set = networkx.single_source_shortest_path(graph, source, num_edge)
        for path_index in path_set:
            if len(path_set[path_index]) == num_edge + 1:
                target_set.append(path_index)
        if settings.DEBUG:
            print "There are " + str(len(target_set)) + " trajectories to choose from..."
        # Randomly choose a target along with its path to source
        target_index = random.randint(0, len(target_set) - 1)
        sequence = path_set[target_set[target_index]]
        path = []
        length = 0
        for i in range(len(sequence) - 1):
            rid = graph.get_edge_data(sequence[i], sequence[i + 1])["id"]
            path.append(rid)
            length += graph.get_edge_data(sequence[i], sequence[i + 1])["weight"]
        path = [length, path]
    return path, target_set[target_index]


def initial_point(ini_road):
    p_set = list(ini_road.p.all())
    ini_location = random.randint(0, len(p_set) - 2)
    ini_bias = random.random()
    ini_lat = p_set[ini_location].lat + ini_bias * (p_set[ini_location + 1].lat - p_set[ini_location].lat)
    ini_lng = p_set[ini_location].lng + ini_bias * (p_set[ini_location + 1].lng - p_set[ini_location].lng)
    ini_p = Point(lat=ini_lat, lng=ini_lng)
    if settings.DEBUG:
        print "Initial point is between " + str(ini_location) + "th shape point(" + str(p_set[ini_location].lat) + "," + str(p_set[ini_location].lng) + ") and " + str(ini_location + 1) + "th shape point(" + str(p_set[ini_location + 1].lat) + "," + str(p_set[ini_location + 1].lng) + ") on road " + str(ini_road.id) + "..."
        print "Point location is (" + str(ini_p.lat) + "," + str(ini_p.lng) + ")"
    return [ini_p, ini_location]


def travel_direction(road, sec):
    if sec.p.lat == list(road.p.all())[0].lat and sec.p.lng == list(road.p.all())[0].lng:
        return -1
    elif sec.p.lat == list(road.p.all())[len(list(road.p.all())) - 1].lat and sec.p.lng == list(road.p.all())[len(list(road.p.all())) - 1].lng:
        return 1
    else:
        print "Input intersection not on input road!"
        raise IOError


def next_point(road_network, path, point, road, location, next_sec, path_index, distance):
    move_path = [road.id]
    p_set = list(road.p.all())
    d = travel_direction(road, next_sec)
    next_l = location + int(0.5 * d + 0.5)
    if (road.length / (len(p_set) - 1)) > distance:
        long_seg = 1
    else:
        long_seg = 0
    if settings.DEBUG:
        print "Before moving, travel direction is " + str(d)
        print "Before moving, next point index is " + str(next_l)
    next_lat = None
    next_lng = None
    while distance > 0:
        if settings.DEBUG:
            print "Current location is (" + str(point.lat) + "," + str(point.lng) + ")..."
        # Will not reach the next shape point
        if distance <= Distance.earth_dist(point, p_set[next_l]):
            if settings.DEBUG:
                print "Will not reach the next shape point..."
            if long_seg == 1:
                if settings.DEBUG:
                    print "Length of road " + str(road.id) + " is " + str(road.length) + " (too long)"
                # Current segment is too long, no need to stay on it
                remain_dis = distance
            else:
                if settings.DEBUG:
                    print "Length of road " + str(road.id) + " is " + str(road.length)
                # Randomly decide the remaining distance of the last road segment
                remain_dis = random.randint(int(distance) / 2, int(distance))
            k = remain_dis / Distance.earth_dist(point, p_set[next_l])
            next_lat = point.lat + k * (p_set[next_l].lat - point.lat)
            next_lng = point.lng + k * (p_set[next_l].lng - point.lng)
            distance = 0
            if settings.DEBUG:
                print "Finally stays between " + str(location) + "th shape point(" + str(p_set[location].lat) + "," + str(p_set[location].lng) + ") and " + str(next_l) + "th shape point(" + str(p_set[next_l].lat) + "," + str(p_set[next_l].lng) + ") on road " + str(road.id) + "..."
        else:
            distance -= Distance.earth_dist(point, p_set[next_l])
            point = p_set[next_l]
            if settings.DEBUG:
                print "The location of next intersection is (" + str(next_sec.p.lat) + "," + str(next_sec.p.lng) + ")"
            # Should move to the next road
            if point.lat == next_sec.p.lat and point.lng == next_sec.p.lng:
                if settings.DEBUG:
                    print "Reached to " + str(next_l) + "th shape point(" + str(p_set[next_l].lat) + "," + str(p_set[next_l].lng) + ") on road " + str(road.id) + "..."
                path_index += 1
                rid = path[1][path_index]
                road = road_network.roads.get(id=rid)
                # Skip the road containing only one point
                while len(list(road.p.all())) < 2:
                    path_index += 1
                    road = road_network.roads.get(id=path[1][path_index])
                move_path.append(road.id)
                p_set = list(road.p.all())
                connected = 0
                temp_sec = None
                for sec in road.intersection.all():
                    if settings.DEBUG:
                        print sec.id + ":" + str(sec.p.lat) + "," + str(sec.p.lng)
                    if sec.p.lat == next_sec.p.lat and sec.p.lng == next_sec.p.lng:
                        connected = 1
                    else:
                        temp_sec = sec
                if connected == 0:
                    print "Next road is not connected with previous road!"
                    raise IOError
                next_sec = temp_sec
                d = travel_direction(road, next_sec)
                if settings.DEBUG:
                    print d
                if d == 1:
                    next_l = 1
                elif d == -1:
                    next_l = len(p_set) - 2
                else:
                    print "Something is wrong while calculating direction!"
                    raise IOError
                if settings.DEBUG:
                    print "Switching to " + str(next_l - d) + "th shape point(" + str(p_set[next_l - d].lat) + "," + str(p_set[next_l - d].lng) + ") on road " + str(road.id) + "..."
                    print "Traveling towards " + str(next_l) + "th shape point(" + str(p_set[next_l].lat) + "," + str(p_set[next_l].lng) + ") on road " + str(road.id) + "..."
            # Stick to the current road
            else:
                next_l += d
                if settings.DEBUG:
                    print "Traveling towards " + str(next_l) + "th shape point(" + str(p_set[next_l].lat) + "," + str(p_set[next_l].lng) + ") on road " + str(road.id) + "..."
            location = next_l - int(0.5 * d + 0.5)
    next_p = Point(lat=next_lat, lng=next_lng)
    if settings.DEBUG:
        print "Point location is (" + str(next_p.lat) + "," + str(next_p.lng) + ")"
    dis_to_go = abs(Distance.length_to_start(next_p, road) - Distance.length_to_start(next_sec.p, road))
    if settings.DEBUG:
        print "Remaining distance on this road is " + str(dis_to_go)
    return [next_p, road, location, path_index, next_sec, move_path]


def add_noise(point, road, shake):
    delta = 33.6833599047  # Distribution parameter from real dataset
    noise_dist = random.gauss(0, delta * shake)
    while noise_dist >= 1436:  # Observed largest distance error
        noise_dist = abs(random.gauss(0, delta + shake))
    p_location = road.point_location(point)
    p1 = list(road.p.all())[p_location]
    p2 = list(road.p.all())[p_location + 1]
    delta_lat = abs(p2.lng - p1.lng) * noise_dist / Distance.earth_dist(p1, p2)
    delta_lng = abs(p2.lat - p1.lat) * noise_dist / Distance.earth_dist(p1, p2)
    lat_dir = random.choice((-1, 1))
    if p2.lng == p1.lng or (p2.lat - p1.lat) / (p2.lng - p1.lng) > 0:
        noised_lat = point.lat + lat_dir * delta_lat
        noised_lng = point.lng - lat_dir * delta_lng
    else:
        noised_lat = point.lat + lat_dir * delta_lat
        noised_lng = point.lng + lat_dir * delta_lng
    noised_p = Point(lat=noised_lat, lng=noised_lng)
    return noised_p


def synthetic_traj_generator(road_network, num_traj, num_sample, sample_rate, start, end, num_edge, shake, missing_rate):
    if settings.DEBUG:
        print "Building road network graph..."
    graph = json_graph.node_link_graph(json.loads(road_network.graph))
    traj_set = []
    ground_truth = []
    path_len = []
    for i in range(num_traj):
        if settings.DEBUG:
            print "Generating the " + str(i + 1) + "th trajectory..."
        traj_rids = []
        # Generate trajectory information
        taxi_id = str(uuid.uuid4())
        trace_id = str(uuid.uuid4())
        trace = Trace(id=trace_id)
        trace.save()
        traj_id = str(uuid.uuid4())
        traj = Trajectory(id=traj_id, taxi=taxi_id, trace=trace)
        traj.save()
        # Generate a shortest path
        path = [0, []]
        remain_num_edge = num_edge
        while remain_num_edge > 0:
            if remain_num_edge <= 50 or start is not None and end is not None:
                sub_path, target = shortest_path_generator(road_network, graph, start, end, remain_num_edge)
                remain_num_edge = 0
            # If the number of edges is too large, divide the generation process
            else:
                sub_path, target = shortest_path_generator(road_network, graph, start, end, 50)
                # Make sure the path does not turn around
                while len(path[1]) > 0 and sub_path[1][0] == path[1][len(path[1]) - 1]:
                    sub_path, target = shortest_path_generator(road_network, graph, start, end, 50)
                start = road_network.intersections.get(id=target)
                remain_num_edge -= 50
            path[0] += sub_path[0]
            path[1] += sub_path[1]
        if start is None and end is not None:
            path.reverse()
        # Generate the first sample
        if settings.DEBUG:
            print "Generating the first sample..."
        ini_sample_id = str(uuid.uuid4())
        ini_time = time_generator()
        ini_r_index = 0
        ini_road = road_network.roads.get(id=path[1][ini_r_index])
        # Skip the road containing only one point
        while len(list(ini_road.p.all())) < 2:
            ini_r_index += 1
            ini_road = road_network.roads.get(id=path[1][ini_r_index])
        ini_p = initial_point(ini_road)
        # Add Gaussian noise to each sample point
        noised_p = add_noise(ini_p[0], ini_road, shake)
        # noised_p = ini_p[0]
        noised_p.save()
        ini_sample = Sample(id=ini_sample_id, p=noised_p, t=ini_time, speed=0, angle=0, occupy=0, src=0)
        ini_sample.save()
        traj.trace.p.add(ini_sample)
        traj_rids.append([ini_road.id, [0]])
        # Save the current information for generating the next sample
        prev_p = ini_p[0]
        prev_road = ini_road
        prev_secset = prev_road.intersection.all()
        second_r_index = ini_r_index + 1
        second_road = road_network.roads.get(id=path[1][ini_r_index + 1])
        # Skip the road containing only one point
        while len(list(second_road.p.all())) < 2:
            second_r_index += 1
            second_road = road_network.roads.get(id=path[1][second_r_index])
        second_secset = second_road.intersection.all()
        if prev_secset[0].id == second_secset[0].id or prev_secset[0].id == second_secset[1].id:
            ini_sec = prev_secset[1]
            prev_sec = prev_secset[0]
        elif prev_secset[1].id == second_secset[0].id or prev_secset[1].id == second_secset[1].id:
            ini_sec = prev_secset[0]
            prev_sec = prev_secset[1]
        else:
            "First road is not connected with second road!"
            raise IOError
        d = travel_direction(prev_road, prev_sec)
        prev_l = ini_p[1]
        prev_path_index = 0
        prev_time = ini_time
        ini_dis = abs(Distance.length_to_start(ini_p[0], ini_road) - Distance.length_to_start(ini_sec.p, ini_road))
        avg_length = int((path[0] - ini_dis) / (num_sample - 1))
        if settings.DEBUG:
            print "Average length between each two sample is " + str(avg_length)
        current_sample_num = 0
        for j in range(num_sample - 1):
            if settings.DEBUG:
                print "Generating the " + str(current_sample_num + 2) + "th sample..."
            # Generate the next sample
            next_p = next_point(road_network, path, prev_p, prev_road, prev_l, prev_sec, prev_path_index, avg_length)
            time_interval = sample_rate + random.randint(0, 10)
            next_time = prev_time + timedelta(seconds=time_interval)
            miss = random.random()
            if miss > missing_rate:
                # Add Gaussian noise to each sample point
                noised_p = add_noise(next_p[0], next_p[1], shake)
                # noised_p = next_p[0]
                noised_p.save()
                next_sample_id = str(uuid.uuid4())
                next_sample = Sample(id=next_sample_id, p=noised_p, t=next_time, speed=0, angle=0, occupy=0, src=0)
                next_sample.save()
                traj.trace.p.add(next_sample)
                current_sample_num += 1
            if len(next_p[5]) == 1:
                if miss > missing_rate:
                    traj_rids[len(traj_rids) - 1][1].append(current_sample_num)
            else:
                for ii in range(1, len(next_p[5]) - 1):
                    traj_rids.append([next_p[5][ii], []])
                if miss > missing_rate:
                    traj_rids.append([next_p[5][len(next_p[5]) - 1], [current_sample_num]])
                else:
                    traj_rids.append([next_p[5][len(next_p[5]) - 1], []])
            prev_time = next_time
            prev_p = next_p[0]
            prev_road = next_p[1]
            prev_l = next_p[2]
            prev_path_index = next_p[3]
            prev_sec = next_p[4]
        traj_set.append(traj)
        path_len.append(path[0])
        ground_truth.append(traj_rids)
        if settings.DEBUG:
            print path
    return [traj_set, ground_truth, path_len]
