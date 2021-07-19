# base image  
FROM python:3.8   

# where your code lives  
WORKDIR /server2/

COPY ./requirements.txt /server2/requirements.txt

RUN pip install -r requirements.txt

COPY . /server2/

# port where the Django app runs  
EXPOSE 8080
RUN chmod +x /server2/sample.sh
    
# start server  
CMD ["/server2/sample.sh"]