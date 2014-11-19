This Project contains tool(s) to report on
- Project(s) resource usage
- Utilisation (VCPUs, RAM) of the system
- Quotas

Example 1: 
python usage2csv.py --start 2014-05-01 --end 2014-05-02 --screen_stats

Example 2:
python usage2csv.py --start 2014-05-01 --end 2014-05-02 --quotas

Options:
python usage2csv.py

Output formats: 
- CSV for Excel 
- Statistical information in text format 
- graphical trending (not for quotas)

TODO:
- separate reporting for the big data nodes
- better precision to take into account VM run time 
  - Now all VM are counted per day  and assumed to be concurrently running
    whether or not their life time was 1 min or 24 h
- nicer graphs


Main author: jarno.laitinen@csc.fi



