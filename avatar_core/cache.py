import json
import time

from django.utils.termcolors import colorize

from serializers import *

ROAD_NETWORK = dict()


def get_road_network_by_id(road_network_id):
    if not ROAD_NETWORK.has_key(road_network_id):
        ROAD_NETWORK[road_network_id] = create_road_network_dict(road_network_id)
    return ROAD_NETWORK[road_network_id]


def create_road_network_dict(road_network_id):
    print colorize("Creating cache for road network " + road_network_id + "...", fg="green")
    start = time.time()
    road_network = RoadNetwork.objects.get(id=road_network_id)
    road_network_data = RoadNetworkSerializer(road_network).data
    # Re-construct the road network into dictionary
    road_network_dict = dict()
    # Save all roads associated with the road network
    road_network_dict["roads"] = dict()
    for road in road_network_data["roads"]:
        road_network_dict["roads"][road["id"]] = road
    # Save all intersections associated with the road network
    road_network_dict["intersections"] = dict()
    for intersection in road_network_data["intersections"]:
        road_network_dict["intersections"][intersection["id"]] = intersection
    # Save all grid cells associated with the road network
    road_network_dict["grid_cells"] = dict()
    for grid_cell in road_network_data["grid_cells"]:
        if not road_network_dict["grid_cells"].has_key(str(grid_cell["lat_id"])):
            road_network_dict["grid_cells"][str(grid_cell["lat_id"])] = dict()
        road_network_dict["grid_cells"][str(grid_cell["lat_id"])][str(grid_cell["lng_id"])] = grid_cell
    # Save other information associated with the road network
    road_network_dict["city"] = road_network_data["city"]
    road_network_dict["grid_lat_count"] = road_network_data["grid_lat_count"]
    road_network_dict["grid_lng_count"] = road_network_data["grid_lng_count"]
    road_network_dict["pmin"] = road_network_data["pmin"]
    road_network_dict["pmax"] = road_network_data["pmax"]
    road_network_dict["graph"] = json.loads(road_network_data["graph"])
    if road_network_data["shortest_path_index"] is not None:
        road_network_dict["shortest_path_index"] = json.loads(road_network_data["shortest_path_index"])
    else:
        road_network_dict["shortest_path_index"] = None
    end = time.time()
    print "Saving road network to memory takes " + str(end - start) + " seconds..."
    return road_network_dict
