FROM robo2025/python:3.6-alpine

ADD . /project/app

WORKDIR /project/app

RUN apk add -U tzdata && \
   ln -sf /usr/share/zoneinfo/Asia/Shanghai  /etc/localtime

RUN pip install -r requirements.txt

RUN cd /project/app && \
   python manage.py collectstatic

CMD ["uwsgi", "/project/app/5GCat/wsgi/uwsgi.ini"]
