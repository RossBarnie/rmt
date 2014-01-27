import web
import psutil
import json

urls = (
    '/cpu', 'cpu',
    '/ram', 'ram'
)
app = web.application(urls, globals())


class cpu:

    def GET(self):
        utilisation = psutil.cpu_times_percent(interval=1)
        dump = json.dumps(utilisation)
        return dump


class ram:

    def GET(self):
        ram_total = psutil.virtual_memory().total
        ram_used = psutil.virtual_memory().used
        dict = {'ram_total': ram_total, 'ram_used': ram_used}
        return json.dumps(dict)

if __name__ == "__main__":
    app.run()