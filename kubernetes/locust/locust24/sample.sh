#!/bin/bash
locust -f locustfile.py --host http://192.168.49.2:30001/polls/ --headless #-u 20 -r 20
