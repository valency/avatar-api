from rest_framework import serializers

from models import *


class PointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Point
        fields = ('lat', 'lng')


class SampleMetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SampleMeta
        fields = ('key', 'value')


class SampleSerializer(serializers.ModelSerializer):
    p = PointSerializer()
    t = serializers.DateTimeField(format="%Y-%m-%d %X")
    meta = SampleMetaSerializer(many=True)

    class Meta:
        model = Sample
        fields = ('id', 'p', 't', 'speed', 'angle', 'occupy', 'meta', 'src')


class IntersectionSerializer(serializers.ModelSerializer):
    p = PointSerializer()

    class Meta:
        model = Intersection
        fields = ('id', 'p')


class RoadSerializer(serializers.ModelSerializer):
    p = PointSerializer(many=True)
    intersection = IntersectionSerializer(many=True)

    class Meta:
        model = Road
        fields = ('id', 'name', 'type', 'length', 'speed', 'p', 'intersection')


class TraceSerializer(serializers.ModelSerializer):
    p = SampleSerializer(many=True)

    class Meta:
        model = Trace
        fields = ('id', 'p')


class PathFragmentSerializer(serializers.ModelSerializer):
    road = RoadSerializer()

    class Meta:
        model = PathFragment
        fields = ('road', 'p')


class PathSerializer(serializers.ModelSerializer):
    road = PathFragmentSerializer(many=True)

    class Meta:
        model = Path
        fields = ('id', 'road')


class TrajectorySerializer(serializers.ModelSerializer):
    trace = TraceSerializer()
    path = PathSerializer()

    class Meta:
        model = Trajectory
        fields = ('id', 'taxi', 'trace', 'path')


class TrajectoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trajectory
        fields = ('id', 'taxi', 'trace', 'path')
