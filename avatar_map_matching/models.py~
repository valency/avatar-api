from avatar_core.models import *


class ShortestPathIndex(models.Model):
    # start.id < end.id
    city = models.ForeignKey(RoadNetwork)
    start = models.ForeignKey(Intersection, related_name="start")
    end = models.ForeignKey(Intersection, related_name="end")
    path = models.ForeignKey(Path)
    length = models.IntegerField(null=True)

    def __str__(self):
        return str(self.length)

    class Meta:
        unique_together = ("city", "start", "end")


class HmmEmissionTable(models.Model):
    city = models.ForeignKey(RoadNetwork)
    traj = models.ForeignKey(Trajectory)
    table = models.TextField(max_length=65535, null=True)

    def __str__(self):
        return str(self.table)

    class Meta:
<<<<<<< HEAD
        unique_together = ("city", "traj")
=======
	unique_together = ("city", "traj")
>>>>>>> b562233098ac8e62c4e170769207445a853b5f6a


class HmmTransitionTable(models.Model):
    city = models.ForeignKey(RoadNetwork)
    traj = models.ForeignKey(Trajectory)
    table = models.TextField(max_length=65535, null=True)

    def __str__(self):
<<<<<<< HEAD
        return str(self.table)

    class Meta:
        unique_together = ("city", "traj")
=======
	return str(self.table)

    class Meta:
	unique_together = ("city", "traj")
>>>>>>> b562233098ac8e62c4e170769207445a853b5f6a
