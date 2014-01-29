import web
import requests

render = web.template.render('templates/', base='layout')

urls = (
    '/', 'index',
    '/host', 'host',
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

    def GET(self):
       # r = None
       # try:
       #     print host_address
        #    r = requests.get(host_address + '/containers')
       # except requests.RequestException as e:
       #     print e
       #     r = None
        containers = None
        #if r:
        #    containers = r.json()
        #if containers:
        #    for container in containers:
        #        del container['SizeRw']
        #        del container['SizeRootFs']
        #        container['Id'] = container['Id'][:5]
        #        names = ""
        #        for i in container['Names']:
        #            names = names + i
        #        container['Names'] = names
        try:
            cpu_response = requests.get('http://0.0.0.0:1235/cpu')
            cpu = cpu_response.json()
            ram_response = requests.get('http://0.0.0.0:1235/ram')
            ram = ram_response.json()
        except requests.RequestException as e:
            print "exception raised:", e
            cpu = None
            ram = None
        cpu_usage = None
        ram_usage = None
        if cpu:
            cpu_usage = cpu[0] + cpu[1]
        if ram:
            ram_usage = {}
            ram_usage['total'] = ram['ram_total'] / 1024 / 1024
            ram_usage['used'] = ram['ram_used'] / 1024 / 1024

        return render.host(containers, cpu_usage, ram_usage)


if __name__ == "__main__":
    app.run()