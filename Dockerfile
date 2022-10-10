FROM python:3.10
ENV PYTHONUNBUFFERED 1

WORKDIR /code

COPY start /usr/local/bin/
RUN chmod +x /usr/local/bin/start
RUN ln -s /usr/local/bin/start /bin/start

COPY requirements.txt /code
#COPY . /code

RUN apt update
RUN pip install -U pip
RUN pip install -r requirements.txt


CMD ["start"]