# Instantiating a RKE2 cluster on machines with multiple network interfaces

I**ntroduction:** 

In many scenarios, you could be deploying RKE2 to a machine with multiple network interfaces.  Perhaps your environment requires a separate management network, or a separate public facing network, along with a high-speed internal network to handle Kubernetes traffic.  In any case, there are certain steps to be taken during the instantiation of both RKE2 High Availability clusters and RKE2 agents in a multi-nic scenario to make the process as easy as possible. 

#### **Initial Assumptions:** 

For this example, we are going to assume you are using a homogeneous network environment.  What does that mean?  Essentially, all servers and agents for your RKE2 cluster should have a similar network setup and interfaces.  For example, if “node1” contains three NICs \(perhaps a public facing net, management net, and Kubernetes traffic net\), then it will make things much smoother if “node2” also has the same NIC setup.  Although theoretically possible, heterogeneous networks are not currently recommended as a deployment option for RKE2 based clusters, so we will focus on a homogenous network for now. 

{% hint style="warning" %}
#### **Caveat:** 

Currently, as of 12/18/20, only static ips \(or statically assigned DHCP leases\) are supported for clusters built with RKE2.  Particularly if operating in a cloud environment, make sure your machines have static IPs associated with the NIC that you expect to use for Kubernetes traffic, so we can set the node-ip and advertise addresses properly for the configuration that RKE2 will use. 
{% endhint %}

####  

{% page-ref page="test.md" %}

#### **Initial Server Configuration:** 

Let us assume the following example network setup for this scenario.  We are going to create an RKE2 High Availability cluster on the following machines: 

| Name:  | Eth0 \(Management\) IP:  | Eth1 \(Kubernetes Traffic\) IP:  | Eth3 \(Intranet Traffic\) IP:  |
| :--- | :--- | :--- | :--- |
| node1  | 192.168.1.101  | 10.20.50.11  | 172.16.0.201  |
| node2  | 192.168.1.102  | 10.20.50.12  | 172.16.0.202  |
| node3  | 192.168.1.103  | 10.20.50.13  | 172.16.0.203  |

Don’t worry about the actual IP addresses, or the number of NICs, or the things the NICs are being used for above.  This is simply an example to better explain the scenario.  The main point here is that we have an interface, Eth1 in this case, that we intended to use for all RKE2/Kubernetes traffic.  We shouldn’t assume that Eth1 is the default network in this case, in fact, let’s assume all default routes go through Eth0, the management network instead. 

How do we deploy RKE2 properly in this setup?  It is easier than you may expect.  First, install rke2 using the method of your choice, whether that be the \(recommended\) RPM based install, the tarball, or the direct binary.  Make sure this is a **clean** setup.  If RKE2, K3S, or other Kubernetes runtimes have been installed on the machine previously, it is highly suggested that you use a fresh image.  If that is not possible for your scenario, skip to the “How to clean up an existing cluster” section. 

Before we even think about running the RKE2 server, we need to make a few configuration changes to the cluster.yml. 

Go ahead and open `/etc/rancher/rke2/config.yaml` using the editor of your choice.  If you are following along with the High Availability install guide, then at minimum, it’s a good idea to configure the “tls-san” field to set the alternative names for the server cert, with the IPs and DNS names you want to add in there.  Ideally, you would stick to DNS/hostnames for the san fields, but in the instances that you need to access the cluster directly from the IP address instead, IP addresses can be added as well to that field.  At this point, if you wish to add your own token, you could.  Or simply omit the entire option, to let RKE2 generate a random token for you. 

The **important** thing we need to add to this configuration is the addition of two fields.  Namely, “advertise-address”, and “node-ip”: 

![blobid0.png](https://support.rancherfederal.com/hc/article_attachments/1500000571161/blobid0.png)

These values should be set to the ip address associated with the network that you wish to use for Kubernetes traffic.  In this case, we wish to have all traffic travel over Eth1, and we are setting up the first node, so this will be set to 10.20.50.11 in our case. 

The “advertise-address” is the IP address that the apiserver uses to advertise to other members of the cluster.  By default, this value uses the IP address in “node-ip”, so technically this field can be omitted in many cases.  However, for this scenario, I wanted to explicitly call it out, just to advertise its function. 

The “node-ip” field is the IP address to advertise the node itself.  By setting these two fields, the various components of RKE2 should have just about everything they need to instantiate a cluster.  If you would like to see all the options available for RKE2 Server and Agent nodes, take a look at the following docs: 

[https://docs.rke2.io/install/install\_options/server\_config/](https://docs.rke2.io/install/install_options/server_config/) 

[https://docs.rke2.io/install/install\_options/agent\_config/](https://docs.rke2.io/install/install_options/agent_config/) 

But wait! 

Before we start an RKE2 server, there is one further change we must make to ensure a successful multi-NIC HA cluster.  We actually need to customize the CNI network plugin of our cluster before deployment, to ensure that all internal pod traffic occurs over the correct NIC. 

See the doc here for the full writeup: 

[https://docs.rke2.io/install/network\_options/\#canal-options](https://docs.rke2.io/install/network_options/#canal-options) 

Using the documentation above, create a rke2-canal-config.yml using the editor of your choice.  For now, we can create this file in any directory, and we will copy it later to the manifest's directory.  In our scenario, the Canal config should look something like this: 

![blobid1.png](https://support.rancherfederal.com/hc/article_attachments/1500000571201/blobid1.png)

Finally, we need to create the manifests directory for rke2, and copy our new configuration into this directory.  RKE2 will automatically grab the files located in the manifests directory and apply them, it’s almost like running a “kubectl apply –f", except the directory is constantly monitored and requires no additional user input.  Neat! 

Now that everything is in place for our first node, we can go ahead and start our RKE2 server.  If you installed via the RPM method, then a simple 

```bash
sudo systemctl enable –now rke2-server.service
```

should suffice.  If using the binary, then you will need to start the server manually, using"

```bash
rke2 server –c nameofyourconfig.yml
```

After a few minutes, the RKE2 server should be up and running. 

#### **Additional Server Node Configuration:** 

When using a High-Availability cluster for RKE2 \(which is highly recommended\), it is at this point that you would add additional server nodes.  The additional server nodes are instantiated nearly exactly the same as the first server node, with a few minor differences. 

Go ahead and copy the configuration that was created earlier for the first node to your second machine.  A few fields need to be added.  An additional “server” parameter, which should contain the IP or DNS name of the initial server.  Also, all subsequent nodes need to have the “token” field populated with the proper values.  If you did not generate your own token during the setup of the first node, you can find the autogenerated token at \(`/var/lib/rancher/rke2/server/node-token`\).  Finally, make sure to edit the advertise-address and node-ip to the proper values associated with your second node. 

For our test scenario, the `/etc/rancher/rke2/config.yaml` will look something like this: 

![blobid2.png](https://support.rancherfederal.com/hc/article_attachments/1500000561202/blobid2.png)

Because the canal CNI has already been deployed and configured via the first node, we do not actually need to modify any configurations for the subsequent nodes.  The first node will autodeploy the required CNI daemonsets on future nodes using the configuration set earlier.  Hence, it is highly suggested that all machines being used for the RKE2 cluster are heterogenous in terms of network configuration as this greatly simplifies deployment. 

Much like the previous server, simply start up RKE2 using the systemctl service or the direct binary.  After a few minutes, you should see the second node appear in your cluster. 

At this point, it is highly suggested to add one more node to achieve cluster quorum for high availability, which can be achieved by using the same steps, and/or viewing the official documentation here: 

[https://docs.rke2.io/install/ha/](https://docs.rke2.io/install/ha/) 

#### **Additional Agent Node Configuration:** 

If you wish to add additional “agent” \(otherwise known as worker\) nodes to your RKE2 cluster, a minor change should occur to the configuration.  Simply remove the advertise-address field in the config.yml, as it is no longer required.  The advertise address is only necessary for server nodes.  The tls-san fields are also not necessary for agent nodes, however it won’t break anything if you leave it there.  Those values will simply be ignored.  For our usecase, the agent node configuration will look something like this: 

![blobid3.png](https://support.rancherfederal.com/hc/article_attachments/1500000561222/blobid3.png)

Much like additional server nodes, simply start up the RKE2 agent using the systemctl service \(rke2-agent\) or the direct binary using the agent argument.  In a few moments, your new agent node should be attached to the cluster! 

####  

#### **How to fully clean up a node \(optional\):** 

To fully clean up a node, first follow the documentation located here: 

[https://docs.rke2.io/install/uninstall/](https://docs.rke2.io/install/uninstall/) 

To make sure everything is completely gone, it’s also recommended to do the following: 

```bash
sudo rm –rf /run/k3s
sudo rm –rf /var/lib/rancher 
```

#### **Conclusion:** 

In this article, we walked through an RKE2 Deployment on machines with multiple NIC interfaces.  Using RKE2 on multi-nic machines is simple but does require a small amount of additional configuration to be successful.  Hopefully, this guide has provided you with confidence of how straightforward it is to use RKE2 in a multi-nic environment. 

## 

## 

## 

## Getting Super Powers

Becoming a super hero is a fairly straight forward process:

```
$ give me super-powers
```

{% hint style="info" %}
 Super-powers are granted randomly so please submit an issue if you're not happy with yours.
{% endhint %}

Once you're strong enough, save the world:

{% code title="hello.sh" %}
```bash
# Ain't no code for that yet, sorry
echo 'You got to trust me on this, I saved the world'
```
{% endcode %}



