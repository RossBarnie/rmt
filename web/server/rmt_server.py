import web
import requests
import dblayer
import os
import urlparse
from datetime import datetime
from ConfigParser import SafeConfigParser
import ConfigParser
from rfc3987 import parse
import json
import gviz_api

template_root = os.path.join(os.path.dirname(__file__))
render = web.template.render(template_root + '/templates/', base='layout')

urls = (
    '/', 'index',
    '/host/(\d+)', 'host',
    '/add', 'add',
    '/delete/(\d+)', 'delete',
    '/history/(\d+)', 'history'
)
app = web.application(urls, globals())

web.config.debug = True

HB_STATE_FINE = "success"
HB_STATE_WARNING = "warning"
HB_STATE_DANGER = "danger"
HB_STATE_DEAD = "dead"
RES_STATE_FINE = "success"
RES_STATE_WARNING = "warning"
RES_STATE_DANGER = "danger"
RES_STATE_DEFAULT = "default"


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
        success = False
        try:
            result = parse(hostname, rule="URI")
            if result['authority'] != '':
                return True
        except ValueError, e:
            print "[ERROR] address given does not match URI definition"
            print e
        return success

    def GET(self):
        ren_dict = {}
        unassigned = dblayer.get_unassigned()
        ren_dict['unassigned'] = unassigned
        return render.add(ren_dict)

    def POST(self):
        form = web.input()
        print "[INFO] Trying to add {}".format(form.address)
        if self.try_host(form.address):
            parser = urlparse.urlparse(form.address)
            if parser.port:
                port = parser.port
            else:
                port = 80
            address = parser.hostname
            if not parser.scheme:
                address = "http://%s" % address
            dblayer.insert_new_address(address, port, form.stack)
            raise web.redirect('/')
        else:
            ren_dict = {}
            ren_dict['unassigned'] = dblayer.get_unassigned()
            ren_dict['status'] = False
            return render.add(ren_dict)


class host:

    def POST(self, host_id):
        host_table = dblayer.get_host_address_from_id(host_id)
        host_info = self.get_host_address(host_id)
        address = "http://{}:{}".format(host_info[0], host_info[1])
        requests.get(address + "/reboot", timeout=5)
        web.redirect("/")

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
            print "[ERROR] more than one host with id %d" % host_id

        return [host_addr, host_port]

    def GET(self, host_id):
        timeout = 5
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
            print "[ERROR] Container request to", \
            host_addr, "failed:"
            print e
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
        render_dict['containers'] = containers
        cpu_response = None
        ram_response = None
        temp_response = None
        cpu = None
        ram = None
        temp = None
        try:
            cpu_response = requests.get('%s/cpu' % url, timeout=timeout)
            cpu = cpu_response.json()
            ram_response = requests.get('%s/ram' % url, timeout=timeout)
            ram = ram_response.json()
            temp_response = requests.get('%s/temperature' % url, timeout=timeout)
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
            print "[ERROR] Problem decoding CPU/RAM/Temperature"
            print v
            temp = None
        cpu_usage = -1
        ram_usage = None
        if cpu:
            cpu_usage = cpu[0] + cpu[1]
        if ram:
            ram_dict = {}
            ram_dict['total'] = ram['ram_total'] / 1024.0 / 1024.0
            ram_dict['used'] = ram['ram_used'] / 1024.0 / 1024.0
            ram_usage = round(ram_dict['used'] / ram_dict['total'] * 100, 1)
        if temp:
            temp = round(temp/1000.0, 2)
        render_dict['temp'] = temp
        render_dict['ram_usage'] = ram_usage
        render_dict['cpu_usage'] = cpu_usage
        cfg = config()
        cfg.refresh_config()
        cpu_state = self.get_state(cpu_usage, cfg.cpu_warning, cfg.cpu_danger)
        ram_state = self.get_state(ram_usage, cfg.ram_warning, cfg.ram_danger)
        temp_state = self.get_state(temp, cfg.temp_warning, cfg.temp_danger)
        render_dict['cpu_state'] = cpu_state
        render_dict['ram_state'] = ram_state
        render_dict['temp_state'] = temp_state

        return render.host(render_dict)


class delete:

    def GET(self, host_id):
        if dblayer.delete_host(host_id):
            print "[INFO] deleted host " + host_id
        else:
            print "[ERROR] host " + host_id + "not deleted, host not found"
        web.redirect('/')


class history:



    def prepare_datetime(self, date):
        dthandler = lambda obj: (
            obj.isoformat()
            if isinstance(obj, datetime)
            else None)
        return json.dumps(date, default=dthandler)

    def GET(self, host_id):
        # chart_template = """
        #
        #         <script type="text/javascript" src="https://www.google.com/jsapi"></script>
        #         <script type="text/javascript">
        #             google.load("visualization", "1", {packages:["corechart"]});
        #             function drawChart() {
        #                 var data = google.visualization.DataTable(%(data)s);
        #                 var options = {
        #                     title: '%(title)s'
        #                 };
        #
        #                 var chart = new google.visualization.LineChart(document.getElementById('%(resource)s_chart'));
        #                 chart.draw(data, options);
        #             }
        #             google.setOnLoadCallback(drawChart);
        #         </script>
        #         <div id="%(resource)s_chart"></div>
        # """
        render_dict = {}
        render_dict['address'] = "placeholder"
        historical = dblayer.get_history_from_host_id(host_id)
        cpu_desc = {"timestamp": ("datetime", "Timestamp"),
                    "load": ("number", "Load")}
        cpu = []
        # ram = []
        # temp = []
        for entry in historical:
            cpu += [{"timestamp": entry['effective'], "load": entry['cpu']}]
            # ram += entry['effective'], entry['ram']
            # temp += [[entry['effective'], entry['temperature']]]
        cpu_table = gviz_api.DataTable(cpu_desc)
        cpu_table.LoadData(cpu)

        cpu_json = cpu_table.ToJSon(columns_order=("timestamp", "load"),
                                    order_by="timestamp")
        # render_dict['cpu_js'] = chart_template
        render_dict['cpu_json'] = cpu_json
        # cpu = [['DateTime', 'Load']]
        # ram = [['DateTime', 'Used']]
        # temp = [['DateTime', 'degrees C']]

        # render_dict['cpu'] = json.dumps(cpu)
        # print render_dict['cpu']
        # render_dict['ram'] = ram
        # render_dict['temp'] = temp
        return render.history(render_dict)


if __name__ == "__main__":
    app.run()
