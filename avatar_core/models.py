from django.db import models


class Point(models.Model):
    lat = models.FloatField()
    lng = models.FloatField()

    def __str__(self):
        return "(" + str(self.lat) + "," + str(self.lng) + ")"


class SampleMeta(models.Model):
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=255)

    def __str__(self):
        return str(self.key) + ": " + str(self.value)


class Sample(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    p = models.ForeignKey(Point)
    t = models.DateTimeField()
    speed = models.IntegerField(null=True)
    angle = models.IntegerField(null=True)
    occupy = models.IntegerField(null=True)
    meta = models.ManyToManyField(SampleMeta)
    src = models.IntegerField(null=True)

    def __str__(self):
        return self.id


class Intersection(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    p = models.ForeignKey(Point, null=True)

    def __str__(self):
        return self.id


class Road(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    name = models.CharField(max_length=255, null=True)
    type = models.IntegerField(null=True)
    length = models.IntegerField(null=True)
    speed = models.IntegerField(null=True)
    p = models.ManyToManyField(Point)
    intersection = models.ManyToManyField(Intersection)

    def __str__(self):
        return self.id


class Trace(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    p = models.ManyToManyField(Sample)

    def __str__(self):
        return self.id


class PathFragment(models.Model):
    road = models.ForeignKey(Road)
    p = models.TextField(max_length=65535, null=True)

    def __str__(self):
        return str(self.road)


class Path(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    road = models.ManyToManyField(PathFragment)

    def __str__(self):
        return self.id


class Trajectory(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    taxi = models.CharField(max_length=255)
    trace = models.ForeignKey(Trace, null=True)
    path = models.ForeignKey(Path, null=True)

    def __str__(self):
        return self.id


class Rect(models.Model):
    lat = models.FloatField()
    lng = models.FloatField()
    width = models.FloatField()
    height = models.FloatField()

    def __str__(self):
        return "(" + str(self.lat) + "," + str(self.lng) + "," + str(self.height) + "," + str(self.width) + ")"


class GridCell(models.Model):
    # Actual ID of the grid cell (lat count, lng count)
    lat_id = models.IntegerField()
    lng_id = models.IntegerField()
    # Bounding box of the gird cell
    area = models.ForeignKey(Rect)
    roads = models.ManyToManyField(Road)
    intersections = models.ManyToManyField(Intersection)

    def __str__(self):
        return "(" + str(self.lat_id) + "," + str(self.lng_id) + ")"


class RoadNetwork(models.Model):
    city = models.CharField(max_length=32, unique=True)
    roads = models.ManyToManyField(Road)
    intersections = models.ManyToManyField(Intersection)
    grid_cells = models.ManyToManyField(GridCell)
    grid_lat_count = models.IntegerField(null=True)
    grid_lng_count = models.IntegerField(null=True)
    pmin = models.ForeignKey(Point, related_name="pmin", null=True)
    pmax = models.ForeignKey(Point, related_name="pmax", null=True)
    graph = models.CharField(max_length=10485760, null=True)
    shortest_path_index = models.CharField(max_length=10485760, null=True)

    def __str__(self):
        return self.city
