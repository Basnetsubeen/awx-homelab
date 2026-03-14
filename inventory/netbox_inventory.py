#!/usr/bin/env python3
import os
import json
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

NETBOX_URL = "http://192.168.99.20"
NETBOX_TOKEN = "8bcdd2cf53d3a5dcb451cef76ce5329b74423520"

headers = {
    "Authorization": f"Token {NETBOX_TOKEN}",
    "Content-Type": "application/json",
}

def get_devices():
    url = f"{NETBOX_URL}/api/dcim/devices/?status=active&limit=1000"
    response = requests.get(url, headers=headers, verify=False)
    data = response.json()
    return data.get("results", [])

def build_inventory():
    devices = get_devices()
    inventory = {
        "_meta": {"hostvars": {}},
        "all": {"hosts": [], "children": []},
    }

    for device in devices:
        name = device.get("name")
        if not name:
            continue

        ip = None
        if device.get("primary_ip4"):
            ip = device["primary_ip4"]["address"].split("/")[0]

        role = ""
        if device.get("role"):
            role = device["role"].get("slug", "")
        elif device.get("device_role"):
            role = device["device_role"].get("slug", "")

        site = ""
        if device.get("site"):
            site = device["site"].get("slug", "")

        platform = ""
        if device.get("platform"):
            platform = device["platform"].get("slug", "")

        inventory["all"]["hosts"].append(name)
        inventory["_meta"]["hostvars"][name] = {
            "ansible_host": ip or name,
            "device_role": role,
            "site": site,
            "platform": platform,
        }

    return inventory

if __name__ == "__main__":
    print(json.dumps(build_inventory(), indent=2))
