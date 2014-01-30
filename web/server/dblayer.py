__author__ = 'ross'

import web


db = web.database(dbn='mysql', user='rmt-user', db='rmt')


def get_hosts():
    return db.select('hosts')


def get_host_id_from_address(address):
    return db.select('hosts', where="hosts.address = " + address)


def get_host_address_from_id(host_id):
    return db.select('hosts', where="hosts.id = " + host_id)


def insert_new_address(address):
    db.insert('hosts', address=address)


