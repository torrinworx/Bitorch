FROM python:3.10-slim

# Set to non interactive
ENV DEBIAN_FRONTEND=noninteractive
ENV ENV=development

# Set working dir
WORKDIR /Bitorch

# Update packages and install necessary tools
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

### Bitorch Setup ###
COPY ./ /Bitorch/

# Install Pipenv
RUN pip install --no-cache-dir pipenv && \
    pipenv install

EXPOSE 8000
