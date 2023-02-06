FROM navikey/raspbian-buster
#FROM balenalib/raspberry-pi-python:3.9-buster
RUN apt update && apt install openssh-server coreutils cmake zlib1g-dev wget -y #software-properties-common -y
#RUN sudo add-apt-repository ppa:deadsnakes/ppa
#RUN apt install python3.9 -y
RUN apt install build-essential tar -y
RUN apt install libssl-dev libncurses5-dev libsqlite3-dev libreadline-dev libtk8.6 libgdm-dev libdb4o-cil-dev libpcap-dev gcc -y
RUN cd /tmp && wget https://www.python.org/ftp/python/3.9.16/Python-3.9.16.tgz && tar -zxvf Python-3.9.16.tgz && cd Python-3.9.16 && apt install python-opencv -y && ./configure --enable-optimizations && make install
RUN useradd -rm -d /home/ubuntu -s /bin/bash -g root -G sudo -u 1000 timur
RUN echo 'timur:test' | chpasswd
COPY ./requirements.txt requirements.txt
RUN pip3 install -U pip setuptools wheel && pip3 install -r requirements.txt
RUN service ssh start
EXPOSE 22

CMD ["/usr/sbin/sshd","-D"]

