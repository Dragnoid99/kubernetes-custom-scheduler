#!/bin/bash
locust -f locustfile.py --host http:///service-1-2/polls/ --headless #-u 20 -r 20
