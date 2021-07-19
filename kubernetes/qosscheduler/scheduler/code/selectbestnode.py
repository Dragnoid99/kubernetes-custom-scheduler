from kubernetes import client, config, watch
import json
import time
import pytz
import datetime
from dateutil import parser
import pickle
from kubernetes.client import configuration
import random
from containerpackingalgo import container_packing_algorithm
from helpers import cpu_convert, mem_convert, get_pod_object, get_deployment, is_valid_pod, is_valid_node, is_smaller, is_equal, time_difference

# Import Kubernetes configurations
config.load_incluster_config()
v1 = client.CoreV1Api()


# Select best node if there are nodes which do not require preemption
def select_node_without_preemption(pod, nodes, cpu_req, cpu_cap, cpu_used):

  # Using the container packing algorithm
  best_node = container_packing_algorithm(pod, nodes, cpu_req, cpu_cap, cpu_used)
  return best_node


# Select best node if there are no nodes which do not require preemption
def select_node_with_preemption(pod, nodes, preempt_pods_dict, pod_qos, number_of_service_class, safety_slo):

  node_tuple = {}
  m = number_of_service_class

  # Calculate tuples for each of the nodes  
  for node in nodes:

    # temp_tuple represents tuple for the node node
    temp_tuple = []

    # Initialize everything to zero
    for i in range(m+1):
      temp_tuple.append(0)

    # Update the tuple for each of the pods to be preempted
    for pod_to_preempt in preempt_pods_dict[node]:
      service_class = int(pod_to_preempt.metadata.labels['service_class'])
      if pod_qos[get_deployment(pod_to_preempt.metadata.name)] >= safety_slo[service_class]:
        temp_tuple[m] += pod_qos[get_deployment(pod_to_preempt.metadata.name)] - safety_slo[service_class]
      else:
        temp_tuple[service_class] += (pod_qos[get_deployment(pod_to_preempt.metadata.name)] - safety_slo[service_class])

    # Ensure no value is zero to avoid division-by-zero error
    for i in range(m):
      if temp_tuple[i] == 0:
        temp_tuple[i] -= 0.000000001

    if temp_tuple[m] == 0:
      temp_tuple[m] += 0.000000001

    for i in range(m+1):
      temp_tuple[i] = 1.0/temp_tuple[i]

    # Stores to key value pair (node, temp_tuple) in the dictionary
    node_tuple[node] = temp_tuple

  # Shuffle the nodes randomly to induce the randomization effect
  random.sample(nodes, len(nodes))

  # Initialize best node as node[0] and smallest_tuple to the tuple corresponding to node[0]
  best_node = nodes[0]
  smallest_tuple = node_tuple[nodes[0]]

  # Select node which will have the smallest tuple value
  for node in nodes:
    # is_smaller(tuple1, tuple2) will return True if tuple1 is lexicographically smaller than tuple2
    if is_smaller(node_tuple[node], smallest_tuple) == True:
      best_node = node
      smallest_tuple = node_tuple[node]

  # Returns the best_node
  return best_node