FROM continuumio/miniconda3:latest

WORKDIR /perform_metrics
COPY conda_env.yml setup.py README.md git_version.txt ./
ADD src/ ./src/

# from the gitlab ci
RUN ls
RUN apt update
RUN apt-get install --yes gcc --fix-missing
RUN conda env create --file conda_env.yml
RUN [ "/bin/bash", "-c", "source activate sd2-perform_metrics && pip install ." ]
RUN echo "source activate sd2-perform_metrics" > ~/.bashrc
RUN export PYTHONPATH=/perform_metrics:$PYTHONPATH
