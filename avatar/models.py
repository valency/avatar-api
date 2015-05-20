from django.db import models

# --- Trajectory Related --- #

class Point(models.Model):
    lat = models.FloatField()
    lng = models.FloatField()

    def __str__(self):
        return "(" + str(self.lat) + "," + str(self.lng) + ")"


class Sample(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    p = models.ForeignKey(Point)
    t = models.DateTimeField()
    speed = models.IntegerField()
    angle = models.IntegerField()
    occupy = models.IntegerField()
    meta = models.CharField()
    src = models.IntegerField()

    def __str__(self):
        return self.id


class Intersection(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    p = models.ForeignKey(Point)

    def __str__(self):
        return self.id


class Road(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    name = models.CharField()
    type = models.IntegerField()
    length = models.IntegerField()
    speed = models.IntegerField()
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
    rid = models.ForeignKey(Road.id)
    p = models.CharField()

    def __str__(self):
        return self.rid


class Path(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    road = models.ManyToManyField(PathFragment)

    def __str__(self):
        return self.id


class Trajectory(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    taxi = models.CharField()
    trace = models.ForeignKey(Trace)
    path = models.ForeignKey(Path)

    def __str__(self):
        return self.id
