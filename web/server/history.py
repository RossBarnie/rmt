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
    if r is not None:
        ret = r.json()
    return ret


def main():
    hosts = dblayer.get_hosts()
    for host in hosts:
        address = host.address
        cpu_list = get_resource(address, host.port, "cpu")
        cpu = cpu_list[0] + cpu_list[1]
        ram_dict = get_resource(address, host.port, "ram")
        ram = round(ram_dict['ram_used'] / ram_dict['ram_total'] * 100, 1)
        temp = get_resource(address, host.port, "temperature")
        temp = round(temp/1000.0, 2)
        effective = datetime.datetime.utcnow()
        expire = effective + datetime.timedelta(weeks=1)
        effective = effective.isoformat(" ")
        expire = expire.isoformat(" ")
        dblayer.add_history(host.id, cpu, ram, temp, effective, expire)


if __name__ == "__main__":
    main()