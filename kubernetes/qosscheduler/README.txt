The main code of the scheduler is in the directory scheduler/code and the main function in in scheduler.py. In order to run the scheduler, just run the script qosschedulerscript.sh, it will run the scheduler periodically.

In order to host the scheduler on a pod in kubernetes cluster, change the load_kube_config() to load_incluster_config() and give it the administrative permissions of the cluster. 
