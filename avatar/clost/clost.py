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
                    lat=copy.copy(float(set_sample[k].p.lat))
                    lng=copy.copy(float(set_sample[k].p.lng))
                    t_raw1=copy.copy(str(set_sample[k].t).split('+'))
                    t_raw2=copy.copy(t_raw1[0])
                    raw_time = copy.copy(RSpanningTree.time_split(t_raw2))
                    #return lat,lng
                    #raw_time = RSpanningTree.time_split(set_sample[k].t)
                    if k==0:
                        if i==0:
                            minlat = copy.copy(lat)
                            minlng = copy.copy(lng)
                            maxlat = copy.copy(lat)
                            maxlng = copy.copy(lng)
                            mindate = copy.copy(raw_time[0])
                            maxdate = copy.copy(raw_time[0])
                        #if k==18:
                    #i = i + 1
                    #if k==18:
                        #return minlng,minlat
                    k=k+1
                    if lat < minlat:
                        minlat = copy.copy(lat)
                    if lat > maxlat:
                        maxlat = copy.copy(lat)
                    if lng < minlng:
                        minlng = copy.copy(lng)
                    if lng > maxlng:
                        maxlng = copy.copy(lng)
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
                    #k=k+1
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
            s.save()
            j = 0
            #num_trace = s.trace.count()  # number of traces in this trajectory
            num_trace = 1
            temp=[s.id, s.taxi]
            temp=s
            temp.save()
            ttemp=copy.copy(temp)
            ttemp.save()
            root.ls_traj.append(ttemp)#save this traj to the tree5
            #root.ls_traj.add(ttemp)
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
    def inserttotree(root, traj, sample, thr):
        if root.occupancy<thr:
        #if root.haschild==0:
            #root.ls_traj.append([traj_id,taxi])
            root.ls_traj.add(traj)
            root.save()
            #root.ls_sample.append(sample)
            root.ls_sample.add(sample)
            root.save()
            root.occupancy=copy.copy(root.occupancy)+1
            root.save()
            return
        elif root.haschild==0:
            init_rect=root.bounding_box
            ls_lat=[]#save the lattitude of every sample saved in this node
            ls_lng=[]
            ls_sample=copy.copy(root.ls_sample.all())
            length=len(ls_sample)
            i=0
            while i<length:
                ls_lng.append(ls_sample[i].p.lng)
                ls_lat.append(ls_sample[i].p.lat)
                i=i+1
        #else:#if this node has been full
            sort_ls_lat=sorted(ls_lat)
            id_lat1=int(thr/2)
            t_id_lat1=2*id_lat1
            if t_id_lat1==thr:#thr is even
                id_lat2=copy.copy(id_lat1)
                id_lat1=copy.copy(id_lat2)-1
            else:#thr is odd
                id_lat2=copy.copy(id_lat1)
                id_lat1=copy.copy(id_lat2)
            lat_axis=(sort_ls_lat[id_lat1]+sort_ls_lat[id_lat2])/2
            ind=0
            ls1=[]
            ls2=[]
            subls_lng1=[]
            subls_lng2=[]
            count1=0
            count2=0
            while ind<thr:
                if ls_sample[ind].p.lat<lat_axis:
                    ls1.append(ls_sample[ind])
                    subls_lng1.append(ls_sample[ind].p.lng)
                    count1=copy.copy(count1)+1
                else:
                    ls2.append(ls_sample[ind])
                    subls_lng2.append(ls_sample[ind].p.lng)
                    count2=copy.copy(count2)+1
                ind=ind+1
            sort_subls_lng1=sorted(subls_lng1)
            sort_subls_lng2=sorted(subls_lng2)
            if count1==0:
                id_lng11=0
                id_lng12=0
                lng_axis1=init_rect.lng+init_rect.width/2
            elif count1==1:
                id_lng11=0
                id_lng12=0
                lng_axis1=(sort_subls_lng1[id_lng11]+sort_subls_lng1[id_lng12])/2
            elif count1%2==0:#if count1 is even
                id_lng12=int(count1/2)
                id_lng11=copy.copy(id_lng12)-1
                lng_axis1=(sort_subls_lng1[id_lng11]+sort_subls_lng1[id_lng12])/2
            else:
                id_lng12=int(count1/2)
                id_lng11=copy.copy(id_lng12)
                lng_axis1=(sort_subls_lng1[id_lng11]+sort_subls_lng1[id_lng12])/2
            #if id_lng11>=len(sort_subls_lng1):
            #    return 'id_lng11 too long'
            #elif id_lng12>=len(sort_subls_lng1):
            #    return 'id_lng12 too long'
            #elif id_lng12<0:
            #    return 'id_lng12<0'
            #elif id_lng11<0:
            #    return 'id_lng11<0'

            if count2==0:
                id_lng21=0
                id_lng22=0
                lng_axis2=init_rect.lng+init_rect.width/2
            elif count2==1:
                id_lng21=0
                id_lng22=1
                lng_axis2=(sort_subls_lng2[id_lng21]+sort_subls_lng2[id_lng22])/2
            elif count2%2==0:#if count1 is even
                id_lng22=int(count2/2)
                id_lng21=copy.copy(id_lng22)-1
                lng_axis2=(sort_subls_lng2[id_lng21]+sort_subls_lng2[id_lng22])/2
            else:
                id_lng22=int(count2/2)
                id_lng21=copy.copy(id_lng22)
                lng_axis2=(sort_subls_lng2[id_lng21]+sort_subls_lng2[id_lng22])/2
            t_width1=lng_axis1-init_rect.lng
            t_height1=lat_axis-init_rect.lat
            rect11=avatar.models.Rect(lng=init_rect.lng,lat=init_rect.lat,width=t_width1,height=t_height1)
            rect11.save()
            t_width2=init_rect.lng+init_rect.width-lng_axis1
            rect12=avatar.models.Rect(lng=lng_axis1,lat=init_rect.lat, width=t_width2,height=t_height1)
            rect12.save()
            t_width3=lng_axis2-init_rect.lng
            t_height2=init_rect.lat+init_rect.height-lat_axis
            rect21=avatar.models.Rect(lng=init_rect.lng,lat=lat_axis,width=t_width3,height=t_height2)
            rect21.save()
            t_width4=init_rect.lng+init_rect.width-lng_axis2
            rect22=avatar.models.Rect(lng=lng_axis2,lat=lat_axis,width=t_width4,height=t_height2)
            rect22.save()
            chil11=avatar.models.CloST.objects.create(bounding_box=rect11,haschild=0,occupancy=0,context='')
            chil11.save()
            chil12=avatar.models.CloST.objects.create(bounding_box=rect12,haschild=0,occupancy=0,context='')
            chil12.save()
            chil21=avatar.models.CloST.objects.create(bounding_box=rect21,haschild=0,occupancy=0,context='')
            chil21.save()
            chil22=avatar.models.CloST.objects.create(bounding_box=rect22,haschild=0,occupancy=0,context='')
            chil22.save()
            chil11.parent=root
            chil11.save()
            root.save()
            chil12.parent=root
            chil12.save()
            root.save()
            chil21.parent=root
            chil21.save()
            root.save()
            chil22.parent=root
            chil22.save()
            root.save()
            root.haschild=1
            root.save()
            ind2=0
            while ind2<thr:
                if ls_sample[ind2].p.lng<chil12.bounding_box.lng:
                    if ls_sample[ind2].p.lat<chil22.bounding_box.lat:
                        RSpanningTree.inserttotree(chil11,traj,ls_sample[ind2],thr)
                    else:
                        RSpanningTree.inserttotree(chil21,traj,ls_sample[ind2],thr)
                elif ls_sample[ind2].p.lat<chil21.bounding_box.lat:
                    RSpanningTree.inserttotree(chil12,traj,ls_sample[ind2],thr)
                else:
                    RSpanningTree.inserttotree(chil22,traj,ls_sample[ind2],thr)
                ind2=ind2+1
            if sample.p.lng<root.get_children()[1].bounding_box.lng:
                if sample.p.lat<root.get_children()[2].bounding_box.lat:
                    RSpanningTree.inserttotree(root.get_children()[0], traj,sample,thr)
                else:
                    RSpanningTree.inserttotree(root.get_children()[2], traj,sample,thr)
            elif sample.p.lat<root.get_children()[2].bounding_box.lat:
                RSpanningTree.inserttotree(root.get_children()[1],traj,sample,thr)
            else:
                RSpanningTree.inserttotree(root.get_children()[3],traj,sample,thr)
            return
        else:
            if sample.p.lng<root.get_children()[1].bounding_box.lng:
                if sample.p.lat<root.get_children()[2].bounding_box.lat:
                    RSpanningTree.inserttotree(root.get_children()[0], traj,sample,thr)
                else:
                    RSpanningTree.inserttotree(root.get_children()[2], traj,sample,thr)
            elif sample.p.lat<root.get_children()[2].bounding_box.lat:
                RSpanningTree.inserttotree(root.get_children()[1],traj,sample,thr)
            else:
                RSpanningTree.inserttotree(root.get_children()[3],traj,sample,thr)


        return
    @staticmethod
    def addtoquadtree(root, list_traj, thr):
        init_rect=root.bounding_box
        #sub00=avatar.models.Rect()
        ls_lat=[]#save the lattitude of every sample saved in this node
        ls_lng=[]
        #ls_sample=[]
        num_traj = len(list_traj)
        occupancy=copy.copy(root.occupancy)
        # rect11=avatar.models.Rect(lat=11,lng=11,width=11,height=11)
        # rect11.save()
        # rect12=avatar.models.Rect(lat=12,lng=12,width=12,height=12)
        # rect12.save()
        # rect21=avatar.models.Rect(lat=21,lng=21,width=21,height=21)
        # rect21.save()
        # rect22=avatar.models.Rect(lat=22,lng=22,width=22,height=22)
        # rect22.save()
        # chil11=avatar.models.CloST.objects.create(bounding_box=rect11,haschild=0)
        # chil11.save()
        # chil12=avatar.models.CloST.objects.create(bounding_box=rect12,haschild=0)
        # chil12.save()
        # chil21=avatar.models.CloST.objects.create(bounding_box=rect21,haschild=0)
        # chil21.save()
        # chil22=avatar.models.CloST.objects.create(bounding_box=rect22,haschild=0)
        # chil22.save()
        # chil11.parent=root
        # chil11.save()
        # root.save()
        # chil12.parent=root
        # chil12.save()
        # root.save()
        # chil21.parent=root
        # chil21.save()
        # root.save()
        # chil22.parent=root
        # chil22.save()
        # root.save()
        # root.haschild=1
        # root.save()
        # return root

        #return num_traj
        i=0
        while i<num_traj:
            s = list_traj[i]
            s.save()
            j = 0
            num_trace = 1
            while j < num_trace:
                s_trace = s.trace
                s_trace.save()
                set_sample = s_trace.p.all()
                num_sample = len(set_sample)
                #return init_rect.lat,init_rect.lng,init_rect.height,init_rect.width
                k=0
                while k<num_sample:
                    if set_sample[k].p.lat>=init_rect.lat+init_rect.height:
                        return k,'1 stuck'
                        continue
                    if set_sample[k].p.lng>=init_rect.lng+init_rect.width:
                        return k,'2 stuck', 'p.lng='+str(set_sample[k].p.lng), '*+*= '+str(init_rect.lng+init_rect.width)
                        continue
                    if set_sample[k].p.lat<init_rect.lat:
                        return k,'3 stuck'
                        continue
                    if set_sample[k].p.lng<init_rect.lng:
                        return k,'4 stuck'
                        continue
                    if occupancy<thr:#if this node hasn't been full
                        root.ls_sample.add(set_sample[k])
                        root.save()
                        ls_sample=copy.copy(root.ls_sample.all())
                        #return len(ls_sample)
                        occupancy=occupancy+1
                        root.occupancy=copy.copy(occupancy)
                        root.save()
                        #root.ls_traj.append([s.id,s.taxi])
                        root.ls_traj.add(s)
                        root.save()
                        ls_lat.append(set_sample[k].p.lat)
                        ls_lng.append(set_sample[k].p.lng)
                    elif root.haschild==0:#if this node has been full
                        sort_ls_lat=sorted(ls_lat)
                        sort_ls_lng=sorted(ls_lng)
                        #return 'len(sort_ls_lat)= '+str(len(sort_ls_lat)),'len(sort_ls_lng)= '+str(len(sort_ls_lng))
                        id_lat1=int(thr/2)
                        #id_lng1=int(thr/2)
                        t_id_lat1=2*id_lat1
                        if t_id_lat1==thr:#thr is even
                            id_lat2=copy.copy(id_lat1)
                            id_lat1=copy.copy(id_lat2)-1
                        else:#thr is odd
                            id_lat2=copy.copy(id_lat1)
                            id_lat1=copy.copy(id_lat2)
                        lat_axis=(sort_ls_lat[id_lat1]+sort_ls_lat[id_lat2])/2
                        #return id_lat1,id_lat2
                        ind=0
                        ls1=[]
                        ls2=[]
                        subls_lng1=[]
                        subls_lng2=[]
                        count1=0
                        count2=0
                        while ind<thr:
                            if ls_sample[ind].p.lat<lat_axis:
                                ls1.append(ls_sample[ind])
                                subls_lng1.append(ls_sample[ind].p.lng)
                                count1=copy.copy(count1)+1
                            else:
                                ls2.append(ls_sample[ind])
                                subls_lng2.append(ls_sample[ind].p.lng)
                                count2=copy.copy(count2)+1
                            ind=ind+1
                        sort_subls_lng1=sorted(subls_lng1)
                        sort_subls_lng2=sorted(subls_lng2)
                        #return count1,count2
                        if count1==0:
                            id_lng12=0
                            id_lng11=0
                            lng_axis1=root.bounding_box.lng+root.bounding_box.width/2
                        elif count1==1:
                            id_lng12=0
                            id_lng11=0
                            lng_axis1=(sort_subls_lng1[id_lng11]+sort_subls_lng1[id_lng12])/2
                        elif count1%2==0:#if count1 is even
                            id_lng12=int(count1/2)
                            id_lng11=copy.copy(id_lng12)-1
                            lng_axis1=(sort_subls_lng1[id_lng11]+sort_subls_lng1[id_lng12])/2
                        else:
                            id_lng12=int(count1/2)
                            id_lng11=copy.copy(id_lng12)
                            lng_axis1=(sort_subls_lng1[id_lng11]+sort_subls_lng1[id_lng12])/2
                        if count2==0:
                            id_lng22=0
                            id_lng21=0
                            lng_axis2=root.bounding_box.lng+root.bounding_box.width/2
                        elif count2==1:
                            id_lng22=0
                            id_lng21=0
                            lng_axis2=(sort_subls_lng2[id_lng21]+sort_subls_lng2[id_lng22])/2
                        elif count2%2==0:#if count1 is even
                            id_lng22=int(count2/2)
                            id_lng21=copy.copy(id_lng22)-1
                            lng_axis2=(sort_subls_lng2[id_lng21]+sort_subls_lng2[id_lng22])/2
                        else:
                            id_lng22=int(count2/2)
                            id_lng21=copy.copy(id_lng22)
                            lng_axis2=(sort_subls_lng2[id_lng21]+sort_subls_lng2[id_lng22])/2
                        t_width1=lng_axis1-init_rect.lng
                        t_height1=lat_axis-init_rect.lat
                        rect11=avatar.models.Rect(lng=init_rect.lng,lat=init_rect.lat,width=t_width1,height=t_height1)
                        rect11.save()
                        t_width2=init_rect.lng+init_rect.width-lng_axis1
                        rect12=avatar.models.Rect(lng=lng_axis1,lat=init_rect.lat, width=t_width2,height=t_height1)
                        rect12.save()
                        t_width3=lng_axis2-init_rect.lng
                        t_height2=init_rect.lat+init_rect.height-lat_axis
                        rect21=avatar.models.Rect(lng=init_rect.lng,lat=lat_axis,width=t_width3,height=t_height2)
                        rect21.save()
                        t_width4=init_rect.lng+init_rect.width-lng_axis2
                        rect22=avatar.models.Rect(lng=lng_axis2,lat=lat_axis,width=t_width4,height=t_height2)
                        rect22.save()
                        chil11=avatar.models.CloST.objects.create(bounding_box=rect11,haschild=0,occupancy=0,context='')
                        chil11.save()
                        chil12=avatar.models.CloST.objects.create(bounding_box=rect12,haschild=0,occupancy=0,context='')
                        chil12.save()
                        chil21=avatar.models.CloST.objects.create(bounding_box=rect21,haschild=0,occupancy=0,context='')
                        chil21.save()
                        chil22=avatar.models.CloST.objects.create(bounding_box=rect22,haschild=0,occupancy=0,context='')
                        chil22.save()
                        chil11.parent=root
                        chil11.save()
                        root.save()
                        chil12.parent=root
                        chil12.save()
                        root.save()
                        chil21.parent=root
                        chil21.save()
                        root.save()
                        chil22.parent=root
                        chil22.save()
                        root.save()
                        root.haschild=1
                        root.save()
                        #RSpanningTree.inserttotree(chil11,s.id,s.taxi,set_sample[k],thr)
                        if set_sample[k].p.lng<root.get_children()[1].bounding_box.lng:
                            if set_sample[k].p.lat<root.get_children()[2].bounding_box.lat:
                                RSpanningTree.inserttotree(root.get_children()[0], s,set_sample[k],thr)
                            else:
                                RSpanningTree.inserttotree(root.get_children()[2], s,set_sample[k],thr)
                        elif set_sample[k].p.lat<root.get_children()[2].bounding_box.lat:
                            RSpanningTree.inserttotree(root.get_children()[1],s,set_sample[k],thr)
                        else:
                            RSpanningTree.inserttotree(root.get_children()[3],s,set_sample[k],thr)
                        #return #root
                    else:
                        if set_sample[k].p.lng<root.get_children()[1].bounding_box.lng:
                            if set_sample[k].p.lat<root.get_children()[2].bounding_box.lat:
                                RSpanningTree.inserttotree(root.get_children()[0], s,set_sample[k],thr)
                            else:
                                RSpanningTree.inserttotree(root.get_children()[2], s,set_sample[k],thr)
                        elif set_sample[k].p.lat<root.get_children()[2].bounding_box.lat:
                            RSpanningTree.inserttotree(root.get_children()[1],s,set_sample[k],thr)
                        else:
                            RSpanningTree.inserttotree(root.get_children()[3],s,set_sample[k],thr)
                        #return #root




                    k=k+1
                j=j+1
            i=i+1

        return #root
    @staticmethod
    def createtimeindex(rootorigin,root,timereso):
        str_box='bounding_box:{\nlat:'+str(root.bounding_box.lat)+',\nlng:'+str(root.bounding_box.lng)+\
             ',\nheight:'+str(root.bounding_box.height)+',\nwidth:'+\
             str(root.bounding_box.width)+'},\n'
        str_haschild='haschild:'+str(root.haschild)+',\n'
        str_occupancy='occupancy:'+str(root.occupancy)+',\n'
        rootorigin.context=rootorigin.context+str_box+str_haschild+str_occupancy
        if root.haschild==1:
            rootorigin.context=rootorigin.context+'children:{[\n'
            RSpanningTree.createtimeindex(rootorigin,root.get_children()[0],timereso)
            rootorigin.context=rootorigin.context+'\n]\n'
            RSpanningTree.createtimeindex(rootorigin,root.get_children()[1],timereso)
            rootorigin.context=rootorigin.context+'\n]\n'
            RSpanningTree.createtimeindex(rootorigin,root.get_children()[2],timereso)
            rootorigin.context=rootorigin.context+'\n]\n'
            RSpanningTree.createtimeindex(rootorigin,root.get_children()[3],timereso)
            rootorigin.context=rootorigin.context+'\n]}\n'
        else:
            ls_traj=root.ls_traj.all()
            num_ls_traj=len(ls_traj)
            num_timeslot=int(86400/timereso)+1
            start_time=[0,0,0]
            end_time=[23,59,59]
            t_raw1=str(rootorigin.starttime).split('+')
            t_raw2=copy.copy(t_raw1[0])
            raw_time = RSpanningTree.time_split(t_raw2)
            raw_time[1][0]=0
            raw_time[1][1]=0
            raw_time[1][2]=0
            #rawtime=rootorigin.
            #stime=
            k=0
            year=copy.copy(raw_time[0][0])
            month=copy.copy(raw_time[0][1])
            day=copy.copy(raw_time[0][2])
            while k<num_timeslot:
                hour=copy.copy(start_time[0])
                minute=copy.copy(start_time[1])
                sec=copy.copy(start_time[2])
                temp_s_time=str(copy.copy(year))+'-'+str(copy.copy(month))+'-'+str(copy.copy(day))+' '\
                            +str(hour)+':'+str(minute)+':'+str(sec)

                t_node=avatar.models.TimeSlot(bounding_box=root.bounding_box,starttime=temp_s_time,timeslot=timereso)
                t_node.save()
                root.timenode.add(t_node)
                root.save()
                rootorigin.save()

                k=k+1
                t_s=RSpanningTree.time_to_sec(start_time)
                t_s=copy.copy(t_s)+timereso
                start_time=RSpanningTree.sec_to_time(t_s)
            i=0
            str_traj='ls_traj: '
            while i<num_ls_traj:
                str_traj=str_traj+'['+str(ls_traj[i].id)+str(ls_traj[i].taxi)+']\n'
                i=i+1
            #str_traj=str_traj+'\n'
            rootorigin.context=rootorigin.context+str_traj
            rootorigin.save()
            str_sample='ls_sample:'
            ls_sample=root.ls_sample.all()
            num_ls_sample=len(ls_sample)
            j=0
            alreadyin=0
            while j<num_ls_sample:
                str_sample=str_sample+'['+str(ls_sample[j].id)+str(ls_sample[j].p.lat)+str(ls_sample[j].p.lng)+']\n'
                tt_raw1=str(ls_sample[j].t).split('+')
                tt_raw2=copy.copy(tt_raw1[0])
                raw_time = RSpanningTree.time_split(tt_raw2)
                timevalue=RSpanningTree.time_to_sec(raw_time[1])
                timeid=int(timevalue/timereso)
                root.timenode.all()[timeid].ls_sample.add(ls_sample[j])
                root.save()
                rootorigin.save()
                if alreadyin==0:
                    root.timenode.all()[timeid].ls_traj.add(ls_traj[0])#in fact, ls_traj might contain several trajs, but here we only
                    root.save()
                    rootorigin.save()
                    alreadyin=1
                #consider 1 traj in each ls_traj
                j=j+1
            k=0
            str_timenode='tnode:'
            while k<num_timeslot:
                num_sample=len(root.timenode.all()[k].ls_sample.all())
                str_timenode=str_timenode+'slot '+str(k)+str(num_sample)+': {\n '
                j=0
                while j<num_sample:
                    str_timenode=str_timenode+'['+str(root.timenode.all()[k].ls_sample.all()[j].id)+\
                                 str(root.timenode.all()[k].ls_sample.all()[j].t)+']'+'\n'
                    j=j+1
                str_timenode=str_timenode+'}\n'
                k=k+1

            #rootorigin.context=rootorigin.context+str_sample
            rootorigin.context=rootorigin.context+str_timenode
            rootorigin.save()




        return
    @staticmethod
    def create_tree(list_traj):
        #[lat,lng]=RSpanningTree.find(list_traj)#list_traj is a list of Trajectory
        #return 1,lat,lng
        [minlat,maxlat,minlng,maxlng,mindate,maxdate]=RSpanningTree.find(list_traj)#list_traj is a list of Trajectory

        #return 1,minlng,maxlng-minlng,minlat,maxlat-minlat,mindate,maxdate
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
        #num_lat_grid=int(latrange/reso_lat)+1
        #num_lng_grid=int(lngrange/reso_lng)+1#number of grids after division
        #print num_lng_grid
        #print num_lat_grid
        print 'before',mindate,maxdate
        print 'after',mindate,maxdate

        i=0
        j=0
        lng_start=int(minlng*lng_round)
        lat_start=int(minlat*lat_round)
        lng_end=int(maxlng*lng_round)+1
        lat_end=int(maxlat*lat_round)+1
        #lng_end=int(lng_start+lngrange*lng_round)+1
        #lat_end=int(lat_start+latrange*lat_round)+1
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
        root=avatar.models.Yohoho(id='0', s_time=copy.copy(temp_mind), e_time=copy.copy(temp_maxd), s_lat=str(lat_start), e_lat=str(lat_end),
                    s_lng=str(lng_start), e_lng=str(lng_end))
#create nodes based on spatial grids
        root.save()
        tt_lng_start=float(lng_start/lng_round)
        tt_lat_start=float(lat_start/lat_round)
        tw1=copy.copy(float(lng_end-lng_start)/float(lng_round))
        tw2=copy.copy(minlng-tt_lng_start)
        twidth=copy.copy(tw1)+copy.copy(tw2)
        th1=copy.copy(float(lat_end-lat_start)/float(lat_round))
        th2=copy.copy(minlat-tt_lat_start)
        theight=copy.copy(th1)+copy.copy(th2)
        #return 1,tw1,tw2,th1,th2
        #return 1,twidth,theight,tt_lng_start,tt_lat_start,minlng,minlat
        #lat_start=tt_lat_start
        #lng_start=tt_lng_start
        rect=avatar.models.Rect(lat=tt_lat_start,lng=tt_lng_start,width=twidth,height=theight)
        rect.save()
        root2=avatar.models.CloST(bounding_box=rect,haschild=0,occupancy=0,context='',starttime=temp_mind)
        root2.save()
        #root2.haschild=0
        root2.save()
        num_lng_grid=int(twidth/temp_lng)+1
        num_lat_grid=int(theight/temp_lat)+1
        #return root2,root2.haschild,root2.bounding_box.lat,root2.bounding_box.lng, root2.bounding_box.height, root2.bounding_box.width,mindate,maxdate
        #return root2, 'theight= '+str(theight), 'twidth= '+str(twidth), temp_lat,temp_lng,num_lat_grid,num_lng_grid#,mindate,maxdate
        #start here
        thr=100
        occupancy=0
        #root3=RSpanningTree.addtoquadtree(root2, list_traj, thr)
        RSpanningTree.addtoquadtree(root2, list_traj, thr)
        #return root2, root2.get_children()[0].get_children()[2].bounding_box.lat, root2.get_children()[0].bounding_box.lat,root2.get_children()[1].bounding_box.lat,root2.get_children()[2].bounding_box.lat,root2.get_children()[3].bounding_box.lat
        test_sample=root2.ls_sample.all()
        child=root2.get_children()[0]
        child.save()
        l_occ=[]
        l_occ.append(child.occupancy)
        while child.haschild==1:
            child=child.get_children()[0]
            l_occ.append(child.occupancy)
        info=RSpanningTree.createtimeindex(root2,root2,reso_time)

        return root2,root2.context
        #return root2, root2.get_children()[0].get_children()[2].bounding_box.lat,root2.get_children()[0].get_children()[1].get_children()[2].bounding_box.lat,test_sample[0].p.lat,l_occ
        #return root2,root3

        #********************************************************************************
        #********************************************************************************
        #********************************************************************************
        # while i<num_lng_grid:
        #     j=0
        #     while j<num_lat_grid:
        #         lng_grid=int(lng_start+j*reso_lng*lng_round)
        #         lat_grid=int(lat_start+i*reso_lat*lat_round)
        #         tj=j+1
        #         elng_grid=int(lng_start+tj*reso_lng*lng_round)
        #         #return root, num_lat_grid, num_lng_grid
        #         node=avatar.models.Yohoho(id=str(count), s_time=copy.copy(temp_mind), e_time=copy.copy(temp_maxd),
        #                     s_lat=str(lat_grid), s_lng=str(lng_grid), e_lat=str(lat_grid), e_lng=str(elng_grid))
        #         node.save()
        #         #return node, mindate, reso_time, maxdate
        #         #RSpanningTree.createfile_daytime(node,mindate,reso_time,maxdate)#in each spatial grid, create node based on time slots
        #         t=RSpanningTree.createfile_daytime(node,mindate,reso_time,maxdate)
        #         return node,t
        # #restart from here
        #         node.save()
        #         root.pointer.add(node)
        #         root.save()
        #         count=count+1
        #         j=j+1
        #     i=i+1
        # return root



#*******************************************#*******************************************
#*******************************************#*******************************************
#*******************************************#*******************************************

#*******************************************#*******************************************
#*******************************************#*******************************************
#*******************************************#*******************************************
        # RSpanningTree.addtofolder(root,list_traj,lng_start,lng_round,lat_start,lat_round,reso_lng,reso_lat,reso_time,num_lat_grid)
        # return root
#*******************************************#*******************************************
#*******************************************#*******************************************
#*******************************************#*******************************************
