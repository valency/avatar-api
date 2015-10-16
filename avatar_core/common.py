from models import *
import networkx as nx

def build_road_network_graph(road_network):
    graph = nx.Graph()
    for road in road_network.roads.all():
	intersections = road.intersection.all()
	graph.add_edge(intersections[0].id, intersections[1].id, weight=road.length, id=road.id)
    return graph
