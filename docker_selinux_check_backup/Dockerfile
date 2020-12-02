FROM ubuntu:18.04
RUN apt-get update -y && \
    apt-get install -y python-pip python-dev
COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY ./app /app
COPY ./static /static
WORKDIR /app
ENTRYPOINT ["python"]
CMD ["main.py"]
