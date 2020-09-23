FROM python:alpine3.7
COPY . /app
WORKDIR /app
RUN apk add build-base
RUN apk add opus
RUN apk add libffi libffi-dev
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
CMD python3 -u ./picturebot.py