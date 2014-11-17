from os import getenv
from getpass import getpass
import time
from datetime import datetime, timedelta
from collections import defaultdict
from openstack import OpenStackConnector
import collections
from plot2 import first

def get_from_env_or_prompt(varname, echo=True):
    """Get an environment variable, if it exists, or query the user for it"""
    value = getenv(varname)
    if value is None:
        print '%s not found in env.' % varname
        if echo:
            value = raw_input('Try sourcing openrc.sh or enter the value: ')
        else:
            value = getpass('Try sourcing openrc.sh or enter the value: ')
    return value


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Reports OpenStack usage')
    parser.add_argument('--start', dest='start', required=True, help='date e.g. 2014-01-01')
    parser.add_argument('--end', dest='end', required=True, help='date e.g. 2014-02-01')
    parser.add_argument('--with-header', dest='header', action='store_const',
                        const=True, default=False)
    parser.add_argument('--project',dest='project',required=False,help='Add name of Project if you want Project specific report',default=False)
    parser.add_argument('--csv',help='To get csv output instead of statistical summary',action="store_true")
    parser.add_argument('--screen_stats',help='To get statistics on screen (human readable)',action="store_true")
    parser.add_argument('--trend',help='plot trends',action="store_true")
    parser.add_argument('--julkict',help='count only julkict Projects',action="store_true",default=False)
    args = parser.parse_args()

    if not (args.start and args.end):
        parser.print_help()
        return

    username = get_from_env_or_prompt('OS_USERNAME')
    password = get_from_env_or_prompt('OS_PASSWORD', echo=False)
    tenant = get_from_env_or_prompt('OS_TENANT_ID')
    auth_url = get_from_env_or_prompt('OS_AUTH_URL')
    osc = OpenStackConnector(username, password, tenant, auth_url)

    start = datetime.fromtimestamp(time.mktime(
        time.strptime(args.start, "%Y-%m-%d")))
    pstart = start
    end = datetime.fromtimestamp(time.mktime(
        time.strptime(args.end, "%Y-%m-%d")))

    if args.header and args.csv:
        print '"Date","Instance ID","VCPUs","Memory MB","Flavor","Project","State","Start","End"'
    vms=defaultdict(defaultdict)
    rams=defaultdict(dict)
    vcpus=defaultdict(dict)
    vms_all=defaultdict(dict)
    rams_all=defaultdict(dict)
    vcpus_all=defaultdict(dict)
    sums = {}
    dates = 0

    min_vms = 999999
    max_vms = 0
    avg_vms = 0
    sum_vms = 0

    sum_ram = 0
    min_ram = 999999
    max_ram = 0
    avg_ram = 0

    sum_vcpus = 0
    min_vcpus = 999999
    max_vcpus = 0
    avg_vcpus = 0

    projects=[]
    projects.append("all")
    while pstart <= end:
        dates += 1
        for tenant in osc.get_tenant_usages(pstart, pstart + timedelta(1)):
            ftime = time.strftime("%Y-%m-%d", pstart.timetuple())
            for vm in tenant.get('server_usages'):
                # print "VM :%s "%vm.items()
                # ftime = time.strftime("%Y-%m-%d", pstart.timetuple())
                skip=False
                if vm.get('tenant_id') == 'nagiostest': # if vm.get('state') == 'active':
                   skip=True
                if  args.project != False: 
                   if vm.get('tenant_id') != args.project:
                      skip=True 
                if args.julkict != False:
                   proj = vm.get('tenant_id')
                   if not proj.startswith("julkict"):
                      skip=True
                if skip==False:    
                   if args.csv:
                             print '"%s","%s",%s,%s,"%s","%s","%s","%s","%s"' % (ftime,
                                                          vm.get('instance_id'),
                                                          vm.get('vcpus'),
                                                          vm.get('memory_mb'),
                                                          vm.get('flavor'),
                                                          vm.get('tenant_id'),
                                                          vm.get('state'),
                                                          vm.get('started_at'),
                                                          vm.get('ended_at'))
                   
                   if vm.get('tenant_id') in vms[ftime]:
                     vms[ftime][vm.get('tenant_id')] += 1
                     rams[ftime][vm.get('tenant_id')] += vm.get('memory_mb') 
                     vcpus[ftime][vm.get('tenant_id')] += vm.get('vcpus')
                   else:
                     vms[ftime][vm.get('tenant_id')]=1 
                     rams[ftime][vm.get('tenant_id')] = vm.get('memory_mb') 
                     vcpus[ftime][vm.get('tenant_id')] = vm.get('vcpus') 
                     if vm.get('tenant_id') not in projects:
                        projects.append(vm.get('tenant_id'))

        vms_all[ftime]=sum(vms[ftime].values())
        rams_all[ftime]=sum(rams[ftime].values() )
        vcpus_all[ftime]=sum(vcpus[ftime].values() )
        if args.screen_stats and not args.csv:
          print 'Total on day %s :  VMs %s, RAM %s and VCPUS %s ' % (ftime, vms_all[ftime],rams_all[ftime],vcpus_all[ftime])

        if sum(vms[ftime].values() ) < min_vms:
          min_vms = sum(vms[ftime].values() )
        if sum(vms[ftime].values() ) > max_vms:
          max_vms = sum(vms[ftime].values() )
        sum_vms += sum(vms[ftime].values() )

        if sum(rams[ftime].values() ) < min_ram:
          min_ram = sum(rams[ftime].values() )
        if sum(rams[ftime].values() ) > max_ram:
          max_ram = sum(rams[ftime].values() )
        sum_ram += sum(rams[ftime].values() )

        if sum(vcpus[ftime].values() ) < min_vcpus:
          min_vcpus = sum(vcpus[ftime].values() )
        if sum(vcpus[ftime].values() ) > max_vcpus:
          max_vcpus = sum(vcpus[ftime].values() )
        sum_vcpus += sum(vcpus[ftime].values() )
         
        pstart = pstart + timedelta(1)

    # print "%s"%projects
    pstart = start
    while pstart <= end:
       ftime = time.strftime("%Y-%m-%d", pstart.timetuple())
       for p in projects:
          if p not in 'all':
            try:
               vms[ftime][p] 
            except KeyError:
               vms[ftime][p] = 0
               rams[ftime][p] = 0
               vcpus[ftime][p] = 0
       pstart += timedelta(1)

    if dates > 0:
      avg_vms = sum_vms/dates
      avg_ram = sum_ram/dates
      avg_vcpus = sum_vcpus/dates
    total_ram = 13*128
    total_vcpus = 13*2*8*2*2 # 13 nodes, 2 CPUS, 8 cores, 2x due Hyper-Threading, 2x due overbooking
    if args.screen_stats and not args.csv:
      print 'VMS: Min %s max %s and avg %s.' % (min_vms,max_vms,avg_vms)
      print 'RAM: Min %s max %s and avg %s.' % (min_ram,max_ram,avg_ram)
      print 'RAM utilisation percentage of total RAM %s GB: min %0.2f  max: %0.2f avg: %0.2f . ' % ( total_ram, (min_ram/1024.0)/total_ram*100, (max_ram/1024.0)/total_ram*100.0,(avg_ram/1024.0)/total_ram*100.0)
      print 'VCPUs: Min %s max %s and avg %s.' % (min_vcpus,max_vcpus,avg_vcpus)
      print 'CPU utilisation percentage of total %s VCPUS: min %0.2f  max: %0.2f avg: %0.2f . ' % ( total_vcpus, min_vcpus/1.0/total_vcpus*100.0, max_vcpus/1.0/total_vcpus*100.0, avg_vcpus/1.0/total_vcpus*100.0)


    # 1: DATE
    for key,value in sorted(vms.items()):
      vms_on_day = 0
      ram_on_day = 0
      vcpus_on_day = 0
      if args.screen_stats and not args.csv:
        print 'Total on day %s :  VMs %s, RAM %s and VCPUS %s ' % (key, sum(vms[key].values() ), sum(rams[key].values() ), sum(vcpus[key].values() ) )
      # TENANTS 
      for key2,value2 in sorted(value.items()):
          # print key2,'is',value2
          #    if key2 in sums:
          #      sums[key2]=sums[key2]+value2[0]
          #  .  else: 
          #      sums[key2]=value2[0]
          vms_on_day = vms_on_day + vms[key][key2]
          ram_on_day = ram_on_day + rams[key][key2]
          vcpus_on_day = vcpus_on_day + vcpus[key][key2]
          if args.screen_stats and not args.csv:
             print ' - Project %s had %s VMs, RAM %s and VCPUs %s ' % (key2, vms[key][key2], rams[key][key2], vcpus[key][key2])
      if args.screen_stats and not args.csv:
         print 'VMs on day %s VMs %s, RAM %s and VCPUS %s ' % (key, vms_on_day,ram_on_day,vcpus_on_day)  
      
    # if args.csv:
    #   print '%s,%s,%s,%s'%(key, vms_on_day,ram_on_day,vcpus_on_day)
    if args.trend:
       first(vms,rams,vcpus,projects,vms_all,rams_all,vcpus_all,dates)
if __name__ == '__main__':
    main()
