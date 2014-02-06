__author__ = 'ross'

import web


db = web.db.database(dbn='mysql', user='rmt-user', db='rmt')


def get_hosts():
    return db.select('hosts')


def get_hosts_by_stack(stack):
    return db.select('hosts', where="hosts.stack = '%s'" % stack)


def get_host_id_from_address(address):
    return db.select('hosts', where="hosts.address = " + address)


def get_host_address_from_id(host_id):
    return db.select('hosts', where="hosts.id = " + host_id)


def insert_new_address(address, stack):
    db.insert('hosts', address=address, stack=stack)


def update_silent(address, time):
    entry = db.select('silent', where="silent.hostname = '%s'" % address)
    if entry:
        db.update("silent", where="silent.hostname = $address", last_contact=time, vars=locals())
    else:
        insert_new_silent(address, time)


def insert_new_silent(name, time):
    db.insert('silent', hostname=name, last_contact=time)
