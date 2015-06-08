import uuid

from rest_framework.renderers import JSONRenderer
from django.http import HttpResponse
from rest_framework import viewsets
from django.core.exceptions import ObjectDoesNotExist
#<<<<<<< HEAD
from avatar.clost.clost import RSpanningTree

from settings import Settings
from serializers import *
from .models import *
from .clost import clost
import datetime
#=======

from settings import Settings
from serializers import *
#>>>>>>> origin/master


class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json;charset=utf-8'
        super(JSONResponse, self).__init__(content, **kwargs)


class TrajectoryViewSet(viewsets.ModelViewSet):
    queryset = Trajectory.objects.all()
    serializer_class = TrajectorySerializer


class RoadViewSet(viewsets.ModelViewSet):
    queryset = Road.objects.all()
    serializer_class = RoadSerializer


class IntersectionViewSet(viewsets.ModelViewSet):
    queryset = Intersection.objects.all()
    serializer_class = IntersectionSerializer


def resp(status, content):
    return JSONResponse({"status": status, "content": content})


def add_traj_from_local_file(request):
    if 'taxi' in request.POST and 'src' in request.POST and 'header' in request.POST:
        traj = Trajectory(id=str(uuid.uuid4()), taxi=request.POST['taxi'])
        traj.save()
        try:
            traj.from_csv(Settings.CSV_UPLOAD_DIR + request.POST['src'], request.POST['taxi'], request.POST['header'].split(","))
        except IOError as e:
            return resp(500, "io error ({0}): {1}".format(e.errno, e.strerror))
        return resp(200, TrajectorySerializer(traj).data)
    else:
        return resp(500, "parameter not correct")


def get_traj_by_id(request):
    if 'id' in request.GET:
        try:
            traj = Trajectory.objects.get(id=request.GET['id'])
            return resp(200, TrajectorySerializer(traj).data)
        except ObjectDoesNotExist:
            return resp(404, "trajectory not exist")
    else:
        return resp(500, "parameter not correct")


def remove_traj_by_id(request):
    if 'id' in request.GET:
        traj = Trajectory.objects.get(id=request.GET['id'])
        traj.delete()
        return resp(200, "success")
    else:
        return resp(500, "parameter not correct")


def get_all_traj_id(request):
    return resp(200, TrajectoryListSerializer(Trajectory.objects.all(), many=True).data)
#<<<<<<< HEAD
#************************************************
class RSpanningTreeViewSet(viewsets.ModelViewSet):
    queryset = Yohoho.objects.all()#is it correct to use Yohoho.objects.all()? I mean, will queryset be the root, or all Yohoho's?
    serializer_class = RSpanningTreeSerializer
#************************************************


#************************************************
def create_index(request):
    #if 'id' in request.GET:
    #return resp(500, "parameter not correct")
    #return resp(500, "parameter not correct")
    #return idset
    traj_set= Trajectory.objects.all()
    #return resp(500, traj_set[0])
    set_sample=traj_set[0].trace.p.all()
    #raw1=str(set_sample[0].t).split('+')
    #raw_time = RSpanningTree.time_split(raw1[0])
    #raw_time[1]= [0,0,0]
    #return resp(200, raw_time)
    #return resp(200, len(set_sample))
    #return resp(200, len(traj_set))
    #traj_set2=[]
    #traj_set2.append(traj_set[3])
    #return resp(200, len(traj_set2))
    #t_raw1=str(temp_node.s_time).split('+')
    #t_raw2=copy.copy(t_raw1[0])
    #raw_time = RSpanningTree.time_split(t_raw2)

    if len(traj_set)==0:
        return resp(500, "parameter not correct")
    else:
        #ls_traj=[]
        #i=0
        #for traj in traj_set:
            #traj = Trajectory.objects.get(taxi=id)
            #ls_traj.append(traj)
        #return resp(500, TrajectorySerializer(traj_set[1]).data)
        #return resp(200, len(traj_set))
        root=RSpanningTree.create_tree(traj_set)
        r=root[1:]
        return resp(200, r)
        point_set=root.pointer.all()
        p=point_set
        #return resp(200, point_set[])
        return resp(200, [[p[0].id, p[0].e_time, p[0].s_lng, p[0].s_lat, p[0].e_lng, p[0].e_lat],['***'],
                          [p[1].id, p[1].e_time, p[1].s_lng, p[1].s_lat, p[1].e_lng, p[1].e_lat]])
        point_set=root.pointer.all()#set of spatial grids
        p=point_set
        p_point_set=point_set[0].pointer.all()#set of date grids
        pp=p_point_set
        p_p_point_set=p_point_set[0].pointer.all()#set of sec grids
        ppp=p_p_point_set
        p_p_p_point_set=p_point_set[0].pointer.all()
        pppp=p_p_p_point_set
        #point_set[0].s_time
        #return resp(200, len(p_p_p_point_set))
        #return resp(200, point_set[].s_lat)
        return resp(200, [[p[0].s_time, p[0].e_time, p[0].s_lng, p[0].s_lat, p[0].e_lng, p[0].e_lat],['***'],
                          [p[1].s_time, p[1].e_time, p[1].s_lng, p[1].s_lat, p[1].e_lng, p[1].e_lat]])
        return resp(200, RSpanningTreeSerializer(root).data)
#************************************************
#=======
#>>>>>>> origin/master
