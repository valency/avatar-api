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
