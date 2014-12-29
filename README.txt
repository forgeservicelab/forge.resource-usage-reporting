This Project contains tool(s) to report on

- Tenants' resource usage and amount of virtual machines as well as
  the total system resources utilisation (VCPUs, RAM)
OR
- Tenant quotas (not for Volumes)
OR
- Volumes usage currently per Tenant

Example 1: Show VM statistics in text format
--------------------------------------------
python usage2csv.py --start 2014-05-01 --end 2014-05-02 --screen_stats


Example: Include Quota information
----------------------------------

python usage2csv.py --start 2014-05-01 --end 2014-05-02 --quotas

Example: Show Volume information:
---------------------------------
$ python usage2csv.py --volumes --csv --with-header 
Tenant,Volumes,Used_GBs
anttidevel,1,2
csc,8,21
nagiostest,1,1

$ python usage2csv.py --volumes --screen_stats
Tenant anttidevel has 1 Volumes using total 2 GB. 
Tenant csc has 8 Volumes using total 21 GB. 
Tenant nagiostest has 1 Volumes using total 1 GB. 

------------------------

Options:
python usage2csv.py

Output formats: 
- CSV for Excel or BIRT 
- Statistical information in text format 
- graphical trending (not for quotas or volumes)

TODO:
- separate reporting for the big data nodes
- better precision to take into account VM run time 
  - Now all VM are counted per day  and assumed to be concurrently running
    whether or not their life time was 1 min or 24 h


Main author: jarno.laitinen@csc.fi



