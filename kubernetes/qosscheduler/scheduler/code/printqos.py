from kubernetes import client, config, watch
import json
import time
import pytz
import datetime
import os
from dateutil import parser
import pickle


def printqos():
  dbfile = open('../files/deployment_run_time', 'rb')
  deployment_run_time = pickle.load(dbfile)
  dbfile.close()

  dbfile = open('../files/deployment_pause_time', 'rb')
  deployment_pause_time = pickle.load(dbfile)
  dbfile.close()


  dbfile = open('../files/deployment_qos', 'rb')
  deployment_qos = pickle.load(dbfile)
  dbfile.close()

  print("Run time of all deployments:\n", deployment_run_time, "\n\n")
  print("pause time of all deployments:\n", deployment_pause_time, "\n\n")
  print("QoS of all deployments:\n", deployment_qos, "\n\n")


if __name__ == "__main__":
  printqos()
