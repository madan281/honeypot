import socket
import threading
import paramiko
import datetime
import logging
from logging.handlers import RotatingFileHandler
import time
from pathlib import Path

# Get the current directory
base_dir = Path(__file__).parent

# File paths
server_key_path = base_dir / 'static' / 'server.key'
creds_log_path = base_dir / 'log_files' / 'creds_audits.log'
cmd_log_path = base_dir / 'log_files' / 'cmd_audits.log'

# Load SSH host key
host_key = paramiko.RSAKey(filename=str(server_key_path))

# Set up logging
formatter = logging.Formatter('%(message)s')

creds_logger = logging.getLogger('CredsLogger')
creds_logger.setLevel(logging.INFO)
creds_handler = RotatingFileHandler(str(creds_log_path), maxBytes=2000, backupCount=5)
creds_handler.setFormatter(formatter)
creds_logger.addHandler(creds_handler)

funnel_logger = logging.getLogger('FunnelLogger')
funnel_logger.setLevel(logging.INFO)
funnel_handler = RotatingFileHandler(str(cmd_log_path), maxBytes=2000, backupCount=5)
funnel_handler.setFormatter(formatter)
funnel_logger.addHandler(funnel_handler)

SSH_BANNER = "SSH-2.0-MySSHServer_1.0"

# Paramiko SSH Server class
class Server(paramiko.ServerInterface):
    def __init__(self, client_ip, input_username=None, input_password=None):
        self.event = threading.Event()
        self.client_ip = client_ip
        self.input_username = input_username
        self.input_password = input_password

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED

    def get_allowed_auths(self, username):
        return "password"

    def check_auth_password(self, username, password):
        creds_logger.info(f'{self.client_ip}, {username}, {password}')
        funnel_logger.info(f'Client {self.client_ip} attempted login with username="{username}" password="{password}"')
        if self.input_username and self.input_password:
            if username == self.input_username and password == self.input_password:
                return paramiko.AUTH_SUCCESSFUL
            else:
                return paramiko.AUTH_FAILED
        return paramiko.AUTH_SUCCESSFUL

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True

    def check_channel_exec_request(self, channel, command):
        return True

# Simulated shell interface
def emulated_shell(channel, client_ip):
    channel.send(b"corporate-jumpbox2$ ")
    command = b""
    while True:
        try:
            char = channel.recv(1)
            if not char:
                break
            channel.send(char)
            command += char
            if char == b"\r":
                clean = command.strip().decode()
                if clean == "exit":
                    channel.send(b"\nGoodbye!\n")
                    channel.close()
                    break
                elif clean == "pwd":
                    response = b"\n/usr/local\n"
                elif clean == "whoami":
                    response = b"\ncorpuser1\n"
                elif clean == "ls":
                    response = b"\njumpbox1.conf\n"
                elif clean == "cat jumpbox1.conf":
                    response = b"\nGo to deeboodah.com\n"
                else:
                    response = b"\nCommand not found: " + command.strip() + b"\n"

                funnel_logger.info(f'Command "{clean}" executed by {client_ip}')
                channel.send(response)
                channel.send(b"corporate-jumpbox2$ ")
                command = b""

        except OSError as e:
            print(f"[WARN] Socket closed during shell interaction: {e}")
            break


# Handle a single client connection
def client_handle(client, addr, username, password, tarpit=False):
    client_ip = addr[0]
    print(f"{client_ip} connected.")

    try:
        transport = paramiko.Transport(client)
        transport.local_version = SSH_BANNER
        transport.add_server_key(host_key)

        server = Server(client_ip=client_ip, input_username=username, input_password=password)
        transport.start_server(server=server)

        channel = transport.accept(100)
        if channel is None:
            print("No channel was opened.")
            return
        emulated_shell(channel, client_ip=client_ip)
    except paramiko.ssh_exception.SSHException as e:
        if "Error reading SSH protocol banner" in str(e):
            print(f"[SKIPPED] Likely non-SSH traffic from {client_ip}")
        else:
            print(f"[SSH ERROR] {e}")
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")

        
        if tarpit:
            banner = "Welcome to Ubuntu 22.04 LTS (Jammy Jellyfish)!\r\n\r\n"
            for char in banner * 10:
                try:
                    channel.send(char.encode())
                    time.sleep(0.1)
                except:
                    break
        else:
            channel.send(banner.encode())

        emulated_shell(channel, client_ip=client_ip)

    except Exception as e:
        print(f"[EXCEPTION] {e.__class__.__name__}: {e}")
    finally:
        try:
            transport.close()
        except:
            pass
        client.close()

# ✅ Main honeypot function
def honeypot(address, port, username, password, tarpit=False):
    socks = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socks.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    socks.bind((address, port))
    socks.listen(100)
    print(f"SSH server is listening on port {port}.")

    while True:
        try:
            client, addr = socks.accept()
            thread = threading.Thread(target=client_handle, args=(client, addr, username, password, tarpit))
            thread.start()
        except Exception as e:
            print(f"!!! Error accepting connection: {e} !!!")

#honeypot('127.0.0.1', 2222, username=None, password=None)
