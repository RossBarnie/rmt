import web
import docker

render = web.template.render('templates/', base='layout')

urls = (
    '/', 'index',
)
app = web.application(urls, globals())


class index:

    def GET(self):
        client = docker.Client()
        containers = client.containers()
        print containers
        for container in containers:
            del container['SizeRw']
            del container['SizeRootFs']
            container['Id'] = container['Id'][:5]
            names = ""
            for i in container['Names']:
                names = names + i
            container['Names'] = names
        print containers
        return render.index(containers)


if __name__ == "__main__":
    app.run()