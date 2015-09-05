import Queue

from avatar.common import *


class ShortestPath:
    def __init__(self):
        pass

    @staticmethod
    # route distance between two points that are both on the road network
    def shortest_path_angle(p1, road1, p2, road2):
        if road1.id == road2.id:
            #	    print 'p1 and p2 are in the same road...'
            return abs(Distance.length_to_start(p1, road1) - Distance.length_to_start(p2, road2))
            # should use shortest path algorithm
        p_cross = Distance.check_intersection(road1, road2)
        if p_cross is not None:
            p1_cross = abs(Distance.length_to_start(p1, road1) - Distance.length_to_start(p_cross, road1))
            p2_cross = abs(Distance.length_to_start(p2, road2) - Distance.length_to_start(p_cross, road2))
            #	    print 'road1 and road2 have intersection...'
            return p1_cross + p2_cross
        else:
            p1_set = road1.p.all()
            p2_set = road2.p.all()
            if Angle.intersection_angle(p2, p1, p1_set[0], p1_set[len(p1_set) - 1]) <= 90:
                p1_cross = Distance.earth_dist(p1, p1_set[0])
                cross1 = p1_set[0]
            else:
                p1_cross = Distance.earth_dist(p1, p1_set[len(p1_set) - 1])
                cross1 = p1_set[len(p1_set) - 1]
            if Angle.intersection_angle(p1, p2, p2_set[0], p2_set[len(p2_set) - 1]) <= 90:
                p2_cross = Distance.earth_dist(p2, p2_set[0])
                cross2 = p2_set[0]
            else:
                p2_cross = Distance.earth_dist(p2, p2_set[len(p2_set) - 1])
                cross2 = p2_set[len(p2_set) - 1]
            #	    print 'road1 and road2 have no intersection...'
            return p1_cross + p2_cross + Distance.earth_dist(cross1, cross2)

    # @staticmethod
    # def shortest_path(p1, road1, p2, road2):
    #     if road1.id == road2.id:
    #         return abs(Distance.length_to_start(p1, road1) - Distance.length_to_start(p2, road2))
    #     return 0

    @staticmethod
    def shortest_path_dijkstra(p1, road1, p2, road2):
        #	print road1.id == road2.id
        if road1.id == road2.id:
            dis = abs(Distance.length_to_start(p1, road1) - Distance.length_to_start(p2, road2))
            return (dis, [[road1.id], [None]])
        p_cross = Distance.check_intersection(road1, road2)
        if p_cross is not None:
            p1_cross = abs(Distance.length_to_start(p1, road1) - Distance.length_to_start(p_cross.p, road1))
            p2_cross = abs(Distance.length_to_start(p2, road2) - Distance.length_to_start(p_cross.p, road2))
            #	    print 'road1 and road2 have intersection...'
            return (p1_cross + p2_cross, [[road1.id, road2.id], [p_cross.id]])
        else:
            path = Queue.PriorityQueue()
            ini_intersec = road1.intersection.all()
            first_seg = abs(Distance.length_to_start(ini_intersec[0].p, road1) - Distance.length_to_start(p1, road1))
            searched1 = (first_seg, [[road1.id], [ini_intersec[0].id]])
            path.put(searched1)
            if len(ini_intersec) > 1:
                first_seg = abs(Distance.length_to_start(ini_intersec[1].p, road1) - Distance.length_to_start(p1, road1))
                searched2 = (first_seg, [[road1.id], [ini_intersec[1].id]])
                path.put(searched2)
            while path.qsize() > 0:
                print path.qsize()
                shortest = path.get()
                #		print shortest[1][0]
                rids = shortest[1][0]
                intersecids = shortest[1][1]
                last_road = Road.objects.get(id=rids[len(rids) - 1])
                for sec in last_road.intersection.all():
                    if sec.id != intersecids[len(intersecids) - 1] and not intersecids.__contains__(sec.id):
                        for road in Road.objects.filter(intersection__id__exact=sec.id):
                            if road.id != rids[len(rids) - 1] and not rids.__contains__(road.id):
                                if road.id == road2.id:
                                    newrids = shortest[1][0][:]
                                    newintersecids = shortest[1][1][:]
                                    newrids.append(road.id)
                                    last_seg = abs(Distance.length_to_start(sec.p, road2) - Distance.length_to_start(p2, road2))
                                    newdist = shortest[0] + last_seg
                                    result = (newdist, [newrids, newintersecids])
                                    return result
                                else:
                                    newrids = shortest[1][0][:]
                                    newintersecids = shortest[1][1][:]
                                    newrids.append(road.id)
                                    newintersecids.append(sec.id)
                                    newdist = shortest[0] + road.length
                                    newpath = (newdist, [newrids, newintersecids])
                                    path.put(newpath)
                                #				    print newpath[1][0]
        return None

    @staticmethod
    def shortest_path_astar_intersec(intersec1, intersec2):
        frontier = Queue.PriorityQueue()
        first_sec = (0.0, [intersec1.id, None])
        frontier.put(first_sec)
        came_from = {}
        cost_so_far = {}
        came_from[intersec1.id] = None
        cost_so_far[intersec1.id] = 0.0
        while frontier.qsize() > 0:
            #	    print frontier.qsize()
            current = frontier.get()
            if current[1][0] == intersec2.id:
                break
            for road in Road.objects.filter(intersection__id__exact=current[1][0]):
                secset = road.intersection.all()
                if len(secset) > 1:
                    if secset[0].id == current[1][0]:
                        nextsec = secset[1]
                    else:
                        nextsec = secset[0]
                    new_cost = cost_so_far[current[1][0]] + road.length
                    if nextsec.id not in cost_so_far or new_cost < cost_so_far[nextsec.id]:
                        cost_so_far[nextsec.id] = new_cost
                        # Use earth distance between next and goal as heuristic cost
                        priority = new_cost + Distance.earth_dist(nextsec.p, intersec2.p)
                        next_move = (priority, [nextsec.id], [road.id])
                        frontier.put(next_move)
                        came_from[nextsec.id] = [current[1][0], road.id]
        path = []
        pathlen = 0.0
        prev_sec = intersec2.id
        while prev_sec != intersec1.id:
            point_to = came_from[prev_sec]
            prev_sec = point_to[0]
            path.append(point_to[1])
        for rid in path:
            road = Road.objects.get(id=rid)
            pathlen += road.length
        return [pathlen, path]

    @staticmethod
    def shortest_path_astar(p1, road1, p2, road2):
        if road1.id == road2.id:
            dis = abs(Distance.length_to_start(p1, road1) - Distance.length_to_start(p2, road2))
            return (dis, [road1.id])
        p_cross = Distance.check_intersection(road1, road2)
        if p_cross is not None:
            p1_cross = abs(Distance.length_to_start(p1, road1) - Distance.length_to_start(p_cross.p, road1))
            p2_cross = abs(Distance.length_to_start(p2, road2) - Distance.length_to_start(p_cross.p, road2))
            #           print 'road1 and road2 have intersection...'
            return (p1_cross + p2_cross, [road2.id, road1.id])
        else:
            dis_between_sec = 16777215.0
            intersec1 = road1.intersection.all()
            intersec2 = road2.intersection.all()
            id1 = 0
            id2 = 0
            for i in range(len(intersec1)):
                for j in range(len(intersec2)):
                    if Distance.earth_dist(intersec1[i].p, intersec2[j].p) < dis_between_sec:
                        id1 = i
                        id2 = j
            path = ShortestPath.shortest_path_astar_intersec(intersec1[id1], intersec2[id2])
            dis1 = abs(Distance.length_to_start(p1, road1) - Distance.length_to_start(intersec1[id1].p, road1))
            dis2 = abs(Distance.length_to_start(p2, road2) - Distance.length_to_start(intersec2[id2].p, road2))
            return (path[0] + dis1 + dis2, [road2.id] + path[1] + [road1.id])
