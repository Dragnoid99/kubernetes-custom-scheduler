# base image
FROM python:3.8

# where your code lives
WORKDIR /locust_dir/

COPY ./requirements.txt /locust_dir/requirements.txt

RUN pip install -r requirements.txt

COPY . /locust_dir/

# port where app runs
EXPOSE 8089

RUN chmod +x /locust_dir/sample.sh

# start program 
CMD ["./sample.sh"]
