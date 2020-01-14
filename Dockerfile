FROM continuumio/miniconda3:latest

RUN apt-get update -y; apt-get upgrade -y; \
    apt-get install -y curl vim-tiny vim-athena

RUN conda config --add channels conda-forge && \
    conda update -n base -y conda
RUN conda create -n eb_conda_configs python=2.7 pip ipython setuptools pip anaconda-client jinja2

RUN echo "alias l='ls -lah'" >> ~/.bashrc
RUN echo "source activate eb_conda_configs" >> ~/.bashrc

ENV CONDA_EXE /opt/conda/bin/conda
ENV CONDA_PREFIX /opt/conda/envs/eb_conda_configs
ENV CONDA_PROMPT_MODIFIER (eb_conda_configs)
ENV CONDA_PYTHON_EXE /opt/conda/bin/python
ENV CONDA_DEFAULT_ENV eb_conda_configs
ENV PATH /opt/conda/envs/eb_conda_configs/bin:/opt/conda/condabin:/opt/conda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ENV CONDA_PREFIX_1 /opt/conda

