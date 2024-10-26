import paramiko
import requests
import time

INFLUXDB_URL = 'http://18.207.204.195:8086/write?db=server_metrics'

def get_metrics(ip, username, private_key):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username=username, key_filename=private_key)

    # Commands to gather metrics
    commands = {
        'cpu': 'cat /proc/stat | grep "cpu "',
        'memory': 'free -m',
        'disk': 'df -h'
    }

    metrics = {}
    for key, cmd in commands.items():
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode()
        metrics[key] = output

    ssh.close()
    return metrics

def format_metrics_to_influx(instance_id, metrics):
    data = f"cpu_usage,host={instance_id} value={metrics['cpu']}\n" \
           f"memory_usage,host={instance_id} value={metrics['memory']}\n" \
           f"disk_usage,host={instance_id} value={metrics['disk']}"
    return data

def send_metrics_to_influxdb(data):
    response = requests.post(INFLUXDB_URL, data=data)
    if response.status_code == 204:
        print("Data successfully written to InfluxDB")
    else:
        print(f"Failed to write to InfluxDB: {response.status_code}, {response.text}")

# Example usage
def monitor_server(ip, instance_id, private_key):
    metrics = get_metrics(ip, 'ubuntu', private_key)
    formatted_data = format_metrics_to_influx(instance_id, metrics)
    send_metrics_to_influxdb(formatted_data)

# Collect metrics from all servers
servers = [
    {"ip": "54.172.223.186", "id": "First_server"},
    # Add more servers here
]

for server in servers:
    monitor_server(server['ip'], server['id'], server['key'])
    time.sleep(5)  # To avoid overloading InfluxDB
