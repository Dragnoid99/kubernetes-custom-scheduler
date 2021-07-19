# base image
FROM python:3.8

# where your code lives
WORKDIR qosscheduler/

COPY ./requirements.txt qosscheduler/requirements.txt

RUN pip install -r qosscheduler/requirements.txt

COPY . qosscheduler/

RUN wget https://github.com/grafana/loki/releases/download/v2.2.1/logcli-linux-amd64.zip

RUN unzip logcli-linux-amd64.zip

RUN mv logcli-linux-amd64 logcli

RUN cp logcli /bin/

RUN chmod +x qosscheduler/qosschedulerscript.sh

CMD ["./qosscheduler/qosschedulerscript.sh"]
