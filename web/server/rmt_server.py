import web
import requests
import dblayer

render = web.template.render('templates/', base='layout')

urls = (
    '/', 'index',
    '/host/(.*)', 'host',
    '/add', 'add'
)
app = web.application(urls, globals())


class index:

    def GET(self):
        hosts = dblayer.get_hosts()
        return render.index(hosts)


class add:

    def try_host(self, hostname):
        # placeholder for some kind of ping to make sure the host exists/can connect
        return True

    def POST(self):
        form = web.input()
        if self.try_host(form.address):
            dblayer.insert_new_address(form.address)
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
            print "[ERROR] Container request to", host_addr, "failed:", e
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
        try:
            cpu_response = requests.get('%s/cpu' % host_addr)
            cpu = cpu_response.json()
            ram_response = requests.get('%s/ram' % host_addr)
            ram = ram_response.json()
        except requests.RequestException as e:
            print "[ERROR] CPU or RAM request error:", e
            cpu = None
            ram = None
        cpu_usage = []
        ram_usage = {}
        if cpu:
            cpu_usage = cpu[0] + cpu[1]
        if ram:
            ram_usage = {}
            ram_usage['total'] = ram['ram_total'] / 1024 / 1024
            ram_usage['used'] = ram['ram_used'] / 1024 / 1024

        return render.host(containers, cpu_usage, ram_usage)


if __name__ == "__main__":
    app.run()