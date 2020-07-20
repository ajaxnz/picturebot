FROM python:alpine3.7
COPY . /app
WORKDIR /app
RUN apk add build-base
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
CMD python ./picturebot.py