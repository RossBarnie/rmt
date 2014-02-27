import web
import psutil
import json
import docker
import command
import subprocess

urls = (
    '/cpu', 'cpu',
    '/ram', 'ram',
    '/containers', 'containers',
    '/temperature', 'temp',
    '/reboot', 'reboot'
)
app = web.application(urls, globals())


def prepare_message(message):
    web.header('Content-Type', 'application/json')
    return json.dumps(message)


class containers:

    def GET(self):
        containers = None
        try:
            client = docker.Client()
            containers = client.containers(all=True)
        except Exception as e:
            print "[ERROR] Containers unavailable: ", e
            containers = None           
        return prepare_message(containers)


class cpu:

    def GET(self):
        utilisation = psutil.cpu_times_percent(interval=1)
        return prepare_message(utilisation)


class ram:

    def GET(self):
        ram_total = psutil.virtual_memory().total
        ram_used = psutil.virtual_memory().used
        ram_dict = {'ram_total': ram_total, 'ram_used': ram_used}
        return prepare_message(ram_dict)
    
        
class temp:
    
    def GET(self):
        com = command.Command(["cat", "/sys/class/thermal/thermal_zone0/temp"])
        temp = None
        try:
            temp = com.execute(return_output=True).get("comm_retval")
            temp = int(temp)
        except Exception, e:
            print "[ERROR] temperature command error: ", e
            return None
        return prepare_message(temp)
        

class reboot:

    def GET(self):
        subprocess.call(['reboot'])
        web.redirect('/')
        #TODO: this redirect shouldn't be here, this is server-side logic

if __name__ == "__main__":
    app.run()
