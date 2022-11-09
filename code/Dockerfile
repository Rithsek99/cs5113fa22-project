FROM ubuntu:rolling

MAINTAINER Rithsek Ngem

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y locals && rm -rf /var/lib/apt/lists/* \
    && localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8
ENV LANG en_US.utf8

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y python3-pip

RUN apt-get install -y emacs nmap iputils-ping ssh htop slurm net-tools

ENV GRPC_PYTHON_VERSION 1.15.0

RUN apt-get install -y libprotoc-dev protobuf-compiler

RUN python3 -m pip install --upgrade pip && python3 -m pip install click grpcio grpcio-tools

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# Build python stuff
COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /usr/src/app

# Create the proto files
# Run protoc --python_out=. --grpc_python_out=. --proto_path=. ./proto/*.proto
RUN python3 -m grpc_tools.protoc -I./proto --python_out=. --grpc_python_out=. pokemonou.proto

EXPOSE 22
EXPOSE 80
EXPOSE 50050-50100

ENV PYTHONUNBUFFERED = 1

# Run the pokemonou game
CMD ["python3", "pokemonou.py"]