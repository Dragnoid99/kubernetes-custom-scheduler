#!/bin/bash
locust -f locustfile.py --host http:///service-0-2/polls/ --headless #-u 20 -r 20
