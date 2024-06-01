FROM python:3.12-slim
LABEL maintainer="mickaelyoshua7674"

# copy files to image
COPY ./requirements.txt /tmp/requirements.txt
COPY ./app /app
WORKDIR /app

# the output of python will be printed directly on console
ENV PYTHONUNBUFFERED=1

    # update Debian
RUN apt-get update && apt-get upgrade -y && \
    # in order to psycopg2 connect to postgres the dependencie 'libpq-dev' must be installed
    apt-get install libpq-dev -y && \
    # install gcc
    apt-get install gcc -y && \
    # remove apt cache
    rm -rf /var/lib/apt/lists/* && \
    # create virtual environment
    python -m venv /venv && \
    # upgrade pip
    /venv/bin/pip install --upgrade pip && \
    # install requirements
    /venv/bin/pip install -r /tmp/requirements.txt && \
    # remove temporary folder
    rm -rf /tmp 

ENV PATH="/venv/bin:$PATH"

EXPOSE 8080