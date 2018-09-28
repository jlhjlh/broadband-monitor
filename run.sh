# fix line 4. that's not the command that runs any more.

#!/bin/sh
if ps -ef | grep -v grep | grep "python3.7 /home/pi/broadband-monitor/bw.py" ; then
        exit 0
else
        cd /home/pi/broadband-monitor/ && . venv/bin/activate && python /home/pi/broadband-monitor/bw.py
        exit 0
fi