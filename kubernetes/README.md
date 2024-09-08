# Cluster Setup for Lurnen Product

## Cluster Information

The cluster for this project has been set up through [DigitalOcean](https://cloud.digitalocean.com/).

### Cluster Specifications
- **Kubernetes Version**: v1.30.2
- **Nodes**: 2-node cluster
- **CPU**: 2 virtual CPUs
- **Memory**: 8 GB
- **Storage**: 100 GB disk space

### Cluster Apps and Connections
- **Docker Hub** via Docker Secret
- **nginx Ingress Controller** (namespace: `nginx`)
- **Jetstack Cert Manager** (namespace: `cert-manager`)
- **PostgreSQL Database** (namespace: `postgres`)

---

## Docker Hub Integration

To allow Kubernetes manifests to access the container repository, a secret must be provided to the cluster. 

For this project, [Docker Hub](https://hub.docker.com/) is used. A secret named `docker.secret` was created to store the `.dockerconfigjson` file, which is referenced in the Kubernetes objects.

---

## Nginx Ingress Controller and Load Balancer

### Overview
The Nginx Ingress Controller enables external users to access services within the cluster.

- **Ingress Controller**: A proxy that serves as a gateway for cluster services. It listens to ingress objects (`ingress.yaml`) and updates the Nginx configuration accordingly, enabling the redirection of external traffic to internal Kubernetes services based on domain/path combinations.

### Pre-Installation
Ensure compatibility between the Nginx version and the Kubernetes cluster by referencing the compatibility matrix on the [Nginx GitHub Repo](https://github.com/kubernetes/ingress-nginx/). The chart version used is `4.11.1`, which corresponds to the Nginx app version `1.11.1`.

### Installation Steps
The following steps are automated via [GitHub Actions](https://github.com/arrodi/lurnen_cluster/blob/main/.github/workflows/nginx_deploy.yml/):
1. Add the [Nginx Helm chart repo](https://kubernetes.github.io/ingress-nginx) to the Helm client.
2. Create a Helm template specifying the Nginx version and the target namespace.
3. Deploy the Helm template to the Kubernetes cluster.

### Post-Installation
Once the Load Balancer is initialized, use its External IP to create an A record in the DNS settings of your domain provider ([GoDaddy](https://www.godaddy.com/)).

---

## Jetstack Cert Manager

### Overview
Cert Manager automates the management of TLS certificates, ensuring secure traffic to the server.

- **Cert Manager**: A Kubernetes add-on that provisions and manages TLS certificates from Let’s Encrypt or other certificate authorities. Certificates are configured by annotating Ingress resources and configuring Issuers or ClusterIssuers.

### Installation Steps
The installation is automated via [GitHub Actions](https://github.com/arrodi/lurnen_cluster/blob/main/.github/workflows/cert_manager_deploy.yml/):
1. Add the [Jetstack Helm chart repo](https://charts.jetstack.io) to the Helm client.
2. Install the Cert Manager Helm chart, which deploys the Cert Manager components (`cert-manager`, `cert-manager-cainjector`, `cert-manager-webhook`).
3. Apply the `ClusterIssuer` object to the cluster.

### Post-Installation
Ensure all Ingress objects in the cluster have the annotation `cert-manager.io/cluster-issuer: letsencrypt` for proper TLS configuration.

---

## PostgreSQL Database Setup

### Overview
To handle persistent data and facilitate microservices, several Kubernetes resources are set up around a PostgreSQL pod.

### Pre-Installation
Before deploying the PostgreSQL image, apply the following Kubernetes objects:
1. Create a dedicated [namespace](https://github.com/arrodi/lurnen_cluster/blob/main/postgres/namespace_postgres.yaml) for PostgreSQL.
2. Create a [Persistent Volume](https://github.com/arrodi/lurnen_cluster/blob/main/postgres/persistentvolume.yaml) to persist data on the cluster.

### Installation Steps
These steps are automated via [GitHub Actions](https://github.com/arrodi/lurnen_cluster/blob/main/.github/workflows/postgres_deploy.yml):
1. Create secrets for PostgreSQL connections.
2. Create a [Persistent Volume Claim](https://github.com/arrodi/lurnen_cluster/blob/main/postgres/persistentvolumeclaim.yaml) for the PostgreSQL pod.
3. Deploy the official PostgreSQL image as a [StatefulSet](https://github.com/arrodi/lurnen_cluster/blob/main/postgres/statefulset.yaml).
4. Deploy the [Service](https://github.com/arrodi/lurnen_cluster/blob/main/postgres/service.yaml) object for internal connections.

### Post-Installation
Access the PostgreSQL database using the credentials from the secret configuration. Use the PostgreSQL service name and port for connections.

---