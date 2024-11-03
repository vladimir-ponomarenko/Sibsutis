ps -e | wc -l
ps -e | grep `whoami` | wc -l


ps -t $(tty) -o pid,ppid,comm --forest

pstree > ~/pstrees
cat ~/pstrees

top

man bash &

jobs

fg %1