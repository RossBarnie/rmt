__author__ = 'ross'

import web

urls = (
    '/', 'index',
    '/add', 'add'
)

render = web.template.render('templates/')

# not working because wrong table and don't want to expose passwords
db = web.database(dbn='mysql', user='rmt-user', db='rmt')


class index:

    def GET(self):
        todos = db.select('todo')
        return render.index(todos)


class add:

    def POST(self):
        i = web.input()
        n = db.insert('todo', title=i.title)
        raise web.seeother('/')

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()