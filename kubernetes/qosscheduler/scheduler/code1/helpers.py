from kubernetes import client, config, watch
import json
import time
import pytz
import datetime
from dateutil import parser
import pickle
from kubernetes.client import configuration
import random

# Import Kubernetes configurations
config.load_incluster_config()
v1 = client.CoreV1Api()

# Convert everything to milli cpu
def cpu_convert(s):
	ret = 0.0
	if s[-1] == 'm':
		ret = float(s[:-1])
	elif s[-1] == 'n':
		ret = float(s[:-1])*0.000001
	else:
		ret = float(s)*1000
	return ret

# Convert everything to Ki
def mem_convert(s):
	if s[-2:] == "Ki":
		return float(s[:-2])
	elif s[-2:] == "Mi":
		return float(s[:-2])*1024
	elif s[-2:] == "Gi":
		return float(s[:-2])*1024*1024 


# Get pod object corresponding to pod name
def get_pod_object(pod_name):
	pod_object = v1.read_namespaced_pod(pod_name, "default")
	return pod_object

# Get the deployment corresponding to the pod
def get_deployment(pod_name):
	pod_object = get_pod_object(pod_name)
	if pod_object.metadata.generate_name == None:
		# See this case
		return pod_name
	else:
		try:
			# deployment name + hash = pod_generate_name
			pod_gen_name = pod_object.metadata.generate_name
			pod_hash = ""
			pod_hash = "-"+pod_object.metadata.labels['pod-template-hash']+"-"
			length = len(pod_hash)

			# Remove the hash from the pod name
			deploy_name = pod_gen_name[:-length]
			return deploy_name
		except:
			return None

# Returns true, if it is valid pod_name that is, either it starts with pod- or dep-
def is_valid_pod(pod_name):
	if len(pod_name)<4:
		return False
	if pod_name[:4] != "pod-" and pod_name[:4] != "dep-":
		return False
	return True

# Returns true if we can scheduler pod on the node
def is_valid_node(node_name):
	return True


# is_equal(x, y) returns true if absolute difference between x, y < 1e-9
def is_equal(x, y):
	if x-y <= 0.000000001:
		return True
	elif x-y >= -0.000000001:
		return True
	else:
		return False


# is_smaller(tuple1, tuple2) returns True if tuple1 is lexicographically smaller than tuple2 else it returns False
def is_smaller(tuple1, tuple2):
	for i in range(len(tuple1)):
		if is_equal(tuple1[i], tuple2[i]):
			continue
		elif tuple1[i] < tuple2[i]:
			return True
		elif tuple1[i] > tuple2[i]:
			return False
	return False


# Gives the time difference between time x and y
def time_difference(x, y):
	diff = (x-y).days*24*3600 + (x-y).seconds
	return diff

# Calculate pod requests
def calculate_pod_req(pod):
	# Calculate cpu and memory requested by the pod which is equal to sum or requests of all containers
	for container in pod.spec.containers:
		cpu_req += cpu_convert(container.resources.requests['cpu'])
		mem_req += mem_convert(container.resources.requests['memory'])