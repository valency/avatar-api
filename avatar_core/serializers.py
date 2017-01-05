from rest_framework import serializers

from avatar_core.models import *


class PointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Point


class SampleMetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SampleMeta


class SampleSerializer(serializers.ModelSerializer):
    p = PointSerializer()
    t = serializers.DateTimeField(format="%Y-%m-%d %X")
    meta = SampleMetaSerializer(many=True)

    class Meta:
        model = Sample


class IntersectionSerializer(serializers.ModelSerializer):
    p = PointSerializer()

    class Meta:
        model = Intersection


class RoadSerializer(serializers.ModelSerializer):
    p = PointSerializer(many=True)
    intersection = IntersectionSerializer(many=True)

    class Meta:
        model = Road


class TraceSerializer(serializers.ModelSerializer):
    p = SampleSerializer(many=True)

    class Meta:
        model = Trace


class PathFragmentSerializer(serializers.ModelSerializer):
    road = RoadSerializer()

    class Meta:
        model = PathFragment


class PathSerializer(serializers.ModelSerializer):
    road = PathFragmentSerializer(many=True)

    class Meta:
        model = Path


class TrajectorySerializer(serializers.ModelSerializer):
    trace = TraceSerializer()
    path = PathSerializer()

    class Meta:
        model = Trajectory


class RectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rect


class GridCellSerializer(serializers.ModelSerializer):
    area = RectSerializer()
    roads = RoadSerializer(many=True)
    intersections = IntersectionSerializer(many=True)

    class Meta:
        model = GridCell


class RoadNetworkSerializer(serializers.ModelSerializer):
    roads = RoadSerializer(many=True)
    intersections = IntersectionSerializer(many=True)
    grid_cells = GridCellSerializer(many=True)
    pmin = PointSerializer()
    pmax = PointSerializer()

    class Meta:
        model = RoadNetwork
