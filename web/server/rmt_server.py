import web
from web import form
import requests
import dblayer
import os

template_root = os.path.join(os.path.dirname(__file__))
render = web.template.render(template_root + '/templates/', base='layout')

urls = (
    '/', 'index',
    '/host/(.*)', 'host',
    '/add', 'add'
)
app = web.application(urls, globals())


class index:

    def GET(self):
        yellow_hosts = dblayer.get_hosts_by_stack("yellow")
        red_hosts = dblayer.get_hosts_by_stack("red")
        green_hosts = dblayer.get_hosts_by_stack("green")
        grey_hosts = dblayer.get_hosts_by_stack("grey")
        hosts = {"yellow": yellow_hosts, "red": red_hosts, "green": green_hosts, "grey": grey_hosts}
        stack = form.Form(
            form.Textbox('address',
                         form.notnull,
                         id="address",
                         class_="form-control"
                         ),
            form.Dropdown('stack',
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
        return render.index(hosts, f)


class add:

    def try_host(self, hostname):
        # placeholder for some kind of ping to make sure the host 
        # exists/can connect
        return True

    def POST(self):
        form = web.input()
        if self.try_host(form.address):
            dblayer.insert_new_address(form.address, form.stack)
        raise web.redirect('/')


class host:

    def GET(self, host_id):

        host_table = dblayer.get_host_address_from_id(host_id)

        host_addr = ""
        count = 0
        for a in host_table:
            count += 1
            host_addr = a['address']

        if count > 1:
            print "[ERROR] more than one host with id %d" % host_id
        r = None
        try:
            r = requests.get('%s/containers' % host_addr)
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
            cpu_response = requests.get('%s/cpu' % host_addr)
            cpu = cpu_response.json()
            ram_response = requests.get('%s/ram' % host_addr)
            ram = ram_response.json()
            temp_response = requests.get('%s/temperature' % host_addr)
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
