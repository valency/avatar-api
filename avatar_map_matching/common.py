from avatar_core.geometry import *


def find_candidates_from_road(road_network, point):
    candidates = []
    rids = []
    unit_lat = (road_network.pmax.lat - road_network.pmin.lat) / road_network.grid_lat_count
    unit_lng = (road_network.pmax.lng - road_network.pmin.lng) / road_network.grid_lng_count
    if point.lat < road_network.pmin.lat or point.lng < road_network.pmin.lng or point.lat > road_network.pmax.lat or point.lng > road_network.pmax.lng:
        print "Warning: point out of bound:", point, road_network.pmin, road_network.pmax
    else:
        lat_index = int((point.lat - road_network.pmin.lat) / unit_lat)
        lng_index = int((point.lng - road_network.pmin.lng) / unit_lng)
        for i in range(lat_index - 1 if lat_index > 0 else 0, lat_index + 2 if lat_index + 1 < road_network.grid_lat_count else road_network.grid_lat_count):
            for j in range(lng_index - 1 if lng_index > 0 else 0, lng_index + 2 if lng_index + 1 < road_network.grid_lng_count else road_network.grid_lng_count):
                grid = road_network.grid_cells.get(lat_id=i, lng_id=j)
                for road in grid.roads.all():
                    candidate = Distance.point_map_to_road(point, road)
                    candidate["rid"] = road.id
                    if road.id not in rids:
                        candidates.append(candidate)
                        rids.append(road.id)
        candidates.sort(key=lambda x: x["dist"])
    print "# of Candidates = " + str(len(candidates))
    return candidates
