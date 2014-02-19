import web
import requests
import dblayer
import os
import urlparse
from datetime import datetime
from ConfigParser import SafeConfigParser
import ConfigParser
from rfc3987 import parse

template_root = os.path.join(os.path.dirname(__file__))
render = web.template.render(template_root + '/templates/', base='layout')

urls = (
    '/', 'index',
    '/host/(.*)', 'host',
    '/add', 'add'
)
app = web.application(urls, globals())

HB_STATE_FINE = "success"
HB_STATE_WARNING = "warning"
HB_STATE_DANGER = "danger"
HB_STATE_DEAD = "dead"
CPU_STATE_FINE = "success"
CPU_STATE_WARNING = "warning"
CPU_STATE_DANGER = "danger"
RAM_STATE_FINE = "success"
RAM_STATE_WARNING = "warning"
RAM_STATE_DANGER = "danger"
TEMP_STATE_FINE = "success"
TEMP_STATE_WARNING = "warning"
TEMP_STATE_DANGER = "danger"


class config:

    site_refresh_time = 10  # 10 seconds default
    hb_danger_time = 60  # 60 seconds default
    hb_warning_time = 30  # 30 seconds default
    hb_dead_time = 86400  # 1 day default (86400 seconds)
    cpu_fine = 0  # 0% default
    cpu_warning = 50  # 50% default
    cpu_danger = 75  # 75% default
    ram_fine = 0  # 0% default
    ram_warning = 50  # 50% default
    ram_danger = 75  # 75% default
    temp_fine = 0  # 0 degrees C default
    temp_warning = 30  # 30 degrees C default
    temp_danger = 40  # 40 degrees C default

    def refresh_config(self):
        parser = SafeConfigParser()
        try:
            parser.read("server.cfg")
            self.hb_warning_time = parser.getint("heartbeat_visualisation", "warning_time")
            self.hb_danger_time = parser.getint("heartbeat_visualisation", "danger_time")
            self.site_refresh_time = parser.getint("website", "refresh_time")
            self.hb_dead_time = parser.getint("heartbeat_visualisation", "dead_time")
            self.cpu_fine = parser.getint("resource_visual", "cpu_fine")
            self.cpu_warning = parser.getint("resource_visual", "cpu_warning")
            self.cpu_danger = parser.getint("resource_visual", "cpu_danger")
            self.ram_fine = parser.getint("resource_visual", "ram_fine")
            self.ram_warning = parser.getint("resource_visual", "ram_warning")
            self.ram_danger = parser.getint("resource_visual", "ram_danger")
            self.temp_fine = parser.getint("resource_visual", "temp_fine")
            self.temp_warning = parser.getint("resource_visual", "temp_warning")
            self.temp_danger = parser.getint("resource_visual", "temp_danger")
        except ConfigParser.ParsingError, e:
            print "[ERROR] parsing config failed"
            print e
            return
        except ConfigParser.NoSectionError, e:
            print "[ERROR] parsing config, section not found"
            print e
            return



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
        yellow_hosts = dblayer.get_hosts_by_stack("yellow")
        red_hosts = dblayer.get_hosts_by_stack("red")
        green_hosts = dblayer.get_hosts_by_stack("green")
        grey_hosts = dblayer.get_hosts_by_stack("grey")
        yellow_hosts = self.get_hb_state(yellow_hosts)
        red_hosts = self.get_hb_state(red_hosts)
        green_hosts = self.get_hb_state(green_hosts)
        grey_hosts = self.get_hb_state(grey_hosts)
        hosts = {"yellow": yellow_hosts, "red": red_hosts, "green": green_hosts, "grey": grey_hosts}
        cfg = config()
        cfg.refresh_config()
        return render.index(hosts, cfg.site_refresh_time)


class add:

    def try_host(self, hostname):
        try:
            result = parse(hostname, rule="URI")
            return True
        except ValueError, e:
            print "[ERROR] address given does not match URI definition"
            print e
            return False

    def GET(self):
        stack = web.form.Form(
            web.form.Textbox(
                'address',
                # form.notnull doesn't appear to work
                # TODO: fix form insertion working when it shouldn't
                web.form.notnull,
                id="address",
                class_="form-control",
            ),
            web.form.Dropdown(
                'stack',
                [
                    ('red', 'Red'),
                    ('yellow', 'Yellow'),
                    ('green', 'Green'),
                    ('grey', 'Grey')
                ],
                id="stack",
                class_="form-control btn btn-default dropdown-toggle"
            )
        )
        form = stack()
        return render.add(form)

    def POST(self):
        form = web.input()
        if self.try_host(form.address):
            parser = urlparse.urlparse(form.address)
            port = parser.port
            address = parser.hostname
            dblayer.insert_new_address(address, port, form.stack)
        raise web.redirect('/')


class host:

    def GET(self, host_id):

        host_table = dblayer.get_host_address_from_id(host_id)

        host_addr = ""
        host_port = -1
        count = 0
        for a in host_table:
            count += 1
            host_addr = a['address']
            host_port = a['port']

        if count > 1:
            print "[ERROR] more than one host with id %d" % host_id
        r = None
        url = ""
        try:
            url = "http://{}:{}".format(host_addr, host_port)
            r = requests.get(url + "/containers")
        except requests.RequestException as e:
            print "[ERROR] Container request to", \
            host_addr, "failed:", e
            r = None
        containers = None
        if r:
            containers = r.json()
        if containers:
            for container in containers:
                del container['SizeRw']
                del container['SizeRootFs']
                container['Id'] = container['Id'][:5]
                names = ""
                for i in container['Names']:
                    names = names + i
                container['Names'] = names
        cpu_response = None
        ram_response = None
        temp_response = None
        cpu = None
        ram = None
        temp = None
        try:
            cpu_response = requests.get('%s/cpu' % url)
            cpu = cpu_response.json()
            ram_response = requests.get('%s/ram' % url)
            ram = ram_response.json()
            temp_response = requests.get('%s/temperature' % url)
            temp = temp_response.json()
        except requests.RequestException as e:
            print "[ERROR] CPU/RAM/temperature request error:", e
            print "CPU: ", cpu_response
            print "RAM: ", ram_response
            print "Temperature: ", temp_response
            cpu = None
            ram = None
            temp = None
        except ValueError as v:
            print "[ERROR] Problem decoding CPU/RAM/Temperature:", v
            temp = None
        cpu_usage = []
        ram_usage = {}
        if cpu:
            cpu_usage = cpu[0] + cpu[1]
        if ram:
            ram_usage = {}
            ram_usage['total'] = int(round(ram['ram_total'] / 1024.0 / 1024.0))
            ram_usage['used'] = int(round(ram['ram_used'] / 1024.0 / 1024.0))
        if temp:
            temp = round(temp/1000.0, 2)

        return render.host(host_addr, containers, cpu_usage, ram_usage, temp)


if __name__ == "__main__":
    app.run()
