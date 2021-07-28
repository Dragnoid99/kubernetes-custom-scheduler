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


def get_pod_deployments():

  # Get the corresponding deployment names of all pods running
  dbfile = open('../files/deployment_pickle', 'rb')
  pod_deployment = pickle.load(dbfile)
  dbfile.close()

  dbfile = open('../files/deployment_pickle', 'wb')

  pods = v1.list_namespaced_pod('default')

  # Update the deployment names of pods are running and which was not updated earlier
  for pod in pods.items:
    if is_valid_pod(pod.metadata.name) == False:
      continue
    if pod.metadata.name not in pod_deployment:
      if pod.metadata.generate_name == None:
        pod_deployment[pod.metadata.name] = pod.metadata.name
      else:
        try:
          pod_gen_name = pod.metadata.generate_name
          pod_hash = '-' + pod.metadata.labels['pod-template-hash'] + '-'
          length = len(pod_hash)

          deploy_name = pod_gen_name[:-length]
          pod_deployment[pod.metadata.name] = deploy_name

        except:
          pass

  # Update the deployments of the pods in the file
  pickle.dump(pod_deployment, dbfile)
  dbfile.close()

  return pod_deployment


def get_pod_creation_timestamps():

  # Load the file which contains all pods creation timestamp
  dbfile = open('../files/pod_creation_pickle', 'rb')
  pod_creation = pickle.load(dbfile)
  dbfile.close()

  dbfile = open('../files/pod_creation_pickle', 'wb')
  pods = v1.list_namespaced_pod('default')

  # Update the creation timestamp of pods that were created recently
  for pod in pods.items:
    if is_valid_pod(pod.metadata.name) == False:
      continue
    if pod.metadata.name not in pod_creation:
      time = pod.metadata.creation_timestamp
      # Note, we have to convert UTC to IST as all LOKI timestamps are in IST
      pod_creation[
          pod.metadata.name] = time  #+ datetime.timedelta(hours=5, minutes=30)

  # Update the creation timestamps of pod in the file
  pickle.dump(pod_creation, dbfile)
  dbfile.close()

  return pod_creation


def get_deployment_slos(pod_deployment, slo):

  # Get the service class of all pods and note down in deployment slo
  dbfile = open('../files/deployment_slo', 'rb')
  deployment_slo = pickle.load(dbfile)
  dbfile.close()

  dbfile = open('../files/deployment_slo', 'wb')
  pods = v1.list_namespaced_pod('default')
  # Update deployment_slo for the current running pods
  for pod in pods.items:
    if is_valid_pod(pod.metadata.name) == False:
      continue
    # try:
    dep = pod_deployment[pod.metadata.name]
    if dep not in deployment_slo:
      deployment_slo[dep] = slo[int(pod.metadata.labels['service_class'])]
    # except:
    #   pass

  # Dump the new deployment_slo in the deployment_slo file
  pickle.dump(deployment_slo, dbfile)
  dbfile.close()

  return deployment_slo


def get_pod_deletion_timestamps():

  IST = pytz.timezone('Asia/Calcutta')

  # Keep track of the pods that are active
  dbfile = open('../files/pods_active_pickle', 'rb')

  # pods_active is the active pod list of the last iteration of this function
  pods_active = pickle.load(dbfile)
  dbfile.close()

  dbfile = open('../files/pods_active_pickle', 'wb')

  # new_pods_active is the dictionary of pods that are currently active
  new_pods_active = {}
  pods = v1.list_namespaced_pod('default')
  for pod in pods.items:
    if is_valid_pod(pod.metadata.name) == False:
      continue
    new_pods_active[pod.metadata.name] = 1

  # Update the pods_active_pickle with the pods that are active now
  pickle.dump(new_pods_active, dbfile)
  dbfile.close()

  # pod_deletion_pickle keeps track of deletion time of all the pods
  dbfile = open('../files/pod_deletion_pickle', 'rb')
  pod_deletion = pickle.load(dbfile)
  dbfile.close()

  dbfile = open('../files/pod_deletion_pickle', 'wb')

  # The pods that were active in last function call but are not active now are treated as deleted and their deleted timestamp is the current time timestamp
  # Max error of the difference in deletion timestamp = time period of calling this function
  for pod in pods_active:
    if pod not in new_pods_active and pod not in pod_deletion:
      time = datetime.datetime.now(tz=IST)
      pod_deletion[pod] = time

  # Update the pod deletion timestamp in the pod_deletion_pickle file
  pickle.dump(pod_deletion, dbfile)
  dbfile.close()

  return pod_deletion, pods_active, new_pods_active
