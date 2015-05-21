from rest_framework import serializers

from models import *


class PointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Point
        fields = ('lat', 'lng')


class SampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sample
        fields = ('id', 'p', 't', 'speed', 'angle', 'occupy', 'meta', 'src')


class IntersectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Intersection
        fields = ('id', 'p')


class RoadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Road
        fields = ('id', 'name', 'type', 'length', 'speed', 'p', 'intersection')


class TraceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trace
        fields = ('id', 'p')


class PathFragmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PathFragment
        fields = ('road', 'p')


class PathSerializer(serializers.ModelSerializer):
    class Meta:
        model = Path
        fields = ('id', 'road')


class TrajectorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Trajectory
        fields = ('id', 'taxi', 'trace', 'path')
