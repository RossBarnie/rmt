import web
from web import form
import requests
import dblayer
import os
import urlparse
from datetime import datetime
from ConfigParser import SafeConfigParser

template_root = os.path.join(os.path.dirname(__file__))
render = web.template.render(template_root + '/templates/', base='layout')

urls = (
    '/', 'index',
    '/host/(.*)', 'host',
    '/add', 'add'
)
app = web.application(urls, globals())

HB_STATE_FINE = "active"
HB_STATE_WARNING = "warning"
HB_STATE_DANGER = "danger"
HB_DANGER_TIME = 60
HB_WARNING_TIME = 30
SITE_REFRESH_TIME = 10


def get_config():
    global HB_WARNING_TIME
    global HB_DANGER_TIME
    parser = SafeConfigParser()
    parser.read("server.cfg")
    HB_WARNING_TIME = parser.get("heartbeat_visualisation", "warning_time")
    HB_DANGER_TIME = parser.get("heartbeat_visualisation", "danger_time")


class index:

    def get_hb_state(self, hosts):
        new_hosts = []
        for host in hosts:
            host.hbstate = HB_STATE_FINE
            delay = datetime.now() - host['last_contacted']
            if delay.seconds >= HB_WARNING_TIME:
                host.hbstate = HB_STATE_WARNING
            if delay.seconds >= HB_DANGER_TIME:
                host.hbstate = HB_STATE_DANGER
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
        stack = form.Form(
            form.Textbox(
                'address',
                # form.notnull doesn't appear to work
                # TODO: fix form insertion working when it shouldn't
                form.notnull,
                id="address",
                class_="form-control",
            ),
            form.Dropdown(
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
        f = stack()
        return render.index(hosts, f, SITE_REFRESH_TIME)


class add:

    def try_host(self, hostname):
        # placeholder for some kind of ping to make sure the host 
        # exists/can connect
        # TODO: actually write this.
        return True

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
    get_config()
    app.run()
