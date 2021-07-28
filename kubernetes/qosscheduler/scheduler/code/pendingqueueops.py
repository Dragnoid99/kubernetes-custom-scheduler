from kubernetes import client, config, watch
import json
import time
import pytz
import datetime
from dateutil import parser
import pickle
from kubernetes.client import configuration
import random
from helpers import cpu_convert, mem_convert, get_pod_object, get_deployment, is_valid_pod, is_valid_node

# Import Kubernetes configurations
config.load_incluster_config()
v1 = client.CoreV1Api()


# Function to create pending queue
def create_pending_queue():

  IST = pytz.timezone('Asia/Calcutta')

  pending_queue = []
  # Watch the events
  w = watch.Watch()

  for event in w.stream(v1.list_pod_for_all_namespaces, timeout_seconds=1):
    # Check if the pod is scheduled or not
    if event['object'].status.phase == 'Pending' and event['object'].spec.node_name == None and event['object'].spec.scheduler_name == "qos-scheduler":
      # If the pod is valid pod the put it in pending queue
      if is_valid_pod(event['object'].metadata.name) == True:
        pending_queue.append(event['object'])

  return pending_queue


# Sort the pending queue
def sort_pending_queue(pending_queue, pod_qos):
  # Currently sorting algorithm is Bubble Sort
  for i in range(len(pending_queue)):
    for j in range(len(pending_queue) - 1):
      if pod_qos[get_deployment(
          pending_queue[j].metadata.name)] > pod_qos[get_deployment(
              pending_queue[j + 1].metadata.name)]:
        temp = pending_queue[j + 1]
        pending_queue[j + 1] = pending_queue[j]
        pending_queue[j] = temp
  return pending_queue
