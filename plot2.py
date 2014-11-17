#!/usr/bin/env python
"""
Show how to make date plots in matplotlib using date tick locators and
formatters.  See major_minor_demo1.py for more information on
controlling major and minor ticks

All matplotlib date plotting is done by converting date instances into
days since the 0001-01-01 UTC.  The conversion, tick locating and
formatting is done behind the scenes so this is most transparent to
you.  The dates module provides several converter functions date2num
and num2date

"""
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, AutoMinorLocator, MaxNLocator, AutoLocator
from matplotlib.dates import DayLocator, WeekdayLocator, MonthLocator, DateFormatter, MONDAY
from matplotlib.widgets import RadioButtons
from collections import defaultdict 


def first(vms,rams,vcpus,projects,vms_all,rams_all,vcpus_all, days):
 #ConvertToDate = lambda s: datetime.strptime(s,"%Y-%m-%d")
 # ConvertToGBs = lambda s: s/1024.0
 # 2014-05-01,d5ca1a43-0841-45a3-a31f-fff0fb4ba7aa,2,4096,m1.medium,provisiontest,active,2014-02-13T13:44:49.000000,None

 # '"Date","Instance ID","VCPUs","Memory MB","Flavor","Project","State","Start","End"
 # alldata = np.genfromtxt('may.csv', delimiter=',', skip_header=0, skip_footer=0,dtype=(object), names=['dates','ID','cpu','ram','flavor','project','state','start','end'], converters={0: ConvertToDate})

 # projects = 
 #for x in alldata:
 #  projects.append(x[5])
 
 #for x in projects:
 #  print x
 fig2 = plt.figure(2)
 fig1 = plt.figure(1) 
 ex1 = fig2.add_subplot(1,1,1)
 # axcolor = 'lightgoldenrodyellow'
 radio = RadioButtons(ex1, projects, active=1)
 ax1 = fig1.add_subplot(4,1,1)
 fig1.autofmt_xdate()
 ax2 = fig1.add_subplot(2,1,2)
 

 def plot(event):

  dates=[]
  machines=[]
  rams_array=[]
  cores=[]
  total_ram_mb=1664.0
  total_cores=832.0
  if event=='all':
    for key,value in sorted(vms_all.items()):
      dates.append(datetime.strptime(key,"%Y-%m-%d"))
      machines.append(vms_all[key])
      rams_array.append(rams_all[key]/1024.0/total_ram_mb*100.0)
      cores.append(vcpus_all[key]/total_cores*100.0)
  else:
    for key,value in sorted(vms.items()):
      dates.append(datetime.strptime(key,"%Y-%m-%d"))
      machines.append(vms[key][event])
      rams_array.append(rams[key][event]/1024.0/total_ram_mb*100.0)
      cores.append(vcpus[key][event]/total_cores*100.0)
  ax1.clear()
  ax2.clear()
  if (days>7):
    ax1.xaxis.set_major_locator(MonthLocator())
    mondays=WeekdayLocator(MONDAY)
    ax1.xaxis.set_minor_locator(mondays)
    ax2.xaxis.set_major_locator(mondays)
    ax2.xaxis.set_minor_locator(AutoLocator())
    #ax2.xaxis.set_minor_locator(MaxNLocatora(5))
  else: 
    ax1.xaxis.set_major_locator(DayLocator())
    ax1.xaxis.set_minor_locator(MultipleLocator(days))
    ax2.xaxis.set_major_locator(DayLocator())
    ax2.xaxis.set_minor_locator(MultipleLocator(days))
  ax1.set_title("Amount of Virtual Machines per day of Project %s"%event)
  ax1.set_xlabel('Date')
  ax1.set_ylabel('VMs')
  m1=min(machines)-1
  m2=max(machines)+1
  ax1.set_ylim(m1,m2)
  ax1.grid(True)
  ax2.set_title("RAM and VCPU utilization (reserved of total capacity)")
  ax2.set_xlabel('Date')
  ax2.set_ylabel('%')
  m1=min(cores)-1
  m2=max(cores)+1
  ax2.set_ylim(m1, m2)
  ax2.grid(True)

  ax1.plot_date(dates,machines,'-', color='r',label='vms')
  ax2.plot_date(dates,cores,'-')
  ax2.plot_date(dates,rams_array,'-')
  ax2.set_title("RAM and VCPU utilization (reserved of total capacity) for project %s. "% event)
  fig1.show()
  fig1.canvas.draw()
  fig1.canvas.flush_events()
 radio.on_clicked(plot)

 plt.show()

