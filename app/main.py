import re
from flask import Flask

# Global Vars
app = Flask(__name__, static_url_path = "", static_folder = "/static")
hostname_file = "/etc/hostname"
hostname = ""
selinux_config_file = open('/etc/selinux/config', 'r')
selinux_raw_config_file = "/etc/selinux/config"
selinux = ""
selinux_current_status = "***SELINUX NOT ENABLED***"

# Functions
def get_hostname():
    global hostname
    with open(hostname_file, 'r') as file:
    
        hostname = file.read()
def get_selinux_config():
    global selinux
    with open(selinux_raw_config_file, 'r') as file:
        selinux = file.read()

def selinux_reader(txtfile):
    global selinux_current_status
    for line in txtfile:
        if re.match("SELINUX=enabled", line):
            selinux_current_status = "***SELINUX ENABLED***"
    print(selinux_current_status)

@app.route('/')
def main_webpage():
    status_image = "/xmark.png"
    if selinux_current_status == "***SELINUX ENABLED***":
        status_image = "/checkmark.jpg"
    html = "<h2>" + str(selinux_current_status) + "</h2>"
    html += "<img src=\"%s\">" % status_image
    html += "<p>Hostname of Current Node: " + str(hostname) + "</p>"
    html +="<p>Full output of SELinux Config: </p>"
    html +="<p>" + str(selinux) + "</p>"
    return html


# Main
get_hostname()
get_selinux_config()
selinux_reader(selinux_config_file)
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
