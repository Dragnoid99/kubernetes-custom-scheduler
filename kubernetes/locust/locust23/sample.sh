#!/bin/bash
locust -f locustfile.py --host http:///service-2-3/polls/ --headless #-u 20 -r 20
