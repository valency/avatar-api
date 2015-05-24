import csv
import datetime

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
    id = models.CharField(max_length=36, primary_key=True)
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

    def from_csv(self, src, header):
        trace = Trace(id=self.id)
        trace.save()
        try:
            f = open(src, "rb")
            reader = csv.reader(f)
            for row in reader:
                try:
                    sampleid = row[header.index("id")]
                    p = Point(lat=float(row[header.index("lat")]), lng=float(row[header.index("lng")]))
                    p.save()
                    t = datetime.datetime.strptime(row[header.index("t")], "%Y-%m-%d %H:%M:%S")
                    speed = int(row[header.index("speed")])
                    angle = int(row[header.index("angle")])
                    occupy = int(row[header.index("occupy")])
                    sample = Sample(id=sampleid, p=p, t=t, speed=speed, angle=angle, occupy=occupy, src=0)
                    sample.save()
                    trace.p.add(sample)
                except TypeError:
                    continue
            f.close()
        except IOError:
            return False
        trace.save()
        self.trace = trace
        self.path = None
        self.save()
        return True
