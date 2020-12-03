import re
import os
import os.path
import socket
from flask import Flask

app = Flask(__name__, static_url_path = "", static_folder = "/static")

class FileParser:
    # Constructor
    def __init__(self, path):
        # init error var
        self.error_occurred = False

        # start reader
        self.file_reader(path)

    # Read in file, split string into a list
    # Catch error if file not found
    def file_reader(self, path):
        try:
            self.file = open(path, 'r')
            self.file = self.file.read().splitlines()
        except IOError:
            self.error_occurred = True
            self.error_message = "FILE NOT FOUND"

class SE_checker:
    # Constructor
    def __init__(self):

        # Relevant File Paths to pass to reader
        self.container_hostname_path = "/etc/hostname"
        self.node_hostname_path = "/etc/nodehostname"
        self.namespace_path = "/var/run/secrets/kubernetes.io/serviceaccount/namespace"
        self.selinux_config_path = "/etc/selinux/config"
        self.container_runtime_path = "/var/run/systemd/container"
    
        # Default Status to False:
        self.selinux_current_status = "***SELINUX NOT ENABLED***"

        # Create objects, parse files
        self.container_hostname_parser = FileParser(self.container_hostname_path)
        self.node_hostname_parser = FileParser(self.node_hostname_path)
        self.namespace_parser = FileParser(self.namespace_path)
        self.selinux_parser = FileParser(self.selinux_config_path)
        self.container_runtime_parser = FileParser(self.container_runtime_path)
        
        # Check SEStatus of Config File
        self.selinux_check(self.selinux_parser.file)

    # Parse info in selinux config
    def selinux_check(self, txtfile):
        #self.selinux_current_status
        for line in txtfile:
            if re.match("SELINUX=enforcing", line):
                self.selinux_current_status = "***SELINUX ENABLED***"
        print(self.selinux_current_status)

@app.route('/')
def main_webpage():
    se_checker = SE_checker()
    status_image = "/xmark.png"
    if se_checker.selinux_current_status == "***SELINUX ENABLED***":
        status_image = "/checkmark.jpg"
    html = "<h2>" + str(se_checker.selinux_current_status) + "</h2>"
    html += "<img src=\"%s\">" % status_image

    # Start Table
    html += "<table style=\"width:80%\">"

    # Grab and Display Node Hostname
    if se_checker.node_hostname_parser.error_occurred is True:
        html += "<tr><td><b>Hostname of Current Node (via /etc/hostname): </b></td><td>" + se_checker.node_hostname_parser.error_message + "</td></tr>"
    else:
        html += "<tr><td><b>Hostname of Current Node (via /etc/hostname): </b></td><td>" + str(se_checker.node_hostname_parser.file) + "</td></tr>"
    
    # Grab and Display Container Hostname
    if se_checker.container_hostname_parser.error_occurred is True:
        html += "<tr><td><b>Hostname of Current Container (via /etc/hostname): </b></td><td>" + se_checker.container_hostname_parser.error_message + "</td></tr>"
        html += "<tr><td><b>Hostname of Current Container (via socket): </b></td><td>" + socket.gethostname() + "</td></tr>"
    else:
        html += "<tr><td><b>Hostname of Current Container (via /etc/hostname): </b></td><td>" + str(se_checker.container_hostname_parser.file) + "</td></tr>"
        html += "<tr><td><b>Hostname of Current Container (via socket): </b></td><td>" + socket.gethostname() + "</td></tr>"

    # Grab and Display IP:
    html += "<tr><td><b>IP Address of Current Container: </b></td><td>" + socket.gethostbyname(socket.gethostname()) + "</td></tr>"

    # Grab and Display Namespace
    if se_checker.namespace_parser.error_occurred is True:
        html += "<tr><td><b>Namespace of Current Pod/Deployment: </b></td><td>" + str(se_checker.namespace_parser.error_message) + "</td></tr>"
    else:
        html += "<tr><td><b>Namespace of Current Pod/Deployment: </b></td><td>" + str(se_checker.namespace_parser.file) + "</td></tr>"

    # Grab and Display Container Runtime
    if se_checker.container_runtime_parser.error_occurred is True:
        html += "<tr><td><b>Container Runtime Engine: </b></td><td>" + str(se_checker.container_runtime_parser.error_message) + "</td></tr>"
    else:
        html += "<tr><td><b>Container Runtime Engine: </b></td><td>" + str(se_checker.container_runtime_parser.file) + "</td></tr>"

    # End of table
    html += "</table>"

    # Display output of SELinux Config
    html += "<br><p><b>Full output of SELinux Config:</b></p>"
    html += "<p>"
    if se_checker.selinux_parser.error_occurred is True:
        html += se_checker.selinux_parser.error_message
    else:
        for line in se_checker.selinux_parser.file:
            html += "<p>" + line + "</p>"
    
    return html

# Main
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
