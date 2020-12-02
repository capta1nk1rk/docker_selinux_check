import re
import os
import os.path
from flask import Flask

app = Flask(__name__, static_url_path = "", static_folder = "/static")

class SE_checker:
    # Constructor
    def __init__(self):
        # Instance Vars
        self.hostname_path = "/etc/hostname"
        self.hostname_file = ""
        self.selinux_config_path = "/etc/selinux/config"
        self.selinux_config_file = ""
        self.selinux_current_status = "***SELINUX NOT ENABLED***"

        # Error Checking
        self.error_occurred_selinux = False
        self.error_occurred_hostname = False
        
        self.selinux_reader()
        self.hostname_reader()
        self.selinux_check(self.selinux_config_file)

    # Main Functions
    def selinux_reader(self):
        try:
            self.selinux_config_file = open(self.selinux_config_path, 'r')
            self.selinux_config_file = self.selinux_config_file.read().splitlines()
        except IOError:
            self.error_occurred_selinux = True
            self.error_message_selinux = "FILE NOT FOUND"
    
    def hostname_reader(self):
        try:
            self.hostname_file = open(self.hostname_path, 'r')
            self.hostname_file = self.hostname_file.read().splitlines()
        except IOError:
            self.error_occured_hostname = True
            self.error_message_hostname = "FILE NOT FOUND"

    def selinux_check(self, txtfile):
        #self.selinux_current_status
        for line in txtfile:
            if re.match("SELINUX=enabled", line):
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
    if se_checker.error_occurred_hostname is True:
        html += "<p>Hostname of Current Node: " + se_checker.error_message_hostname + "</p>"
    else:
        html += "<p>Hostname of Current Node: " + str(se_checker.hostname_file) + "</p>"
    html += "<p>Full output of SELinux Config: </p>"
    html += "<p>"
    if se_checker.error_occurred_selinux is True:
        html += se_checker.error_message_selinux
    else:
        for line in se_checker.selinux_config_file:
            html += "<p>" + line + "</p>"
    
    return html


# Main
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
