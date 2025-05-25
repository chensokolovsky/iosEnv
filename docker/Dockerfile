FROM ubuntu:22.04

# update
RUN apt-get update -y
RUN apt-get upgrade -y

# install
RUN apt-get install -y curl
RUN apt-get install -y lldb-14
RUN apt-get install -y python3-lldb-14
RUN ln -s /usr/lib/llvm-14/lib/python3.10/dist-packages/lldb/* /usr/lib/python3/dist-packages/lldb/
RUN apt-get install -y libusbmuxd-tools
RUN apt-get install -y python3-pip
RUN pip install frida-tools==13.0.4
RUN apt-get install -y openssh-client

# workdir
WORKDIR /env

COPY ./config.cfg /env/
COPY ./docker/env /env/
RUN mkdir /env/scripts

RUN chmod +x /env/debug
RUN chmod +x /env/init
RUN chmod +x /env/generate_lldbinit
RUN chmod +x /env/logger.sh

