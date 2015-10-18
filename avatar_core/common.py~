import math

from models import *


class Distance:
    earth_radius = 6371000.0
    degrees_to_radians = math.pi / 180.0
    radians_to_degrees = 180.0 / math.pi

    def __init__(self):
        pass

    @staticmethod
    def earth_dist(p1, p2):
        dlat = (p2.lat - p1.lat) * Distance.degrees_to_radians
        dlng = (p2.lng - p1.lng) * Distance.degrees_to_radians
        a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(p1.lat * Distance.degrees_to_radians) * math.cos(p2.lat * Distance.degrees_to_radians) * math.sin(dlng / 2) * math.sin(dlng / 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        dist = Distance.earth_radius * c
        return dist

    @staticmethod
    def perpendicular_dist(p0, p1, p2):
        seg_lat = p2.lat - p1.lat
        seg_lng = p2.lng - p1.lng
        pp1_lat = p0.lat - p1.lat
        pp1_lng = p0.lng - p1.lng
        c1_vector = pp1_lat * seg_lat + pp1_lng * seg_lng
        if c1_vector <= 0:
            mapped_p = Point(lat=p1.lat, lng=p1.lng)
            dist = Distance.earth_dist(p0, p1)
            return {'mapped': mapped_p, 'dist': dist}
        c2_vector = seg_lat * seg_lat + seg_lng * seg_lng
        if c2_vector <= c1_vector:
            mapped_p = Point(lat=p2.lat, lng=p2.lng)
            dist = Distance.earth_dist(p0, p2)
            return {'mapped': mapped_p, 'dist': dist}
        ratio = c1_vector / c2_vector
        mapped_p = Point(lat=ratio * seg_lat + p1.lat, lng=ratio * seg_lng + p1.lng)
        dist = Distance.earth_dist(p0, mapped_p)
        return {'mapped': mapped_p, 'dist': dist}

    @staticmethod
    def point_map_to_road(p, road):
        dist = 16777215.0
        mapped_p = None
        location = 0
        p_set = road.p.all()
        for i in range(0, len(p_set) - 1):
            p1 = p_set[i]
            p2 = p_set[i + 1]
            p2r_dist = Distance.perpendicular_dist(p, p1, p2)
            if p2r_dist['dist'] < dist:
                dist = p2r_dist['dist']
                mapped_p = p2r_dist['mapped']
                location = i
        return {'mapped': mapped_p, 'location': location, 'dist': dist}

    @staticmethod
    # route distance between the query point and the first point of the road
    def length_to_start(p, road):
        all_p = road.p.all()
        location = road.point_location(p)
        length_p = 0.0
        for i in range(0, location):
            length_p += Distance.earth_dist(all_p[i], all_p[i + 1])
        length_p += Distance.earth_dist(all_p[location], p)
        return length_p

    @staticmethod
    def road_length(road):
        all_p = road.p.all()
        length = 0.0
        for i in range(len(all_p) - 1):
            length += Distance.earth_dist(all_p[i], all_p[i + 1])
        return length

    @staticmethod
    def check_intersection(road1, road2):
        for p1 in road1.intersection.all():
            for p2 in road2.intersection.all():
                if p1.p.lat == p2.p.lat and p1.p.lng == p2.p.lng:
                    return p1
        return None


class Angle:
    def __init__(self):
        pass

    @staticmethod
    def horizontal_angle(p1, p2):
        if p1.lng == p2.lng:
            if p1.lat < p2.lat:
                angle = 90
            elif p1.lat > p2.lat:
                angle = 270
            else:
                angle = 0
        else:
            angle = math.atan((p2.lat - p1.lat) / (p2.lng - p1.lng)) * Distance.radians_to_degrees
            if p1.lng < p2.lng and p1.lat <= p2.lat:
                angle = angle
            elif p1.lng > p2.lng:
                angle += 180
            else:
                angle += 360
        return angle

    @staticmethod
    def intersection_angle(p1, p2, p3, p4):
        angle1 = Angle.horizontal_angle(p1, p2)
        angle2 = Angle.horizontal_angle(p3, p4)
        if abs(angle1 - angle2) > 180:
            return 360 - abs(angle1 - angle2)
        else:
            return abs(angle1 - angle2)
