from kubernetes import client, config, watch
import json
import time
import pytz
import datetime
from dateutil import parser
import pickle
from kubernetes.client import configuration
import random
from config import *

from calculateqos import get_all_pod_qos
from helpers import cpu_convert, mem_convert, get_pod_object, get_deployment, is_valid_pod, is_valid_node, calculate_pod_req
from pendingqueueops import create_pending_queue, sort_pending_queue
from selectbestnode import select_node_with_preemption, select_node_without_preemption
from checkfeasibility import feasibility_check
from schedulingpods import preempt_pods, bind_pod_to_node
from getallstats import get_stats_nodes

# Import Kubernetes configurations
config.load_incluster_config()
v1 = client.CoreV1Api()

def scheduler():

  pods_preempted = {}

  # Calculate qos of all pods and store them
  pod_qos = get_all_pod_qos(slo)

  # Create Pending Queue
  pending_queue = create_pending_queue()

  # Sort pending queue
  pending_queue = sort_pending_queue(pending_queue, pod_qos)

  # dictionary which keeps track of pods that are bound to a node
  is_bound = {""}

  for pod in pending_queue:

    pod_name = pod.metadata.name

    # Calculate the requests of the pod
    cpu_req, mem_req = calculate_pod_req(pod)

    nodes_without_preemption = []
    nodes_with_preemption = []

    # Get statistics of all nodes
    cpu_cap, cpu_used, mem_cap, mem_used, list_nodes = get_stats_nodes(
        pods_preempted)

    preempt_pods_dict = {}

    for node in list_nodes:
      if is_valid_node(node) == False:
        continue
      flag, pods_to_preempt = feasibility_check(pod, node, pod_name, cpu_req,
                                                mem_req, cpu_cap[node],
                                                mem_cap[node], cpu_used[node],
                                                mem_used[node], pod_qos,
                                                safety_param, safety_slo,
                                                pods_preempted)
      if flag == False:
        # Node cannot host the pod at any cost
        continue
      if len(pods_to_preempt) == 0:
        nodes_without_preemption.append(node)
      else:
        nodes_with_preemption.append(node)
      preempt_pods_dict[node] = pods_to_preempt

    # If no host is deeemed feasible then skip
    if len(nodes_with_preemption) == 0 and len(nodes_without_preemption) == 0:
      print("Did not bind the pod", pod.metadata.name, "\n")
      continue

    # If there is atleast one node which does not require preemption
    if len(nodes_without_preemption) != 0:
      best_node = select_node_without_preemption(pod, nodes_without_preemption,
                                                 cpu_req, cpu_cap, cpu_used)

    # If all nodes require preemption
    if len(nodes_without_preemption) == 0 and len(nodes_with_preemption) != 0:
      best_node = select_node_with_preemption(pod, nodes_with_preemption,
                                              preempt_pods_dict, pod_qos,
                                              number_of_service_class,
                                              safety_slo)
      pods_preempted = preempt_pods(preempt_pods_dict[best_node],
                                    pods_preempted)

    bind_pod_to_node(pod, best_node)

    is_bound.add(pod.metadata.name)
    print("Bound", pod.metadata.name, "to node", node, "\n")


  pods = v1.list_namespaced_pod("default")

  print("The following pods are not bound till now")
  for pod in pods.items:
    if is_valid_pod(pod.metadata.name) == False:
      continue
    if pod.status.phase == "Pending" and pod.metadata.name not in is_bound:
      print(pod.metadata.name)

pods = v1.list_namespaced_pod("default")
for pod in pods.items:
  if is_valid_pod(pod.metadata.name) == True:
    if pod.status.phase == "Failed":
      try:
        print("OOM, OOC pod = ", pod.metadata.name)
        pods_to_preempt = []
        pods_to_preempt.append(pod)
        z = {}
        pods_preempted = preempt_pods(pods_to_preempt, z)
        print("Successfully Preempted")
      except:
        print("Failed to Preempt")
        pass

  print("\n\n")
  
  
if __name__ == "__main__":
  scheduler()
