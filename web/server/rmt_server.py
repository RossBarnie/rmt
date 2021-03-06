import web
import requests
import dblayer
import os
import urlparse
from datetime import datetime
from config import config
from rfc3987 import parse
import logging

root_dir = os.path.join(os.path.dirname(__file__))
render = web.template.render(root_dir + '/templates/', base='layout')

urls = (
    '/', 'index',
    '/host/(.*)', 'host',
    '/add', 'add',
    '/delete/(.*)', 'delete'
)
app = web.application(urls, globals())

HB_STATE_FINE = "success"
HB_STATE_WARNING = "warning"
HB_STATE_DANGER = "danger"
HB_STATE_DEAD = "dead"
RES_STATE_FINE = "success"
RES_STATE_WARNING = "warning"
RES_STATE_DANGER = "danger"
RES_STATE_DEFAULT = "default"


class index:

    def get_hb_state(self, hosts):
        new_hosts = []
        cfg = config()
        cfg.refresh_config()
        for host in hosts:
            host.hbstate = HB_STATE_FINE
            delay = datetime.now() - host['last_contacted']
            if delay.seconds >= cfg.hb_warning_time:
                host.hbstate = HB_STATE_WARNING
            if delay.seconds >= cfg.hb_danger_time:
                host.hbstate = HB_STATE_DANGER
            if delay.seconds >= cfg.hb_dead_time:
                host.hbstate = HB_STATE_DEAD
            new_hosts += [host]
        return new_hosts

    def GET(self):
        yellow_hosts = dblayer.get_hosts_by_tower("yellow")
        red_hosts = dblayer.get_hosts_by_tower("red")
        green_hosts = dblayer.get_hosts_by_tower("green")
        blue_hosts = dblayer.get_hosts_by_tower("blue")
        yellow_hosts = self.get_hb_state(yellow_hosts)
        red_hosts = self.get_hb_state(red_hosts)
        green_hosts = self.get_hb_state(green_hosts)
        blue_hosts = self.get_hb_state(blue_hosts)
        hosts = {"yellow": yellow_hosts, "red": red_hosts, "green": green_hosts, "blue": blue_hosts}
        cfg = config()
        cfg.refresh_config()
        return render.index(hosts, cfg.site_refresh_time)


class add:

    def try_host(self, hostname):
        success = False
        try:
            result = parse(hostname, rule="URI")
            if result['authority'] != '':
                return True
        except ValueError, e:
            logging.error("address given does not match URI definition")
            logging.exception(e)
        return success

    def GET(self):
        ren_dict = {}
        unassigned = dblayer.get_unassigned()
        ren_dict['unassigned'] = unassigned
        return render.add(ren_dict)

    def POST(self):
        form = web.input()
        logging.info("Trying to add {}".format(form.address))
        if self.try_host(form.address):
            parser = urlparse.urlparse(form.address)
            if parser.port:
                port = parser.port
            else:
                port = 80
            address = parser.hostname
            if not parser.scheme:
                address = "http://{}".format(address)
            dblayer.insert_new_address(address, port, form.tower)
            raise web.redirect('/')
        else:
            ren_dict = {}
            ren_dict['unassigned'] = dblayer.get_unassigned()
            ren_dict['status'] = False
            return render.add(ren_dict)


class host:

    reboot_msg = ""

    def POST(self, host_id):
        host_table = dblayer.get_host_address_from_id(host_id)
        host_info = self.get_host_address(host_id)
        address = "http://{}:{}".format(host_info[0], host_info[1])
        r = None
        try:
            r = requests.get(address + "/reboot", timeout=2)
            logging.info("reboot request sent")
        except requests.RequestException, e:
            logging.warning("reboot request to {} failed".format(address))
            logging.exception(e)
        if r is not None:
            host.reboot_msg = r.text
        web.redirect("/host/{}".format(host_id))

    def get_state(self, value, warn_val, danger_val):
        state = RES_STATE_DEFAULT
        if value >= 0:
            state = RES_STATE_FINE
            if value >= warn_val:
                state = RES_STATE_WARNING
            if value >= danger_val:
                state = RES_STATE_DANGER
        return state

    def get_host_address(self, host_id):
        host_table = dblayer.get_host_address_from_id(host_id)

        host_addr = ""
        host_port = -1
        count = 0
        for a in host_table:
            count += 1
            host_addr = a['address']
            host_port = a['port']
        if count > 1:
            logging.error("more than one host with id {}".format(host_id))

        return [host_addr, host_port]

    def GET(self, host_id):
        timeout = 2
        render_dict = {}
        render_dict['host_id'] = host_id
        host_info = self.get_host_address(host_id)
        render_dict['host_addr'] = host_addr = host_info[0]
        render_dict['host_port'] = host_port = host_info[1]
        r = None
        url = ""
        try:
            url = "http://{}:{}".format(host_addr, host_port)
            r = requests.get(url + "/containers", timeout=timeout)
        except requests.RequestException as e:
            logging.error("Container request to {} failed:".format(host_addr))
            logging.exception(e)
            r = None
        containers = None

        if r:
            containers = r.json()
        else:
            logging.warning("No response object received from {}".format(host_addr))
        if containers:
            for container in containers:
                del container['SizeRw']
                del container['SizeRootFs']
                container['Id'] = container['Id'][:5]
        else:
            logging.warning("No containers received from {}".format(host_addr))
        render_dict['containers'] = containers
        cpu_response = None
        ram_response = None
        temp_response = None
        cpu = None
        ram = None
        temp = None
        try:
            cpu_response = requests.get('{}/cpu'.format(url), timeout=timeout)
            cpu = cpu_response.json()
            ram_response = requests.get('{}/ram'.format(url), timeout=timeout)
            ram = ram_response.json()
            temp_response = requests.get('{}/temperature'.format(url), timeout=timeout)
            temp = temp_response.json()
        except requests.RequestException as e:
            logging.error("CPU/RAM/temperature request error:")
            logging.error("CPU: {}".format(cpu_response))
            logging.error("RAM: {}".format(ram_response))
            logging.error("Temperature: {}".format(temp_response))
            cpu = None
            ram = None
            temp = None
        except ValueError as v:
            logging.error("Problem decoding CPU/RAM/Temperature")
            logging.exception(v)
            temp = None
        cpu_usage = -1
        ram_usage = None
        if cpu:
            cpu_usage = cpu[0] + cpu[1]
        else:
            logging.warning("No CPU information received from {}".format(host_addr))
        if ram:
            ram_dict = {}
            ram_dict['total'] = ram['ram_total'] / 1024.0 / 1024.0
            ram_dict['used'] = ram['ram_used'] / 1024.0 / 1024.0
            ram_usage = round(ram_dict['used'] / ram_dict['total'] * 100, 1)
        else:
            logging.warning("No RAM information received from {}".format(host_addr))
        if temp:
            temp = round(temp/1000.0, 2)
        else:
            logging.warning("No Temperature information received from {}".format(host_addr))
        render_dict['temp'] = temp
        render_dict['ram_usage'] = ram_usage
        render_dict['cpu_usage'] = cpu_usage
        cfg = config()
        cpu_state = self.get_state(cpu_usage, cfg.cpu_warning, cfg.cpu_danger)
        ram_state = self.get_state(ram_usage, cfg.ram_warning, cfg.ram_danger)
        temp_state = self.get_state(temp, cfg.temp_warning, cfg.temp_danger)
        render_dict['cpu_state'] = cpu_state
        render_dict['ram_state'] = ram_state
        render_dict['temp_state'] = temp_state
        render_dict['reboot_msg'] = host.reboot_msg
        host.reboot_msg = ""
        return render.host(render_dict)


class delete:

    def GET(self, host_id):
        if dblayer.delete_host(host_id):
            logging.info("deleted host " + host_id)
        else:
            logging.error("host " + host_id + "not deleted, host not found")
        web.redirect('/')


if __name__ == "__main__":
    log_dir = os.path.dirname(os.path.realpath(__file__))
    print "Logging information in " + log_dir + '/server.log'
    logging.basicConfig(filename='{}/server.log'.format(log_dir), level=logging.INFO)
    logging.info("Started server")
    app.run()
    logging.info("Stopped server")
