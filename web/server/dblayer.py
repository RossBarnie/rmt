__author__ = 'ross'

import web


db = web.db.database(dbn='mysql', user='rmt-user', db='rmt')


def get_hosts():
    return db.select('hosts')


def get_hosts_by_tower(tower):
    return db.select('hosts', where="hosts.tower = '{}'".format(tower), order="hosts.address")


def get_assigned():
    return db.select('hosts', where="hosts.tower is not null")


def get_unassigned():
    return db.select('hosts', where="hosts.tower is null")


def get_host_id_from_address(address):
    return db.select('hosts', where="hosts.address = " + address)


def get_host_address_from_id(host_id):
    return db.select('hosts', where="hosts.id = " + host_id)


def insert_new_address(address, port, tower):
    exists = db.select('hosts', where="address = '{}'".format(address))
    if exists:
        db.update('hosts', where="hosts.address = '{}'".format(address), port=port, tower=tower)
    else:
        db.insert('hosts', address=address, port=port, tower=tower)


def update_heartbeat(address, time):
    entry = db.select('hosts', where="hosts.address = '{}'".format(address))
    if entry:
        db.update("hosts", where="hosts.address = '{}'".format(address), last_contacted=time, vars=locals())
    else:
        insert_new_heartbeat(address, time)


def insert_new_heartbeat(name, time):
    db.insert('hosts', address=name, last_contacted=time)


def delete_host(host_id):
    success = True
    exists = db.select('hosts', where="hosts.id = " + host_id)
    if exists:
        db.delete('hosts', where="hosts.id = " + host_id)
    else:
        success = False
    return success


def add_history(host_id, cpu, ram, temp, effective, expire):
    db.insert('history', host_id=host_id, cpu=cpu, ram=ram, temperature=temp, effective=effective, expiry=expire)


def get_history_from_address(host_id):
    db.select('history', where="history.host_id = '{}'".format(host_id))