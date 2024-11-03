#!/bin/bash

while true; do
  clear

  printf "%-8s %-8s %-8s %-12s %s\n" PID LWP NLWP TIME CMD

  ps -eo pid,lwp,nlwp,time,cmd | tail -n +2 | while read pid lwp nlwp time cmd; do
    printf "%-8s %-8s %-8s %-12s %s\n" "$pid" "$lwp" "$nlwp" "$time" "$cmd"
  done

  sleep 1
done