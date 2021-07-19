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

# Function to preempt pods
def preempt_pods(list_of_pods, pods_preempted):

	IST = pytz.timezone('Asia/Calcutta')

	# Preempt pods
	for pod in list_of_pods:
		# # namespace that the pod is running in and the name of the pod
		# pod_namespace = pod.metadata.namespace
		# pod_name = pod.metadata.name
		pod_name = pod.metadata.name
		pod_namespace = "default"
		try:
			response = v1.delete_namespaced_pod(pod_name, pod_namespace)
			print("Preempting pods->", pod.metadata.name)
			print("Successfully preempted", "\n")

			pods_preempted[pod_name] = 1

			# Enter deletion time of this pod in pod_deletion_pickle
			dbfile = open('pod_deletion_pickle', 'rb')
			pod_deletion = pickle.load(dbfile)
			dbfile.close()

			dbfile = open('pod_deletion_pickle', 'wb')

			# Enter deletion time in the dict
			time = datetime.datetime.now(tz = IST)
			pod_deletion[pod_name] = time

			# Update the pod deletion timestamp in the pod_deletion_pickle file 
			pickle.dump(pod_deletion, dbfile)
			dbfile.close()

		except:
			print("Could not preempt pod ", pod_name, " in the namespace ", pod_namespace, "\n")

	return pods_preempted


# Binds the pod to the node
def bind_pod_to_node(pod, node, namespace = "default"):
	pod_name = pod.metadata.name
	target = client.V1ObjectReference()
	target.kind = "Node"
	target.apiVersion = "v1"
	target.name = node

	meta = client.V1ObjectMeta()
	meta.name = pod_name

	body = client.V1Binding(target=target)

	body.metadata = meta

	resp = v1.create_namespaced_binding(namespace, body, _preload_content=False)

	return resp