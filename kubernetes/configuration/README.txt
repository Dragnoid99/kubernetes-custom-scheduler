This directory contains all the configuration files for the Kubernetes Cluster. This directory contains the following folders ->

deployments: This directory contains all the deployments that can be deployed in the cluster. Each of them gets scheduled by the custom scheduler and have a service class associated to it. The naming of deployments is deployment-<service_class>-<instance_no>. For example deployment-i-j is the jth deployment with service class i.

deploymentservices: This directory contains services that exposes the deployments of the cluster. The naming convention of the services in this directory is service-<deployment_name>.yaml. Ex. the service service-deployment-0-1.yaml is the service that exposes the deployment-0-1.yaml.

podautoscaling: This directory contains horizontal pod autoscalers corresponding to each of the deployment. autoscaler-<deployment_name>.yaml is the autoscaler corresponding to <deployment_name>.yaml. For example autoscaler-deployment-0-1.yaml is the autoscaler for the deployment-0-1.yaml

roles: This directory contains all the roles with administrative permissions of the cluster.

services: This directory contains all the services that maybe needed to ensure the custom scheduler runs perfectly like the loki-ingress.yaml that hosts the loki using ingress service to be accessible to the scheduler.
