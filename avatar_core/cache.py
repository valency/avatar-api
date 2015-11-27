import json

from django.core.cache import cache
from django.utils.termcolors import colorize

from serializers import *


def get_road_network_by_id(road_network_id):
    road_network = cache.get("avatar_road_network_" + road_network_id)
    if road_network is not None:
        return road_network
    else:
        print colorize("Cache for road network " + str(road_network_id) + " is missing, now creating...", fg="green")
        return create_cache_for_road_network(road_network_id)


def create_cache_for_road_network(road_network_id):
    print colorize("Creating cache for road network " + str(road_network_id) + "...", fg="green")
    road_network = RoadNetwork.objects.get(id=road_network_id)
    road_network_data = RoadNetworkSerializer(road_network).data
    # Re-construct the road network into a dictionary
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
        if not road_network_dict["grid_cells"].has_key(grid_cell["lat_id"]):
            road_network_dict["grid_cells"][grid_cell["lat_id"]] = dict()
        road_network_dict["grid_cells"][grid_cell["lat_id"]][grid_cell["lng_id"]] = grid_cell
    # Save other information associated with the road network
    road_network_dict["grid_lat_count"] = road_network_data["grid_lat_count"]
    road_network_dict["grid_lng_count"] = road_network_data["grid_lng_count"]
    road_network_dict["pmin"] = road_network_data["pmin"]
    road_network_dict["pmax"] = road_network_data["pmax"]
    road_network_dict["graph"] = json.loads(road_network_data["graph"])
    # Write the road network into memory cache
    road_network_str = json.dumps(road_network_dict)
    cache_name = "avatar_road_network_" + str(road_network_id)
    cache.set(cache_name, road_network_str)
    return road_network_str
