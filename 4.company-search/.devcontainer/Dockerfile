# Start from a base image that includes Python
FROM mcr.microsoft.com/devcontainers/python:0-3.11

# Install some necessary system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    bzip2 \
    && rm -rf /var/lib/apt/lists/*

# Set the Miniconda version and the path
ENV MINICONDA_VERSION py38_4.8.3
ENV CONDA_DIR /opt/conda

# Add the conda bin directory to the path
ENV PATH $CONDA_DIR/bin:$PATH

# Download and install Miniconda
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p $CONDA_DIR && \
    rm ~/miniconda.sh

# Create a conda environment and installs some packages
RUN conda create -y -n myenv python=3.11
RUN echo "source activate myenv" > ~/.bashrc
