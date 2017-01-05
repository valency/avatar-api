import json
import uuid

import numpy
from networkx.readwrite import json_graph
from sklearn.cluster import DBSCAN

from avatar_core.geometry import *
from avatar_core.models import *


def pairwise_dist(x, y):
    dlat = (y[0] - x[0]) * Distance.degrees_to_radians
    dlng = (y[1] - x[1]) * Distance.degrees_to_radians
    a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(x[0] * Distance.degrees_to_radians) * math.cos(y[0] * Distance.degrees_to_radians) * math.sin(dlng / 2) * math.sin(dlng / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    dist = Distance.earth_radius * c
    return dist


def find_clustered_intersections(intersections, eps, min_samples):
    sec_ids = []
    sec_loc = []
    for sec in intersections:
        sec_ids.append(sec.id)
        sec_loc.append([sec.p.lat, sec.p.lng])
    p_set = numpy.array(sec_loc)
    db = DBSCAN(eps=eps, min_samples=min_samples, metric=pairwise_dist).fit(p_set)
    labels = db.labels_
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
    clustered_sec = [[]] * n_clusters_
    for i in range(len(labels)):
        if labels[i] != -1:
            clustered_sec[labels[i]].append(sec_ids[i])
    return clustered_sec


def merge_intersections_by_road_network(road_network, eps, min_samples, sub_cluster_bound):
    intersections = road_network.intersections.all()
    final_clusters = []
    first_clusters = find_clustered_intersections(intersections, eps, min_samples)
    todo_clusters = []
    for cluster in first_clusters:
        if len(cluster) > min_samples * 2:
            todo_clusters.append(cluster)
        else:
            final_clusters.append(cluster)
    # If some of the clusters are too large, divide the large clusters into smaller sub clusters
    sub_eps = float(eps) * 0.5
    while sub_eps >= sub_cluster_bound:
        log("Perform DB-Scan with eps = " + str(sub_eps) + "...")
        new_clusters = []
        for cluster in todo_clusters:
            sub_secs = []
            for sec_id in cluster:
                sub_secs.append(Intersection.objects.get(id=sec_id))
            sub_clusters = find_clustered_intersections(sub_secs, sub_eps, min_samples)
            for sub_cluster in sub_clusters:
                if len(sub_cluster) > 0:
                    if len(sub_cluster) > min_samples * 2:
                        new_clusters.append(sub_cluster)
                    else:
                        final_clusters.append(sub_cluster)
        todo_clusters = new_clusters
        sub_eps *= 0.5
    # print todo_clusters
    # Save merged intersection index in cache
    merged_secs = dict()
    for cluster in final_clusters:
        lats = 0.0
        lngs = 0.0
        for sec_id in cluster:
            orig_sec = Intersection.objects.get(id=sec_id)
            lats += orig_sec.p.lat
            lngs += orig_sec.p.lng
        merged_lat = lats / len(cluster)
        merged_lng = lngs / len(cluster)
        merged_p = Point(lat=merged_lat, lng=merged_lng)
        merged_p.save()
        merged_sec = Intersection(id=str(uuid.uuid4()), p=merged_p)
        merged_sec.save()
        merged_secs[merged_sec.id] = cluster
    return merged_secs


def merge_road_segments_by_road_network(road_network, eps, min_samples, sub_cluster_bound):
    if road_network.graph is None:
        log("ERROR: Road network must have a graph!", "red")
        exit()
    graph = json_graph.node_link_graph(json.loads(road_network.graph))
    merged_secs = merge_intersections_by_road_network(road_network, eps, min_samples, sub_cluster_bound)
    # Modify graph with merged intersections
    for merged_sec_id in merged_secs:
        for orig_sec_id in merged_secs[merged_sec_id]:
            for node in graph.neighbors(orig_sec_id):
                info = graph.get_edge_data(orig_sec_id, node)
                if node != merged_sec_id:
                    if not graph.has_edge(merged_sec_id, node):
                        graph.add_edge(merged_sec_id, node, weight=info["weight"], id=info["id"])
                    else:
                        if node not in merged_secs[merged_sec_id]:
                            merged_info = graph.get_edge_data(merged_sec_id, node)
                            graph.add_edge(merged_sec_id, node, weight=info["weight"], id=merged_info["id"] + "," + info["id"])
    # Record the degree of each merged intersections to check whether it involves parallel road segments
    parallel_degree = dict()
    for merged_sec_id in merged_secs:
        parallel_degree[merged_sec_id] = graph.degree(merged_sec_id)
    # Check parallel road segments
    for edge in graph.edges():
        info = graph.get_edge_data(edge[0], edge[1])
        rid = info["id"].split(",")
        # No parallel road segments between these two intersections, degree minus 1
        if len(rid) == 1:
            if edge[0] in parallel_degree:
                parallel_degree[edge[0]] -= 1
            if edge[1] in parallel_degree:
                parallel_degree[edge[1]] -= 1
        # If there are parallel road segments, only keep the first one
        else:
            graph.remove_edge(edge[0], edge[1])
            graph.add_edge(edge[0], edge[1], weight=info["weight"], id=rid[0])
    # Remove additional nodes
    for merged_sec_id in merged_secs:
        if parallel_degree[merged_sec_id] > 0:
            for node in merged_secs[merged_sec_id]:
                graph.remove_node(node)
        else:
            graph.remove_node(merged_sec_id)
    return graph, merged_secs
