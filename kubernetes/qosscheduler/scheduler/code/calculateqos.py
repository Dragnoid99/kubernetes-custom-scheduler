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
from helpers import cpu_convert, mem_convert, get_pod_object, get_deployment, is_valid_pod, is_valid_node
from calculateqoshelper import get_pod_deployments, get_pod_creation_timestamps, get_deployment_slos, get_pod_deletion_timestamps

# Import Kubernetes configurations
config.load_incluster_config()
v1 = client.CoreV1Api()

# Returns the logs of all events of the cluster
def _generate_logs():
  pod_namespace = "kube-system"
  pods = v1.list_namespaced_pod('kube-system')

  # Obtain the pod_name of the pod of deployment eventrouter
  for pod in pods.items:
    if len(pod.metadata.name)>=11 and pod.metadata.name[:11] == "eventrouter":
      pod_name = pod.metadata.name

  # Read the logs of the pod
  logs = v1.read_namespaced_pod_log(name=pod_name, namespace=pod_namespace)
  log_string = ""

  cnt_level = 0
  count_entry = 0
  tmp_json_list = []
  json_list = []
  tmp_list = []
  
  # is_message keeps the flag entry for is we are inside the key or value in key-value pair
  is_message = 0
  orig_date = datetime.datetime(1970,1,1,tzinfo = datetime.timezone.utc)
  
  # Parse the logs of eventrouter as string
  for i in range(len(logs)):
    # in_entry keeps the flag which stores if it is in some json entry
    in_entry = 0

    if cnt_level!=0 and logs[i] == "\"" and logs[i-1] != "\\":
      if is_message == 1:
        is_message = 0
      else:
        is_message = 1
    
    if is_message == 1:
      log_string += logs[i]
      continue
    
    if logs[i] == '{':
      cnt_level += 1

    if cnt_level != 0:
      in_entry = 1
      log_string += logs[i]

    if logs[i] == '}':
      cnt_level -= 1

    if cnt_level == 0 and in_entry == 1:
      try:
        # In this case, one of the entries of logs has been parsed and it's corresponding string form is stored in log_string
        json_obj = json.loads(log_string)
        log_string = ""
        json_obj2 = {}
        json_obj2['action'] = json_obj['event']['reason']
        json_obj2['involvedObject'] = json_obj['event']['involvedObject']['name']
        json_obj2['timestamp'] = json_obj['event']['firstTimestamp']
        if json_obj2['timestamp'] !=  None:
          tmp_list.append(((parser.parse(json_obj['event']['firstTimestamp'])-orig_date).total_seconds(), count_entry))
          tmp_json_list.append(json_obj2)
          count_entry += 1
      except:
        pass

  tmp_list.sort()

  for i in range(len(tmp_list)):
    json_list.append(tmp_json_list[tmp_list[i][1]])

  return json_list

# Returns the pod qos
def get_all_pod_qos(slo):

  IST = pytz.timezone('Asia/Calcutta')

  # Generate a file with logs of all the logs of the cluster
  json_list = _generate_logs()

  # Stores timestamp, pod_names, actions of all events obtained by querying loki
  timestamps = []
  pod_names = []
  action = []

  for obj in json_list:
    timestamps.append(parser.parse(obj['timestamp']))
    action.append(obj['action'])
    try:
      pod_names.append(obj['involvedObject'])
    except:
      pod_names.append("none")

  # If we can't find creation_timestamp of some pod then assume it started running from default_time
  default_time = timestamps[0]


  pod_creation = get_pod_creation_timestamps()
  pod_deployment = get_pod_deployments()
  deployment_slo = get_deployment_slos(pod_deployment, slo)
  pod_deletion, pods_active, new_pods_active = get_pod_deletion_timestamps()


  # whether this is the first scheduling of the pod
  whether_created = {}
  # State of the pod, 'Running' if the pod is scheduled, 'Pending', if the pod is waiting to be scheduled
  pod_state = {}
  # Last timestamp when pod went to the running state
  pod_start_time = {}
  # Last timestamp when pod went to Pending state
  pod_end_time = {}

  # Runtime and pause time of the deployments
  deployment_run_time = {}
  deployment_pause_time = {}
  deployment_qos_metric = {}
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



  # Initialize the deployment_run_time and deployment_pause_time of all deployments
  for pod in pod_deployment:
    dep = pod_deployment[pod]
    deployment_run_time[dep] = 0.0
    deployment_pause_time[dep] = 0.0
    deployment_qos_metric[dep] = 0.0
    deployment_qos[dep] = 0.0


  # For new pods
  for pod in new_pods_active:
    if pod not in pod_end_time:
      pod_state[pod] = 'Paused'
      pod_end_time[pod] = pod_creation[pod]


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
          pod_state[pod_names[i]] = 'Paused'
          pod_end_time[pod_names[i]] = pod_creation[pod_names[i]]

        # If the pod changed it's state then update it's state and increment deployment_pause_time of it's deployment
        if pod_state[pod_names[i]] != 'Running':
          deployment_pause_time[pod_deployment[pod_names[i]]] += (timestamps[i] - pod_end_time[pod_names[i]]).total_seconds()
          pod_start_time[pod_names[i]] = timestamps[i]
          pod_state[pod_names[i]] = 'Running'

      # SandboxChanged and Killing denotes that it has been put to the pending state
      if action[i] == "Killing" or action[i] == "SandboxChanged":
        # If the pod is running for the first time then initialize some of it's values
        if pod_names[i] not in whether_created:
          whether_created[pod_names[i]] = 1
          pod_state[pod_names[i]] = 'Paused'
          pod_end_time[pod_names[i]] = pod_creation[pod_names[i]]

        # If the pod changed it's state then update it's state and increment deployment_run_time of it's deploment
        elif pod_state[pod_names[i]] != 'Paused':
          deployment_run_time[pod_deployment[pod_names[i]]] += (timestamps[i] - pod_start_time[pod_names[i]]).total_seconds()
          pod_end_time[pod_names[i]] = timestamps[i]
          pod_state[pod_names[i]] = 'Paused'
    except:
      pass


  # For the pods that have not been marked inactive yet and are inactive, mark them as inactive and calulate the remaining deployment_run_time/deployment_pause_time
  # For the pods that are still active, update their deployment_run_time/deployment_pause_time
  for pod in pod_deployment:
    if is_valid_pod(pod) == False:
      continue
    try:
      if pod not in pod_deletion:
        if pod_state[pod] == 'Running':
          deployment_run_time[pod_deployment[pod]] += (datetime.datetime.now(tz = IST) - pod_start_time[pod]).total_seconds()
        else:
          deployment_pause_time[pod_deployment[pod]] += (datetime.datetime.now(tz = IST) - pod_end_time[pod]).total_seconds()

      else:
        if pod_state[pod] == 'Running':
          deployment_run_time[pod_deployment[pod]] += (pod_deletion[pod] - pod_start_time[pod]).total_seconds()

        else:
          deployment_pause_time[pod_deployment[pod]] += (pod_deletion[pod] - pod_end_time[pod]).total_seconds()
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
    
      deployment_qos[dep] = deployment_run_time[dep]/(deployment_run_time[dep]+deployment_pause_time[dep]+0.000000001)
      deployment_qos_metric[dep] = deployment_run_time[dep]/(deployment_slo[dep]+0.000000001) - (deployment_run_time[dep] + deployment_pause_time[dep])
    
    except:
      pass

  print("\n\nDeployment Qos = ", deployment_qos_metric, "\n")
  print("Run time = ", deployment_run_time, "\n")
  print("Pause time = ", deployment_pause_time, "\n")

  dbfile = open('../files/deployment_run_time', 'wb')
  pickle.dump(deployment_run_time, dbfile)
  dbfile.close()

  dbfile = open('../files/deployment_pause_time', 'wb')
  pickle.dump(deployment_pause_time, dbfile)
  dbfile.close()

  dbfile = open('../files/deployment_qos', 'wb')
  pickle.dump(deployment_qos, dbfile)
  dbfile.close()

  dbfile = open('../files/deployment_qos_metric', 'wb')
  pickle.dump(deployment_qos_metric, dbfile)
  dbfile.close()


  return deployment_qos_metric
