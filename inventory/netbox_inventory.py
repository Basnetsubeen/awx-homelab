#!/usr/bin/env python3
import os
import json
import requests

NETBOX_URL = "http://192.168.99.20"
NETBOX_TOKEN = "your-new-netbox-token"

headers = {
    "Authorization": f"Token {NETBOX_TOKEN}",
    "Content-Type": "application/json",
}

def get_devices():
    url = f"{NETBOX_URL}/api/dcim/devices/?status=active&limit=1000"
    response = requests.get(url, headers=headers, verify=False)
    return response.json()["results"]

def build_inventory():
    devices = get_devices()
    inventory = {
        "_meta": {"hostvars": {}},
        "all": {"hosts": [], "children": []},
    }

    for device in devices:
        name = device["name"]
        ip = None

        if device.get("primary_ip4"):
            ip = device["primary_ip4"]["address"].split("/")[0]

        inventory["all"]["hosts"].append(name)
        inventory["_meta"]["hostvars"][name] = {
            "ansible_host": ip or name,
            "device_role": device["device_role"]["slug"],
            "site": device["site"]["slug"] if device.get("site") else "",
            "platform": device["platform"]["slug"] if device.get("platform") else "",
        }

    return inventory

if __name__ == "__main__":
    print(json.dumps(build_inventory(), indent=2))
