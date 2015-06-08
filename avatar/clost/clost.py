import os
import sys
import json
import copy
import rtree
from rtree import index
import time
import datetime
#from avatar.models import *
#from ..models import Yohoho
sys.path.insert(0,'..')
import avatar.models
from django.db.models import Count

#find the minimum/maximum of longitude and latitude
#as well as the range
#in the test.json, lat stands for longitude, lng for latitude
#savedir='/home/pfc/Downloads/data/test.json'# this should be an input of this function
#idx=index.Index()
#*******************************************#*******************************************
#*******************************************#*******************************************
#*******************************************#*******************************************
#list_traj=[]
#*******************************************#*******************************************
#*******************************************#*******************************************
#*******************************************#*******************************************

class RSpanningTree:
    @staticmethod
    def sec_to_time(initial):
    #initial comes in number of seconds, i.e., 1200 stands for 1200 seconds
    #20 minutes
        hour=int(initial/3600)
        minute=int((initial-3600*hour)/60)
        second=initial-3600*hour-60*minute
        return hour,minute,second
    @staticmethod
    def time_to_sec(timeslot):
    #timeslot comes in [hour,minute,second], transform it to number of seconds
        time=timeslot[0]*3600+timeslot[1]*60+timeslot[2]
        return time

    @staticmethod
    def timeplus(initial, difference):
    #two input both in form [hour,minute,second]
    #we add them together and output also [hour,minute,second]
        add1=RSpanningTree.time_to_sec(initial)
        add2=RSpanningTree.time_to_sec(difference)
        result=add1+add2
        rresult=RSpanningTree.sec_to_time(result)
        return rresult

    @staticmethod
    def time_split(timeslot):
    #input a string in form '2009-09-01 01:03:40'
    #output a list: ([2009, 9, 1], [1, 3, 40])
        t1=timeslot.split(' ')
        time1=t1[0].split('-')
        time2=t1[1].split(':')
        day=[int(x) for x in time1]
        moment=[int(x) for x in time2]
        return day,moment

    @staticmethod
    def date_plus(initial, difference):
    #input is initial~[year, month, date],difference~number of days
    #output is also [year, month, date]
    #don't consider that Feb of 2012 has 29 days
        mon_day=[0,31,28,31,30,31,30,31,31,30,31,30,31]#mon_day[1]=31
        temp=copy.copy(initial[2])+difference
        print 'difference',difference
    #print 'temp in date_plus',temp
    #print mon_day[initial[1]]
        while temp>mon_day[initial[1]]:#check if the additional days cross a month
            temp2=mon_day[initial[1]]
            print 'temp2 in date_plus while temp>mon_day',temp2
            print 'initial[2]',initial[2]
            temp=temp-temp2
            print 'temp after minus',temp
            if initial[1]==12:#we need to add 1 month, before we should know if need
                initial[0]=initial[0]+1#add 1 year
            initial[1]=(initial[1]+1)%12#add 1 month
            if initial[1]==0:
                initial[1]=12
        initial[2]=copy.copy(temp)#after adding year and month(if needed), set value of day
    #print initial
        return initial


#*******************************************#*******************************************
#*******************************************#*******************************************
#*******************************************#*******************************************
    @staticmethod
    def createfile_daytime(node, start_time, time_reso, end_time):
        year=copy.copy(start_time[0])
        month=copy.copy(start_time[1])
        day=copy.copy(start_time[2])
        e0=copy.copy(end_time[0])
        e1=copy.copy(end_time[1])
        e2=copy.copy(end_time[2])
        t_id=0
        #return [year,month,day,e0,e1,e2]
        while start_time[1]<=e1:
            if start_time[0]>e0:
                    break
            while start_time[2]<=e2:
                if start_time[0]>e0:
                    break
                if start_time[1]>e1:
                    break
                tt_id=copy.copy(t_id)
                year=copy.copy(start_time[0])
                month=copy.copy(start_time[1])
                day=copy.copy(start_time[2])
                #return start_time
                temp_s_time=str(year)+'-'+str(month)+'-'+str(day)+' 00:00:00'
                temp_e_time=str(year)+'-'+str(month)+'-'+str(day)+' 23:59:59'
                #return temp_e_time, temp_s_time
                temp_node=avatar.models.Yohoho(id=copy.copy(node.id)+'-'+str(tt_id), s_time=copy.copy(temp_s_time),
                                 e_time=copy.copy(temp_e_time), s_lat=copy.copy(node.s_lat), s_lng=copy.copy(node.s_lng),
                                               e_lat=copy.copy(node.e_lat), e_lng=copy.copy(node.e_lng))
                #return temp_e_time, temp_s_time
                temp_node.save()
                #return temp_node.s_time, time_reso
                t=RSpanningTree.createfile_second(temp_node, time_reso)
                return t
                temp_node.save()
                node.pointer.add(temp_node)
                node.save()
                temp=copy.copy(start_time)
                #return temp
                kao=RSpanningTree.date_plus(temp,1)
                print start_time
                start_time=copy.copy(kao)
                #*************for test******************
                #return start_time, kao
                #*************for test******************
            #createfile_second(filename,time_reso)
            if start_time[1]==e1:
                if start_time[2]>e2:
                    break
            t_id=t_id+1
        #return [year,month,day,e0,e1,e2]
        return start_time


#*******************************************#*******************************************
#*******************************************#*******************************************
#*******************************************#*******************************************



#*******************************************#*******************************************
#*******************************************#*******************************************
#*******************************************#*******************************************
    @staticmethod
    def createfile_second(temp_node,time_reso):
    #num_month=end_time[1]-start_time[1]+1#how many months in the time slot
    #year=start_time[0]
    #month=start_time[1]
    #day=start_time[2]
    #filename=filedir+'\\'+str(year)+'-'+str(month)+'-'+str(day)
    #if not os.path.isdir(filename):
    #    os.mkdir(filename)
        start_time=[0,0,0]
        end_time=[23,59,59]
        t_raw1=str(temp_node.s_time).split('+')
        t_raw2=copy.copy(t_raw1[0])
        raw_time = RSpanningTree.time_split(t_raw2)
        raw_time[1][0]=0
        raw_time[1][1]=0
        raw_time[1][2]=0
        time_reso=RSpanningTree.sec_to_time(time_reso)
        s=0
        e=RSpanningTree.time_to_sec(end_time)
        i=0
        #return s,end_time
        p=temp_node.pointer.all()
        #return i, len(p)
        t_r=RSpanningTree.time_to_sec(time_reso)
        t_s=RSpanningTree.time_to_sec(start_time)
        size=int(e/t_r)
        j=0
        #return t_r, size
        while i<size:
            hour=copy.copy(start_time[0])
            minute=copy.copy(start_time[1])
            sec=copy.copy(start_time[2])
            year=copy.copy(raw_time[0][0])
            month=copy.copy(raw_time[0][1])
            day=copy.copy(raw_time[0][2])
            temp_s_time=str(copy.copy(year))+'-'+str(copy.copy(month))+'-'+str(copy.copy(day))+' '+str(hour)+':'+str(minute)+':'+str(sec)
            #return temp_s_time






            #return t_r, t_s, e
            i=copy.copy(i)+1
            #if j==100:
                #return 'i='+str(i)
            tt_s=copy.copy(t_s)
            #if j==200:
                #return 'tt_s='+str(tt_s)
            t_s=tt_s+t_r
            #if j==100:
                #return 't_r='+str(t_r)
            #if j==10:
                #return 't_s='+str(t_s)
            #if j==1:
            #    return t_s

        #if not os.path.isdir(filename):
            #os.mkdir(filename)
        #notedir=filename+'\\'+str(hour)+'-'+str(minute)+'-'+str(sec)+'.txt'
        #file_note=open(notedir,'w')
        #file_note.write('')
        #file_note.close()

            if t_s<=e:
                start_time=RSpanningTree.timeplus(start_time,time_reso)
                s=RSpanningTree.time_to_sec(start_time)
                hour=copy.copy(start_time[0])
                minute=copy.copy(start_time[1])
                sec=copy.copy(start_time[2])
            #return t_r, t_s

            else:
                hour='23'
                minute='59'
                sec='59'
            #return t_r, t_s
            temp_e_time=str(copy.copy(year))+'-'+str(copy.copy(month))+'-'+str(copy.copy(day))+' '+str(hour)+':'+str(minute)+':'+str(sec)
            temp_temp_node=avatar.models.Yohoho(id=copy.copy(temp_node.id)+'-'+str(i), s_time=copy.copy(temp_s_time),e_time=copy.copy(temp_e_time),
                                  s_lat=copy.copy(temp_node.s_lat), s_lng=copy.copy(temp_node.s_lng),
                                                e_lat=copy.copy(temp_node.e_lat), e_lng=copy.copy(temp_node.e_lng))
            temp_temp_node.save()
            #return t_r, t_s
            #return temp_temp_node.e_time
            temp_node.pointer.add(temp_temp_node)
            temp_node.save()
            p=temp_node.pointer.all()
            #return p[0].e_time
            #i=i+1
            j=copy.copy(j)+1
            s=s+t_s
            #return t_r, t_s
        p=temp_node.pointer.all()
        return i, p[20].s_time

#*******************************************#*******************************************
#*******************************************#*******************************************
#*******************************************#*******************************************


#*******************************************#*******************************************
#*******************************************#*******************************************
#*******************************************#*******************************************
    @staticmethod
    def date_compare(date1,date2):
        mon_day=[0,31,28,31,30,31,30,31,31,30,31,30,31]#mon_day[1]=31
        mon_day2=[0,31,29,31,30,31,30,31,31,30,31,30,31]
        year_day=[365,366]
        year1=date1[0]
        month1=date1[1]
        day1=date1[2]
        year2=date2[0]
        month2=date2[1]
        day2=date2[2]
        dif=0
        anti_dif=day2
        dif_year=year1-year2
        while year2<year1:
        #dif=dif+mon_day[month2]-day2
        #if month2<12:
        #    month2=month2+1
        #else:
        #    year2=year2+1
        #    month2=1
        #    continue
            while month2<=12:
                dif=dif+mon_day[month2]
                month2=month2+1
            year2=year2+1
            month2=1
        while month2<month1:
            dif=dif+mon_day[month2]
            month2=month2+1
        dif=dif+day1-anti_dif
        return dif
#*******************************************#*******************************************
#*******************************************#*******************************************
#*******************************************#*******************************************




    @staticmethod
    def find(list_traj):
        minlat = 0
        minlng = 0
        maxlng = 0
        maxlat = 0
        mindate = []
        maxdate = []
        i = 0
        #num_traj = list.count(list_traj)
        num_traj = len(list_traj)
        while i<num_traj:
        #while list_traj[i] is not None:
            s = list_traj[i]
            j = 0
            #num_trace = s.trace.objects.count()  # number of traces in this trajectory
            num_trace = 1
            while j < num_trace:
                #s_trace = s.trace[j]
                s_trace = s.trace
                #num_sample = s_trace.p.objects.count()  # number of sample points in this trace
                set_sample = s_trace.p.all()
                #num_sample = s_trace.p.count
                num_sample = len(set_sample)
                k=0
                while k<num_sample:
                    #lat=float(s_trace.p[k].p.lat)
                    #lng=float(s_trace.p[k].p.lng)
                    lat=float(set_sample[k].p.lat)
                    lng=float(set_sample[k].p.lng)
                    t_raw1=str(set_sample[k].t).split('+')
                    t_raw2=copy.copy(t_raw1[0])
                    raw_time = RSpanningTree.time_split(t_raw2)
                    #raw_time = RSpanningTree.time_split(set_sample[k].t)
                    k=k+1
                    if i==0:
                        minlat = lat
                        minlng = lng
                        maxlat = lat
                        maxlng = lng
                        mindate = copy.copy(raw_time[0])
                        maxdate = copy.copy(raw_time[0])
                    #i = i + 1
                    if lat < minlat:
                        minlat = lat
                    if lat > maxlat:
                        maxlat = lat
                    if lng < minlng:
                        minlng = lng
                    if lng > maxlng:
                        maxlng = lng
                    if raw_time[0][1] < mindate[1]:
                        mindate = copy.copy(raw_time[0])
                    elif raw_time[0][1] == mindate[1]:
                        if raw_time[0][2] < mindate[2]:
                            mindate = copy.copy(raw_time[0])
                    if raw_time[0][1] > maxdate[1]:
                        maxdate = copy.copy(raw_time[0])
                    elif raw_time[0][1] == maxdate[1]:
                        if raw_time[0][2] > maxdate[2]:
                            maxdate = copy.copy(raw_time[0])
                j=j+1
            i=i+1


        return minlat, maxlat, minlng, maxlng, mindate, maxdate


    @staticmethod
    def addtofolder(root, list_traj, lng_start, lng_round, lat_start, lat_round, lng_reso, lat_reso, t_reso,
                    num_lat_grid):
        i = 0
        num_traj = len(list_traj)
        while i<num_traj:
        #while list_traj[i] is not None:
            s = list_traj[i]
            j = 0
            #num_trace = s.trace.count()  # number of traces in this trajectory
            num_trace = 1
            temp=[s.id, s.taxi]
            ttemp=copy.copy(temp)
            root.ls_traj.append(ttemp)#save this traj to the tree5
            root.save()
            while j < num_trace:
                #s_trace = s.trace[j]
                s_trace = s.trace
                set_sample = s_trace.p.all()
                #num_sample = s_trace.p.count()  # number of sample points in this trace
                num_sample = len(set_sample)
                k=0
                while k<num_sample:
                    #lat=float(s_trace.p[k].p.lat)
                    #lng=float(s_trace.p[k].p.lng)
                    lat=float(set_sample[k].p.lat)
                    lng=float(set_sample[k].p.lng)
                    lat = int(lat * float(lat_round))
                    lng = int(lng * float(lng_round))
                    t_raw1=str(set_sample[k].t).split('+')
                    t_raw2=copy.copy(t_raw1[0])
                    raw_time = RSpanningTree.time_split(t_raw2)
                    #raw_time = RSpanningTree.time_split(set_sample[k].t)#the time when this sample is taken
                    k=k+1
                    lng_incre_unit = lng_reso * lng_round
                    lat_incre_unit = lat_reso * lat_round

                    lng_index = int((lng - lng_start) / lng_incre_unit)
                    lat_index = int((lat - lat_start) / lat_incre_unit)
                    count = lng_index + lat_index * (num_lat_grid + 1)
                    root.pointer[count].ls_traj.append(ttemp)
                    root.save()
                    spa_grid=root.pointer[count]#the spatial grid that this sample belongs to
                    t_raw1=str(spa_grid.s_time).split('+')
                    t_raw2=copy.copy(t_raw1[0])
                    raw_time_min = RSpanningTree.time_split(t_raw2)
                    #raw_time_min=RSpanningTree.time_split(spa_grid.s_time)
                    dif=RSpanningTree.date_compare(raw_time[0],raw_time_min[0])
                    spa_grid.pointer[dif].ls_traj.append(ttemp)#the date grid that this sample belongs to
                    spa_grid.save()
                    date_grid=spa_grid.pointer[dif]#the date grid that this sample belongs to
                    t1=RSpanningTree.time_to_sec(raw_time[1])
                    t2=RSpanningTree.time_to_sec(raw_time_min[1])
                    dif_sec=t1-t2
                    sec_index=int(dif_sec/t_reso)
                    date_grid.pointer[sec_index].ls_traj.append(ttemp)
                    date_grid.save()


                j=j+1
            i=i+1


#*******************************************#*******************************************
#*******************************************#*******************************************
#*******************************************#*******************************************



#*******************************************#*******************************************
#*******************************************#*******************************************
#*******************************************#*******************************************
    @staticmethod
    def create_tree(list_traj):
        [minlng,maxlng,minlat,maxlat,mindate,maxdate]=RSpanningTree.find(list_traj)#list_traj is a list of Trajectory
#*******************************************#*******************************************
#*******************************************#*******************************************
#*******************************************#*******************************************
        latrange=maxlat-minlat
        lngrange=maxlng-minlng
#set the resolution of division of space and time
        reso_lat=0.02
        reso_lng=0.05#resolution of dividing the whole areas
#resolution should also be an input of this function

#for convenience we need to round lat and lng to integers, we need to know
#how much should a raw lat/lng multiplies
        i=0
        temp_lng=reso_lng
        temp_lat=reso_lat
        lat_round=1
        lng_round=1
        while temp_lng<1:
            temp_lng=temp_lng*10
            lng_round=lng_round*10
        while temp_lat<1:
            temp_lat=temp_lat*10
            lat_round=lat_round*10
    
        reso_time=1635#in seconds
#resolution should also be an input of this function

#get the number of spatial grids
        num_lat_grid=int(latrange/reso_lat)+1
        num_lng_grid=int(lngrange/reso_lng)+1#number of grids after division
        print num_lng_grid
        print num_lat_grid
        print 'before',mindate,maxdate
        print 'after',mindate,maxdate

        i=0
        j=0
        lng_start=int(minlng*lng_round)
        lat_start=int(minlat*lat_round)
        lng_end=int(lng_start+lngrange*lng_round)
        lat_end=int(lat_start+latrange*lat_round)
        print lng_start,lat_start,"\n***************************"
        lng_grid=0
        lat_grid=0
        count=0


#*******************************************#*******************************************
#*******************************************#*******************************************
#*******************************************#*******************************************
        year=str(maxdate[0])
        month=str(maxdate[1])
        day=str(maxdate[2])
        temp_maxd=copy.copy(str(year))+'-'+copy.copy(str(month))+'-'+copy.copy(str(day))+' 23:59:59'
        year=str(mindate[0])
        month=str(mindate[1])
        day=str(mindate[2])
        temp_mind=copy.copy(str(year))+'-'+copy.copy(str(month))+'-'+copy.copy(str(day))+' 00:00:00'
        #root=avatar.models.Yohoho(id='0', s_time=copy.copy(temp_mind), e_time=copy.copy(temp_maxd), s_lat=str(lat_start), e_lat=str(lat_end),
        #            s_lng=str(lng_start), e_lng=str(lng_end))
#create nodes based on spatial grids
        twidth=lng_end-lng_start
        theight=lat_end-lat_start
        rect=avatar.models.Rect(lat=lat_start,lng=lng_start,width=twidth,height=theight)
        root=avatar.models.CloST(bounding_box=rect)
        root.save()
        return root,minlng,maxlng,minlat,maxlat,mindate,maxdate
        while i<num_lng_grid:
            j=0
            while j<num_lat_grid:
                lng_grid=int(lng_start+j*reso_lng*lng_round)
                lat_grid=int(lat_start+i*reso_lat*lat_round)
                tj=j+1
                elng_grid=int(lng_start+tj*reso_lng*lng_round)
                #return root, num_lat_grid, num_lng_grid
                node=avatar.models.Yohoho(id=str(count), s_time=copy.copy(temp_mind), e_time=copy.copy(temp_maxd),
                            s_lat=str(lat_grid), s_lng=str(lng_grid), e_lat=str(lat_grid), e_lng=str(elng_grid))
                node.save()
                #return node, mindate, reso_time, maxdate
                #RSpanningTree.createfile_daytime(node,mindate,reso_time,maxdate)#in each spatial grid, create node based on time slots
                t=RSpanningTree.createfile_daytime(node,mindate,reso_time,maxdate)
                return node,t
        #restart from here
                node.save()
                root.pointer.add(node)
                root.save()
                count=count+1
                j=j+1
            i=i+1
        return root



#*******************************************#*******************************************
#*******************************************#*******************************************
#*******************************************#*******************************************

#*******************************************#*******************************************
#*******************************************#*******************************************
#*******************************************#*******************************************
        RSpanningTree.addtofolder(root,list_traj,lng_start,lng_round,lat_start,lat_round,reso_lng,reso_lat,reso_time,num_lat_grid)
        return root
#*******************************************#*******************************************
#*******************************************#*******************************************
#*******************************************#*******************************************
