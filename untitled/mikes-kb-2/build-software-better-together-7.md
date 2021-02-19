# Build software better, together

 @@ -1,10 +1,14 @@  
 \# low side  
 \#\# make directory for all your dependencies: \`\`\` mkdir RKE\_Dependencies \`\`\`  
 \#\# download rke2 rpms and images This follows the same process from https://rancherfederal.com/blog/installing-rke-government-in-airgap-environments/ \`\`\` mkdir RKE\_Dependencies docker run --rm \ -v $\(pwd\)/RKE\_Dependencies:/mnt \ -w /mnt centos:7 \ @@ -13,30 +17,58 @@ docker run --rm \ \`\`\` This just collects RPMs from centos repos, outputs a tar with images, RPMs, and preconfigured rpm repo  
  
 \#\# k9s is so necessary \`\`\` wget https://github.com/derailed/k9s/releases/download/v0.24.2/k9s\_Linux\_x86\_64.tar.gz curl -LO https://github.com/derailed/k9s/releases/download/v0.24.2/k9s\_Linux\_x86\_64.tar.gz mv k9s\_Linux\_x86\_64.tar.gz RKE\_Dependencies/ \`\`\`  
 \#\# download helm binary \`\`\` wget https://get.helm.sh/helm-v3.5.0-linux-amd64.tar.gz curl -LO https://get.helm.sh/helm-v3.5.0-linux-amd64.tar.gz mv helm-v3.5.0-linux-amd64.tar.gz RKE\_Dependencies/ \`\`\`  
 \#\# download Rancher images This takes a long time but downloads all the combinations of rancher related images. Ideally you would only ship a subset of these if you know the specific versions of features/images you intend to use. Run all three of these commands on the online box with docker.  
 \`\`\`shell curl -LO https://github.com/rancher/rancher/releases/download/v2.5.5/rancher-images.txt curl -LO https://github.com/rancher/rancher/releases/download/v2.5.5/rancher-load-images.sh curl -sfL https://github.com/rancher/rancher/releases/download/v2.5.5/rancher-save-images.sh \| bash - \`\`\` wget https://github.com/rancher/rancher/releases/download/v2.5.5/rancher-images.txt wget https://github.com/rancher/rancher/releases/download/v2.5.5/rancher-save-images.sh wget https://github.com/rancher/rancher/releases/download/v2.5.5/rancher-load-images.sh  
 \`\`\`shell mv rancher-images.txt RKE\_Dependencies/ mv rancher-load-images.sh RKE\_Dependencies/ mv rancher-images.tar.gz RKE\_Dependencies/ \`\`\` \#\#\# chmod +x rancher-save-images.sh ; ./rancher-save-images.sh --image-list rancher-images.txt  
 \#\# pull the helm chart  
 \#\# pull the helm chart files install helm if you don't have it already \`\`\` helm repo add rancher-latest https://releases.rancher.com/server-charts/latest && helm repo update helm fetch rancher-latest/rancher --version=2.5.5 \# -&gt; rancher-2.5.5.tgz curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 \| bash \`\`\`  
 \`\`\` curl -LO https://github.com/jetstack/cert-manager/releases/download/v1.0.4/cert-manager.crds.yaml helm repo add rancher-latest https://releases.rancher.com/server-charts/latest helm repo add jetstack https://charts.jetstack.io helm repo update helm fetch rancher-latest/rancher --version=2.5.5 helm fetch jetstack/cert-manager --version v1.0.4 mv rancher-2.5.5.tgz RKE\_Dependencies/ mv cert-manager-v1.0.4.tgz RKE\_Dependencies/ mv cert-manager.crds.yaml RKE\_Dependencies/ \`\`\`  
 \#\# send all files into airgap \`\`\` scp RKE\_Dependencies/\* user@rke2-server.com:/home/user \`\`\`  
  
 \# airgap @@ -74,4 +106,30 @@ EOF zypper addrepo /var/lib/rancher/rke\_rpm\_deps.repo zypper --plus-content="rke\_rpm\_deps" --non-interactive install --replacefiles rke2-server \`\`\`  \`\`\`  
 \#\# Untar rancher images \`\`\` zcat rancher-images.tar.gz &gt; /var/lib/rancher/rke2/agent/images/rancher-images.tar \`\`\` &gt; restart rke2-server if you've already started it \`systemctl restart rke2-server\` \#\# Start rke2-server \`\`\` systemctl start rke2-server systemctl enable rke2-server export KUBECONFIG=/etc/rancher/rke2/rke2.yaml export PATH=$PATH:/var/lib/rancher/rke2/bin:/usr/local/bin export CRI\_CONFIG\_FILE=/var/lib/rancher/rke2/agent/etc/crictl.yaml alias ku=kubectl journalctl -u rke2-server -f \`\`\`  
 \#\# install rancher  
 kubectl apply -f cert-manager.crds.yaml tar xvf helm-v3.5.0-linux-amd64.tar.gz kubectl create ns cert-manager kubectl create ns cattle-system linux-amd64/helm install cert-manager cert-manager-v1.0.4.tgz --namespace cert-manager --version v1.0.4 linux-amd64/helm install rancher rancher-2.5.5.tgz --namespace cattle-system --set hostname=rancher.example.com 

