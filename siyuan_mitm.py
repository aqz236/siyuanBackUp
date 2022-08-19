from mitmproxy.http import flow
import os, socket, fcntl, struct, subprocess

port=6807
targetApi="/api/self/backup/alipan"
nic="eth0"
if nic not in os.listdir('/sys/class/net/'):
    print(os.listdir('/sys/class/net/'))
    print("你的网卡名可能有错误，需要手动进行修改\n同时/etc/sysconfig/iptables中添加的两条自定义规则也要改")

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    inet = fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', bytes(ifname[:15], 'utf-8')))
    return socket.inet_ntoa(inet[20:24])


def request(flow: flow):
    if f"http://{get_ip_address(nic)}:{port}{targetApi}" in flow.request.url:
        subprocess.Popen("sh backup.sh", shell=True)