__author__ = 'ross'

import dblayer
import requests
import datetime
import logging


def get_resource(address, port, resource):
    ret = None
    r = None
    try:
        if address is not None and port is not None and resource is not None:
            r = requests.get("http://{}:{}/{}".format(address, port, resource), timeout=2)
        else:
            logging.warning("attempted to access address with missing information")
    except requests.RequestException, e:
        logging.error("request for {} failed".format(resource))
        logging.exception(e)
    if r is not None:
        if r.status_code == 200:
            ret = r.json()
        else:
            logging.warning(" request to http://{}:{}/{} status code:{}".format(address, port, resource, r.status_code))
    else:
        logging.info("] no response object, request failed")
    return ret


def attempt_contact(address, port):
    ret = False
    r = None
    try:
        r = requests.head("http://{}:{}".format(address, port), timeout=1)
    except requests.RequestException, e:
        logging.info("] request to http://{}:{} failed, ignoring".format(address, port))
    if r is not None:
        if r.status_code == 404:  # a running client will return 404, otherwise should timeout
            ret = True
    return ret


def main():
    hosts = dblayer.get_hosts()
    for host in hosts:
        address = host.address
        if attempt_contact(address, host.port):
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