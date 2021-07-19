from kubernetes import client, config, watch
import json
import time
import pytz
import datetime
from dateutil import parser
import pickle
from kubernetes.client import configuration
import random

# Container packing algorithm based on CPU
def container_packing_algorithm(pod, nodes, cpu_req, cpu_cap, cpu_used):

  # Set the margins for low and high usage node
  low = float(0.3)
  high = float(0.7)

  low_nodes = {}
  medium_nodes = {}
  high_nodes = {}

  # Divide the nodes in 3 categories, low usage nodes, medium usage nodes and high usage nodes based on their cpu utilization
  for node in nodes:
    try:
      util = cpu_used[node]/cpu_cap[node]
      if util<=low:
        low_nodes[node] = util
      elif util<=high:
        medium_nodes[node] = util
      else :
        high_nodes[node] = util
    
    except:
      pass
  
  best_node = ""

  max_util = 0

  # First try to select node from medium utilization nodes
  for node in medium_nodes:
    if medium_nodes[node] > max_util :
      max_util = medium_nodes[node]
      best_node = node

  # If there is no node available in medium utilization node, then try to select from low utilization nodes
  if best_node == "":
    for node in low_nodes:
      if low_nodes[node] > max_util :
        max_util = low_nodes[node]
        best_node = node

  # If there is no node available in low, medium utilization node, then try to select from high utilization nodes    
  if best_node == "":
    min_util = 1e20
    for node in high_nodes:
      if high_nodes[node] < min_util :
        min_util = high_nodes[node]
        best_node = node

  return best_node