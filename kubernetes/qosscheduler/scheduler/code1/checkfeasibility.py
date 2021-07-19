from kubernetes import client, config, watch
from helpers import cpu_convert, mem_convert, get_pod_object, get_deployment, is_valid_pod, is_valid_node, is_smaller, is_equal, time_difference

# Import Kubernetes configurations
config.load_incluster_config()
v1 = client.CoreV1Api()

# Checks if pod2 can be preempted by pod1
def can_preempt(pod1, pod2, pod_qos, safety_slo):
	try:

		# There are 3 simple situations where pod1 can preempt pod2
		pod1_dep = get_deployment(pod1.metadata.name)
		pod2_dep = get_deployment(pod2.metadata.name)
		pod1_obj = pod1
		pod2_obj = pod2

		if pod_qos[pod1_dep]<pod_qos[pod2_dep] and pod_qos[pod2_dep]>safety_slo[int(pod2_obj.metadata.labels['service_class'])]:
			return True

		if int(pod1_obj.metadata.labels['service_class'])<int(pod2_obj.metadata.labels['service_class']) and pod_qos[pod1_dep]<safety_slo[int(pod1_obj.metadata.labels['service_class'])]:
			return True

		if int(pod1_obj.metadata.labels['service_class'])==int(pod2_obj.metadata.labels['service_class']) and pod_qos[pod1_dep]<pod_qos[pod2_dep]:
			return True

	except:
		pass

	return False


# Checks if the node can host the pod, if yes then which pods does it need to preempt (if any?)
def feasibility_check(pod, node, pod_name, pod_cpu, pod_mem, cpu_cap, mem_cap, cpu_used, mem_used, pod_qos, safety_param, safety_slo, pods_preempted):
	
	# Currently checking for only resources and not any other placement constraints 
	# Initialize pods_to_preempt as empty
	pods_to_preempt = []

	# Check if preemption is not required
	if cpu_used + pod_cpu <= safety_param*cpu_cap and mem_used + pod_mem <= safety_param*mem_cap:
		return True, pods_to_preempt

	# Get all pods running in the node
	pods_running_in_node = []
	field_selector = 'spec.nodeName=' + node
	ret = v1.list_pod_for_all_namespaces(watch = False, field_selector = field_selector)

	# Now, get all pods running in default namespace
	for po in ret.items:
		# Check if the pod has been preempted already
		if po.metadata.name in pods_preempted:
			continue
		if po.metadata.namespace == 'default' and is_valid_pod(po.metadata.name):
			pods_running_in_node.append(po)

	# Try to preempt pods running in current node one by one
	for pod_running in pods_running_in_node:
		# Check if the pod_running is valid
		if is_valid_pod(pod_running.metadata.name) == False:
			continue
		# Check if pod can preempt pod_running which is running in node node
		if can_preempt(pod, pod_running, pod_qos, safety_slo):
			pods_to_preempt.append(pod_running)

			# If pod_running is preempted then all it's resources will also be freed
			for container in pod_running.spec.containers:
				cpu_used -= cpu_convert(container.resources.requests['cpu'])
				mem_used -= mem_convert(container.resources.requests['memory'])

			# Check if there are enough resources available to host the pod
			if cpu_used + pod_cpu <= safety_param*cpu_cap and mem_used + pod_mem <= safety_param*mem_cap:
				break


	# Finally check if all the preemptions, the pod can be hosted or not
	if cpu_used + pod_cpu <= safety_param*cpu_cap and mem_used + pod_mem <= safety_param*mem_cap:
		return True, pods_to_preempt

	# If function reaches this point then the pod cannot be hosted on the node
	return False, pods_to_preempt