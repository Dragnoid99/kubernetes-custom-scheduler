from kubernetes import client, config, watch
import json
import time
import pytz
import datetime
from dateutil import parser
import pickle
from kubernetes.client import configuration
import random
from helpers import cpu_convert, mem_convert, get_pod_object, get_deployment, is_valid_pod, is_valid_node, is_smaller, is_equal, time_difference

# Import Kubernetes configurations
config.load_incluster_config()
v1 = client.CoreV1Api()

# Function to return the stats of all nodes and the list of available nodes which can host pods
def get_stats_nodes(pods_preempted):

	# Import configuration
	config.load_incluster_config()
	v1 = client.CoreV1Api()


	list_node = v1.list_node()
	avail_nodes = []
	cpu_cap = {}
	cpu_used = {}
	mem_cap = {}
	mem_used = {}

	for node in list_node.items:
		if is_valid_node(node.metadata.name) == False:
			continue
		for status in node.status.conditions:
			if status.status != "True" or status.type != "Ready":
				# The node is not suitable for hosting any pod
				continue

			# Convert memory and CPU to default units
			# Note down the cpu and memory capacities of the node
			cpu_cap[node.metadata.name] = cpu_convert(node.status.capacity["cpu"])
			mem_cap[node.metadata.name] = mem_convert(node.status.capacity["memory"])

			# keep track which nodes can host pod right now
			avail_nodes.append(node.metadata.name)

			cpu_used[node.metadata.name] = 0.0
			mem_used[node.metadata.name] = 0.0

			# Computing CPU used, memory used by pods in the node
			field_selector = 'spec.nodeName=' + node.metadata.name
			ret = v1.list_pod_for_all_namespaces(watch = False, field_selector = field_selector)
			for pod in ret.items:
				if pod.metadata.name in pods_preempted:
					continue
				for container in pod.spec.containers:
					try:
						cpu_used[node.metadata.name] += cpu_convert(container.resources.requests['cpu'])
						mem_used += mem_convert(container.resources.requests['memory'])
					except:
						pass


	# The actual cpu and memory used in the node. It is currently disabled to be used this way...

	# api = client.CustomObjectsApi()
	# # Update the memory and cpu already used of the node
	# k8s_nodes = api.list_cluster_custom_object("metrics.k8s.io","v1beta1","nodes")
	# for stats in k8s_nodes['items']:
	# 	cpu_used[stats['metadata']['name']] = cpu_convert(stats['usage']['cpu'])
	# 	mem_used[stats['metadata']['name']] = mem_convert(stats['usage']['memory'])

	return cpu_cap, cpu_used, mem_cap, mem_used, avail_nodes
