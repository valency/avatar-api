from rest_framework import serializers

from avatar_core.models import *


class PointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Point
        fields = '__all__'


class SampleMetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SampleMeta
        fields = '__all__'


class SampleSerializer(serializers.ModelSerializer):
    p = PointSerializer()
    t = serializers.DateTimeField(format="%Y-%m-%d %X")
    meta = SampleMetaSerializer(many=True)

    class Meta:
        model = Sample
        fields = '__all__'


class IntersectionSerializer(serializers.ModelSerializer):
    p = PointSerializer()

    class Meta:
        model = Intersection
        fields = '__all__'


class RoadSerializer(serializers.ModelSerializer):
    p = PointSerializer(many=True)
    intersection = IntersectionSerializer(many=True)

    class Meta:
        model = Road
        fields = '__all__'


class TraceSerializer(serializers.ModelSerializer):
    p = SampleSerializer(many=True)

    class Meta:
        model = Trace
        fields = '__all__'


class PathFragmentSerializer(serializers.ModelSerializer):
    road = RoadSerializer()

    class Meta:
        model = PathFragment
        fields = '__all__'


class PathSerializer(serializers.ModelSerializer):
    road = PathFragmentSerializer(many=True)

    class Meta:
        model = Path
        fields = '__all__'


class TrajectorySerializer(serializers.ModelSerializer):
    trace = TraceSerializer()
    path = PathSerializer()

    class Meta:
        model = Trajectory
        fields = '__all__'


class RectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rect
        fields = '__all__'


class GridCellSerializer(serializers.ModelSerializer):
    area = RectSerializer()
    roads = RoadSerializer(many=True)
    intersections = IntersectionSerializer(many=True)

    class Meta:
        model = GridCell
        fields = '__all__'


class RoadNetworkSerializer(serializers.ModelSerializer):
    roads = RoadSerializer(many=True)
    intersections = IntersectionSerializer(many=True)
    grid_cells = GridCellSerializer(many=True)
    pmin = PointSerializer()
    pmax = PointSerializer()

    class Meta:
        model = RoadNetwork
        fields = '__all__'
