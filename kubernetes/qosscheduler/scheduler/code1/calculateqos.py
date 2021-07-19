from kubernetes import client, config, watch
import json
import time
import pytz
import datetime
import os
from dateutil import parser
import pickle
from kubernetes.client import configuration
import random
from helpers import cpu_convert, mem_convert, get_pod_object, get_deployment, is_valid_pod, is_valid_node, is_smaller, is_equal, time_difference
from calculateqoshelper import get_pod_deployments, get_pod_creation_timestamps, get_deployment_slos, get_pod_deletion_timestamps

# Import Kubernetes configurations
config.load_incluster_config()
v1 = client.CoreV1Api()

# Returns the pod qos
def get_all_pod_qos(slo):

	IST = pytz.timezone('Asia/Calcutta')

	# Initialize the loki address,  "http://192.168.49.2" is the minikube address
	os.environ['LOKI_ADDR'] = "http://192.168.49.2"

	# Query from loki and store in a json file, with limit being 1e12 and starting time as some time in 2006
	os.system("logcli query '{app=\"events-collector\"}' --limit=1000000000000 --output=jsonl --from=2006-01-02T15:04:05.999999999Z --forward > ../logs/logs.json")

	objlist = []

	# Stores timestamp, pod_names, actions of all events obtained by querying loki
	timestamps = []
	pod_names = []
	action = []


	# Processing logs.json and extracting timestamps, pod_names, actions from them
	with open('../logs/logs.json') as f:
		for jsonObj in f:
			temp = json.loads(jsonObj)
			objlist.append(temp)

	for obj in objlist:
		timestamps.append(parser.parse(obj['timestamp']))
		line = obj['line']
		line = line.split()
		action.append(line[2])
		pod_names.append(line[3][4:])

	# If we can't find creation_timestamp of some pod then assume it started running from default_time
	default_time = timestamps[0]
	

	pod_creation = get_pod_creation_timestamps()
	pod_deployment = get_pod_deployments()
	deployment_slo = get_deployment_slos(pod_deployment, slo)
	pod_deletion, pods_active, new_pods_active = get_pod_deletion_timestamps()


	# whether this is the first scheduling of the pod
	whether_created = {}
	# State of the pod, 1 if the pod is running else 0
	state_of_pod = {}
	# Last timestamp when pod went to the running state
	start_time = {}
	# Last timestamp when pod went to Pending state
	end_time = {}
	
	# Runtime and pause time of the deployments
	run_time = {}
	pause_time = {}
	deployment_qos = {}




	# Nullify it when simulating
	# To tackle any possible errors like the pods that were deployed before start of the loki
	for i in range(len(action)):
		if is_valid_pod(pod_names[i]) == False: 
			continue
		if pod_names[i] not in pod_creation:
			pod_creation[pod_names[i]] = default_time
		if pod_names[i] not in pod_deployment:
			pod_deployment[pod_names[i]] = "_"



	# Initialize the run_time and pause_time of all deployments
	for pod in pod_deployment:
		dep = pod_deployment[pod]
		run_time[dep] = 0.0
		pause_time[dep] = 0.0
		deployment_qos[dep] = 0.0


	# For new pods
	for pod in new_pods_active:
		if pod not in end_time:
			state_of_pod[pod] = 0
			end_time[pod] = pod_creation[pod]


	# Process the entries of logs one by one
	for i in range(len(action)):
		if is_valid_pod(pod_names[i]) == False:
			continue

		# To be cautious, put it in try, except
		try:
			# Pulling and scheduled denotes that pod has been scheduled
			if action[i] == "Pulling" or action[i] == "Scheduled":
				# If the pod is running for the first time then initialize some of it's values
				if pod_names[i] not in whether_created:
					whether_created[pod_names[i]] = 1
					state_of_pod[pod_names[i]] = 0
					end_time[pod_names[i]] = pod_creation[pod_names[i]]

				# If the pod changed it's state then update it's state and increment pause_time of it's deployment
				if state_of_pod[pod_names[i]] != 1:
					pause_time[pod_deployment[pod_names[i]]] += time_difference(timestamps[i], end_time[pod_names[i]])
					start_time[pod_names[i]] = timestamps[i]
					state_of_pod[pod_names[i]] = 1

			# SandboxChanged and Killing denotes that it has been put to the pending state
			if action[i] == "Killing" or action[i] == "SandboxChanged":
				# If the pod is running for the first time then initialize some of it's values
				if pod_names[i] not in whether_created:
					whether_created[pod_names[i]] = 1
					state_of_pod[pod_names[i]] = 0
					end_time[pod_names[i]] = pod_creation[pod_names[i]]

				# If the pod changed it's state then update it's state and increment run_time of it's deploment 
				elif state_of_pod[pod_names[i]] != 0:
					run_time[pod_deployment[pod_names[i]]] += time_difference(timestamps[i],start_time[pod_names[i]])
					end_time[pod_names[i]] = timestamps[i]
					state_of_pod[pod_names[i]] = 0
		except:
			pass
			

	# For the pods that have not been marked inactive yet and are inactive, mark them as inactive and calulate the remaining run_time/pause_time
	# For the pods that are still active, update their run_time/pause_time
	for pod in pod_deployment:
		if is_valid_pod(pod) == False:
			continue
		try:
			if pod not in pod_deletion:
				if state_of_pod[pod] == 1:
					run_time[pod_deployment[pod]] += time_difference(datetime.datetime.now(tz = IST), start_time[pod])
				else:
					pause_time[pod_deployment[pod]] += time_difference(datetime.datetime.now(tz = IST), end_time[pod])

			else:
				if state_of_pod[pod] == 1:
					run_time[pod_deployment[pod]] += time_difference(pod_deletion[pod], start_time[pod])

				else:
					pause_time[pod_deployment[pod]] += time_difference(pod_deletion[pod], end_time[pod])
		except:
			pass

	# Calculate TTV, Recoveribility of the pods
	for pod in pod_deployment:
		try:
			if is_valid_pod(pod) == False:
				continue

			dep = pod_deployment[pod]
			
			if is_valid_pod(dep) == False:
				continue
			
			deployment_qos[dep] = run_time[dep]/(deployment_slo[dep]+0.000000001) - (run_time[dep] + pause_time[dep])
		except:
			pass
		
	print("\n\nDeployment Qos = ", deployment_qos, "\n")
	print("Run time = ", run_time, "\n")
	print("Pause time = ", pause_time, "\n")

	return deployment_qos
