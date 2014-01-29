import web
import requests

render = web.template.render('templates/', base='layout')

urls = (
    '/', 'index',
    '/host/(.*)', 'host',
    '/add', 'add'
)
app = web.application(urls, globals())

db = web.database(dbn='mysql', user='rmt-user', db='rmt')


class index:

    def GET(self):
        hosts = db.select('hosts')
        return render.index(hosts)


class add:

    def try_host(self, hostname):
        return True

    def POST(self):
        form = web.input()
        if self.try_host(form.address):
            db.insert('hosts', address=form.address)
        raise web.redirect('/')


class host:

    def GET(self, host_id):

        host_addr = db.select('hosts.address', where='hosts.id = ' + host_id)

        r = None
        try:
            print host_id
            r = requests.get(host_addr + '/containers')
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
            cpu_response = requests.get(host_addr + '/cpu')
            cpu = cpu_response.json()
            ram_response = requests.get(host_addr + '/ram')
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