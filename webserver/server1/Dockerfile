# base image  
FROM python:3.8   

# where your code lives  
WORKDIR /mysite/

COPY ./requirements.txt /mysite/requirements.txt

RUN pip install -r requirements.txt

COPY . /mysite/

# port where the Django app runs  
EXPOSE 8000  
RUN chmod +x /mysite/sample.sh
    
# start server  
CMD ["/mysite/sample.sh"]