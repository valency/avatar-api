from datetime import datetime

from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from traj_generator import *


CSV_UPLOAD_DIR = "/var/www/html/avatar/data/"


@api_view(['GET'])
def generate_trajectory(request):
    if "city" in request.GET and "traj" in request.GET and "point" in request.GET:
        city = RoadNetwork.objects.get(id=request.GET['city'])
	num_traj = int(request.GET['traj'])
	num_sample = int(request.GET['point'])
	stop_rate = 0.05
	sample_rate = 60
	# GPS error around 20m
	delta_lat = 0.0001
	delta_lng = 0.0002
	if "stop" in request.GET:
	    stop_rate = float(request.GET['stop'])
	if "sample" in request.GET:
            sample_rate = float(request.GET['sample'])
	if "lat" in request.GET:
            delta_lat = float(request.GET['lat'])
	if "lng" in request.GET:
            delta_lng = float(request.GET['lng'])
	result = traj_generator(city, num_traj, num_sample, stop_rate, sample_rate, delta_lat, delta_lng)
	print "Finished!"
	traj_id = []
#	for traj in result[0]:
#	    traj_id.append(traj.id)
#        return Response(traj_id)
	return Response(result[1])
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)
