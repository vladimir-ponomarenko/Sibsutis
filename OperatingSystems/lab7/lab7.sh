#!/bin/bash

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
workdir="${script_dir}" 

cat /home/user/STUDENT/MPM/vladimir.txt > "${workdir}/Lab7.txt"
cat "${workdir}/Lab7.txt"
cat /etc/passwd
cd /home/user/STUDENT && ls -l > "${workdir}/output.txt" && cp /etc/passwd "${workdir}/passwd.orig" && sort "${workdir}/passwd.orig" > "${workdir}/sorted_passwd.orig" && ls -l
cat "${workdir}/sorted_passwd.orig"
cat >> "${workdir}/passwd.orig" << END
newuser:x:1001:1001:New User,,,:/home/newuser:/bin/bash
END
cat "${workdir}/passwd.orig"