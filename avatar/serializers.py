from rest_framework import serializers

from models import *


class PointSerializer(serializers.Serializer):
    class Meta:
        model = Point
        fields = ('lat', 'lng')


class SampleSerializer(serializers.Serializer):
    class Meta:
        model = Sample
        fields = ('id', 'p', 't', 'speed', 'angle', 'occupy', 'meta', 'src')


class IntersectionSerializer(serializers.Serializer):
    class Meta:
        model = Intersection
        fields = ('id', 'p')


class RoadSerializer(serializers.Serializer):
    class Meta:
        model = Road
        fields = ('id', 'name', 'type', 'length', 'speed', 'p', 'intersection')


class TraceSerializer(serializers.Serializer):
    class Meta:
        model = Trace
        fields = ('id', 'p')


class PathFragmentSerializer(serializers.Serializer):
    class Meta:
        model = PathFragment
        fields = ('road', 'p')


class PathSerializer(serializers.Serializer):
    class Meta:
        model = Path
        fields = ('id', 'road')


class TrajectorySerializer(serializers.Serializer):
    class Meta:
        model = Trajectory
        fields = ('id', 'taxi', 'trace', 'path')
