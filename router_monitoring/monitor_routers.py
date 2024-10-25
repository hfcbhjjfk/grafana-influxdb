from influxdb import InfluxDBClient
from pysnmp.hlapi import *
import time

def get_router_metric(ip, community, oid):
    iterator = getCmd(SnmpEngine(),
                      CommunityData(community),
                      UdpTransportTarget((ip, 161)),
                      ContextData(),
                      ObjectType(ObjectIdentity(oid)))
    error_indication, error_status, error_index, var_binds = next(iterator)
    if error_indication:
        print(f"Error: {error_indication}")
        return None
    else:
        for var_bind in var_binds:
            return float(var_bind.prettyPrint().split('=')[-1].strip())

def write_to_influxdb(device_name, metric_name, value):
    client = InfluxDBClient(host='localhost', port=8086, database='network_metrics')
    json_body = [
        {
            "measurement": metric_name,
            "tags": {"device": device_name},
            "fields": {"value": value}
        }
    ]
    client.write_points(json_body)

# Define router details
routers = {
    'router1': {'ip': '192.168.1.1', 'community': 'public', 'oids': {'cpu': '1.3.6.1.4.1.x.y.z'}},
    'router2': {'ip': '192.168.1.2', 'community': 'public', 'oids': {'cpu': '1.3.6.1.4.1.x.y.z'}},
    # Add more routers as needed
}

# Main function to collect and send data
while True:
    for router, details in routers.items():
        cpu_usage = get_router_metric(details['ip'], details['community'], details['oids']['cpu'])
        if cpu_usage is not None:
            write_to_influxdb(router, 'cpu_usage', cpu_usage)
    time.sleep(300)  # Run every 5 minutes

