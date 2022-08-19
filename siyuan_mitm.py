from mitmproxy.http import flow
import socket, fcntl, struct, subprocess

port=6807
targetApi="/api/self/backup/alipan"

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    inet = fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', bytes(ifname[:15], 'utf-8')))
    return socket.inet_ntoa(inet[20:24])


def request(flow: flow):
    if f"http://{get_ip_address('eth0')}:{port}{targetApi}" in flow.request.url:
        subprocess.Popen("sh backup.sh", shell=True)
