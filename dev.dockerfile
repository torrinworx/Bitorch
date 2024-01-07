FROM ubuntu:22.04

# Set to non interactive
ENV DEBIAN_FRONTEND=noninteractive

# Update packages and install necessary tools
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y curl build-essential python3-dev gcc libgl1-mesa-glx python3-pip

# Set working dir
WORKDIR /Bitorch

### Bitorch Setup ###

# Copy app to container
COPY ./ /Bitorch

# Install Pipenv
RUN pip install pipenv

# Install Python dependencies using pipenv
RUN pipenv install
