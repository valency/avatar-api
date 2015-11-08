from avatar_core.models import *
from avatar_user.models import *


class ShortestPathIndex(models.Model):
    # start.id < end.id
    city = models.ForeignKey(RoadNetwork)
    start = models.ForeignKey(Intersection, related_name="start")
    end = models.ForeignKey(Intersection, related_name="end")
    path = models.ForeignKey(Path, null=True)
    length = models.IntegerField(null=True)

    def __str__(self):
        return str(self.length)

    class Meta:
        unique_together = ("city", "start", "end")


class HmmEmissionTable(models.Model):
    city = models.ForeignKey(RoadNetwork)
    traj = models.ForeignKey(Trajectory)
    candidate = models.TextField(max_length=65535, null=True)
    table = models.TextField(max_length=65535, null=True)

    def __str__(self):
        return str(self.table)

    class Meta:
        unique_together = ("city", "traj")


class HmmTransitionTable(models.Model):
    city = models.ForeignKey(RoadNetwork)
    traj = models.ForeignKey(Trajectory)
    table = models.TextField(max_length=65535, null=True)

    def __str__(self):
        return str(self.table)

    class Meta:
        unique_together = ("city", "traj")


class HmmPath(models.Model):
    city = models.ForeignKey(RoadNetwork)
    traj = models.ForeignKey(Trajectory)
    path = models.ForeignKey(Path, null=True)

    def __str__(self):
        return str(self.path.id)

    class Meta:
        unique_together = ("city", "traj")


class HmmPathIndex(models.Model):
    city = models.ForeignKey(RoadNetwork)
    traj = models.ForeignKey(Trajectory)
    index = models.TextField(max_length=65535, null=True)

    def __str__(self):
        return str(self.index)

    class Meta:
        unique_together = ("city", "traj")


class Action(models.Model):
    point = models.ForeignKey(Sample)
    road = models.ForeignKey(Road)

    def __str__(self):
        return str(self.point.id) + ":" + str(self.road.id)


class UserActionHistory(models.Model):
    user = models.ForeignKey(Account)
    traj = models.ForeignKey(Trajectory)
    action = models.ManyToManyField(Action)

    def __str__(self):
        return str(self.user.id) + "," + str(self.traj.id)

    class Meta:
        unique_together = ("user", "traj")
