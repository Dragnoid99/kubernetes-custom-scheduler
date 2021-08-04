# base image
FROM python:3.8

# where your code lives
WORKDIR qosscheduler/

COPY ./requirements.txt qosscheduler/requirements.txt

RUN pip install -r qosscheduler/requirements.txt

COPY . qosscheduler/

RUN chmod +x qosscheduler/qosschedulerscript.sh

CMD ["./qosscheduler/qosschedulerscript.sh"]
