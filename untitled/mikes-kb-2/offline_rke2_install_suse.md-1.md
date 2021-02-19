# Offline\_RKE2\_Install\_SUSE.md

## low side

### make directory for all your dependencies:

```text
mkdir RKE_Dependencies
```

### download rke2 rpms and images

This follows the same process from [https://rancherfederal.com/blog/installing-rke-government-in-airgap-environments/](https://rancherfederal.com/blog/installing-rke-government-in-airgap-environments/)

```text
docker run --rm \
-v $(pwd)/RKE_Dependencies:/mnt \
-w /mnt centos:7 \
/bin/bash -c \
"curl -sfL https://gist.githubusercontent.com/mddamato/45efeb226b5109fb72a7a7289a943bf3/raw | bash -"
```

This just collects RPMs from centos repos, outputs a tar with images, RPMs, and preconfigured rpm repo

### k9s is so necessary

```text
curl -LO https://github.com/derailed/k9s/releases/download/v0.24.2/k9s_Linux_x86_64.tar.gz
mv k9s_Linux_x86_64.tar.gz RKE_Dependencies/
```

### download helm binary

```text
curl -LO https://get.helm.sh/helm-v3.5.0-linux-amd64.tar.gz
mv helm-v3.5.0-linux-amd64.tar.gz RKE_Dependencies/
```

### download Rancher images

This takes a long time but downloads all the combinations of rancher related images. Ideally you would only ship a subset of these if you know the specific versions of features/images you intend to use. Run all three of these commands on the online box with docker.

```text
curl -LO https://github.com/rancher/rancher/releases/download/v2.5.5/rancher-images.txt
curl -LO https://github.com/rancher/rancher/releases/download/v2.5.5/rancher-load-images.sh
curl -sfL https://github.com/rancher/rancher/releases/download/v2.5.5/rancher-save-images.sh | bash -
```

```text
mv rancher-images.txt RKE_Dependencies/
mv rancher-load-images.sh RKE_Dependencies/
mv rancher-images.tar.gz RKE_Dependencies/
```

### pull the helm chart files

install helm if you don't have it already

```text
curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash
```

```text
curl -LO https://github.com/jetstack/cert-manager/releases/download/v1.0.4/cert-manager.crds.yaml
helm repo add rancher-latest https://releases.rancher.com/server-charts/latest
helm repo add jetstack https://charts.jetstack.io
helm repo update
helm fetch rancher-latest/rancher --version=2.5.5
helm fetch jetstack/cert-manager --version v1.0.4

mv rancher-2.5.5.tgz RKE_Dependencies/
mv cert-manager-v1.0.4.tgz RKE_Dependencies/
mv cert-manager.crds.yaml RKE_Dependencies/
```

### send all files into airgap

```text
scp RKE_Dependencies/* user@rke2-server.com:/home/user
```

## airgap

### disable firewalld

```text
systemctl stop firewalld & systemctl disable firewalld
```

### create rke2 config file

```text
mkdir -p /etc/rancher/rke2
echo "selinux: false" > /etc/rancher/rke2/config.yaml
```

### install rke2

This is similar to [https://rancherfederal.com/blog/installing-rke-government-in-airgap-environments/](https://rancherfederal.com/blog/installing-rke-government-in-airgap-environments/) but with some modifications to work with zypper. This is not the ideal solution but works for now. An all Zypper solution would be much better.

```text
tar xzvf rke-government-deps-*.tar.gz

mkdir -p /var/lib/rancher/rke2/agent/images/ && \
zcat rke2-images.linux-amd64.tar.gz > /var/lib/rancher/rke2/agent/images/rke2-images.linux-amd64.tar

mkdir -p /var/lib/rancher/yum_repos
tar xzf rke_rpm_deps.tar.gz -C /var/lib/rancher/yum_repos
cat > /var/lib/rancher/rke_rpm_deps.repo <
```

### `Untar rancher images`

```text
zcat rancher-images.tar.gz > /var/lib/rancher/rke2/agent/images/rancher-images.tar
```

> restart rke2-server if you've already started it `systemctl restart rke2-server`

### Start rke2-server

```text
systemctl start rke2-server
systemctl enable rke2-server
export KUBECONFIG=/etc/rancher/rke2/rke2.yaml
export PATH=$PATH:/var/lib/rancher/rke2/bin:/usr/local/bin
export CRI_CONFIG_FILE=/var/lib/rancher/rke2/agent/etc/crictl.yaml
alias ku=kubectl
journalctl -u rke2-server -f
```

### install rancher

kubectl apply -f cert-manager.crds.yaml tar xvf helm-v3.5.0-linux-amd64.tar.gz kubectl create ns cert-manager kubectl create ns cattle-system linux-amd64/helm install cert-manager cert-manager-v1.0.4.tgz --namespace cert-manager --version v1.0.4 linux-amd64/helm install rancher rancher-2.5.5.tgz --namespace cattle-system --set hostname=rancher.example.com

