# Offline\_RKE2\_Install\_SUSE.md

## \_ \_ \_

## \| \| \_\_\_\_\_ \_\_\_\_\_\(\_\) \_\_\| \| \_\_\_

## \| \|/ \_ \ \ /\ / / \_\_\| \|/ \_\` \|/ \_ \

## \| \| \(_\) \ V V /\__ \ \| \(\_\| \| \_\_/

## \|_\|\_**/ \_/\_/ \|**_/_\|\__,\_\|\_\_\_\|

## download rke2 rpms and images

This follows the same process from [https://rancherfederal.com/blog/installing-rke-government-in-airgap-environments/](https://rancherfederal.com/blog/installing-rke-government-in-airgap-environments/)

```text
mkdir RKE_Dependencies
docker run --rm \
-v $(pwd)/RKE_Dependencies:/mnt \
-w /mnt centos:7 \
/bin/bash -c \
"curl -sfL https://gist.githubusercontent.com/mddamato/45efeb226b5109fb72a7a7289a943bf3/raw | bash -"
```

## k9s is so necessary

```text
wget https://github.com/derailed/k9s/releases/download/v0.24.2/k9s_Linux_x86_64.tar.gz
```

## download helm binary

```text
wget https://get.helm.sh/helm-v3.5.0-linux-amd64.tar.gz
```

## download Rancher images

```text
wget https://github.com/rancher/rancher/releases/download/v2.5.5/rancher-images.txt
wget https://github.com/rancher/rancher/releases/download/v2.5.5/rancher-save-images.sh
wget https://github.com/rancher/rancher/releases/download/v2.5.5/rancher-load-images.sh
```

### chmod +x rancher-save-images.sh ; ./rancher-save-images.sh --image-list rancher-images.txt

\#pull the helm chart

```text
helm repo add rancher-latest https://releases.rancher.com/server-charts/latest && helm repo update
helm fetch rancher-latest/rancher --version=2.5.5 # -> rancher-2.5.5.tgz
```

## \_ \_

## \_\_ _\(_\)\_ \_\_ \_\_ \_ \_\_ \_ \_ \_\_ \| \|\_\_ \_\_\_\_\_ \_\_

## / _`| | '__/ _` \|/ \` \| '_ \| ' \ / \_ \ / /

## \| \(_\| \| \| \| \| \(_\| \| \(_\| \| \|_\) \| \|_\) \| \(_\) &gt; &lt;

## \__,_\|_\|_\| \__, \|\__,_\| .\_\_/\|_.**/ \_**/\_/\_\

## \|\_\__/ \|_\|

### airgap

### disable firewalld

```text
systemctl stop firewalld & systemctl disable firewalld
```

## create rke2 config file

```text
mkdir -p /etc/rancher/rke2
echo "selinux:false" > /etc/rancher/rke2/config.yaml
```

## install rke2

This is similar to [https://rancherfederal.com/blog/installing-rke-government-in-airgap-environments/](https://rancherfederal.com/blog/installing-rke-government-in-airgap-environments/) but with some modifications to work with zypper. This is not the ideal solution but works for now. An all Zypper solution would be much better.

```text
tar xzvf rke-government-deps-*.tar.gz

mkdir -p /var/lib/rancher/rke2/agent/images/ && \
zcat rke2-images.linux-amd64.tar.gz > /var/lib/rancher/rke2/agent/images/rke2-images.linux-amd64.tar

mkdir -p /var/lib/rancher/yum_repos
tar xzf rke_rpm_deps.tar.gz -C /var/lib/rancher/yum_repos
cat > /var/lib/rancher/rke_rpm_deps.repo <
```

