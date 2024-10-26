FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    openssh-server \
    python3 \
    python3-pip \
    sudo

RUN mkdir /var/run/sshd

RUN echo 'root:password' | chpasswd
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

RUN useradd -rm -d /home/ansible -s /bin/bash -g root -G sudo -u 1000 ansible
RUN echo 'ansible:password' | chpasswd

RUN echo 'ansible ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

EXPOSE 22

CMD ["/usr/sbin/sshd", "-D"]
