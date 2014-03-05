__author__ = 'ross'

import dblayer
import requests
import datetime


def get_resource(address, port, resource):
    ret = None
    r = None
    try:
        r = requests.get("http://{}:{}/{}".format(address, port, resource), timeout=2)
    except requests.RequestException, e:
        print "[ERROR] request for {} failed".format(resource)
        print e
    if r is not None and r.status_code == 200:
        ret = r.json()
    else:
        print "[WARNING] request to http://{}:{}/{} failed".format(address, port, resource)
    return ret


def main():
    hosts = dblayer.get_hosts()
    for host in hosts:
        address = host.address
        cpu_list = get_resource(address, host.port, "cpu")
        cpu = None
        ram = None
        temp = None
        if cpu_list:
            cpu = cpu_list[0] + cpu_list[1]
        ram_dict = get_resource(address, host.port, "ram")
        if ram_dict:
            used = ram_dict['ram_used'] / 1024.0 / 1024
            total = ram_dict['ram_total'] / 1024.0 / 1024
            ram = round(used / total * 100, 1)
        temp_response = get_resource(address, host.port, "temperature")
        if temp_response:
            temp = round(temp_response/1000.0, 2)
        effective = datetime.datetime.utcnow()
        expire = effective + datetime.timedelta(weeks=1)
        effective = effective.isoformat(" ")
        expire = expire.isoformat(" ")
        if cpu is not None and ram is not None and temp is not None:
            dblayer.add_history(host.id, cpu, ram, temp, effective, expire)


if __name__ == "__main__":
    main()