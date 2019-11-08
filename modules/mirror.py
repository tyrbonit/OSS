#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gluon import *
import cPickle
import redis, json, socket, re
from time import time
from cachetools import Cache


class RedisClient(object):
    """Вспомогательный класс клиента для ускорения пересчета ключей"""
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.rd = redis.Redis(*args, **kwargs)
        self.rd4pp = None
        self.default_sock_stack = 0
        self.sock_stack = self.default_sock_stack

    def __getattr__(self, attr):
        return self.rd.__getattribute__(attr)

    def connect(self, host='localhost', port=6379, db=0, password=None,
                *args, **kwargs):
        try:
            self.rd4pp.close()
        except:
            pass
        self.rd4pp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.rd4pp.connect((host, port))
        if password:
            self.rd4pp.send(
                '*2\r\n$4\r\nAUTH\r\n$%s\r\n%s\r\n'
                % (len(password), password))
        if db:
            self.rd4pp.send(
                '*2\r\n$6\r\nSELECT\r\n$%s\r\n%s\r\n' % (len(db), db))
        self.sock_stack = self.default_sock_stack

    def pipeline(self, transaction=False):
        pp = self.rd.pipeline(transaction=transaction)
        if transaction:
            return pp
        #exe = pp.execute
        def execute(transaction=False):
            if transaction:
                return pp.execute()
            if self.sock_stack < 0:
                self.connect(*self.args, **self.kwargs)
            self.rd4pp.send(''.join(
                '*%s\r\n' % len(cmd)
                + ''.join(['$%s\r\n%s\r\n' % (len(str(w)), w) for w in cmd])
                for cmd, _ in pp.command_stack))
            pp.command_stack = []
            self.sock_stack -= 1
            return []
        pp.execute = execute
        return pp


class MIRROR(object):
    #cache = Cache(20000)
    def __init__(self):
        print('init mirror')
        self.rdb = RedisClient() #redis.StrictRedis(db=0)
        self.rdb.connect()
        self.bpipe = self.rdb.pipeline(transaction=False)
        side = self.rdb
        """for id in side.keys("1*"):
            #data = {k:v for k,v in side.hgetall(id).items() }
            [side.hdel(id, k) for k in side.hkeys(id) if not k in ['value', 'valueclc', 'lastCalcTime']]
            #self.cache[id] = [float(side.hget(id, "valueclc")), float(side.hget(id, "lastCalcTime"))]"""

    def registerObject(self, id, data, *args, **kvargs):
        print('register: ', id)
        self.rdb.hmset(id, {k:v for k,v in data.items() if k in ['value', 'valueclc', 'lastCalcTime']})

    def getObject(self, id, *args, **kvargs):
        side = self.rdb
        if side.exists(id):
            return dict(id=id, **side.hgetall(id))
        else:
            print('object %s not exists' % id)
            return None

    def getObjects(self, pattern = "*"):
        side = self.rdb
        return [side.hgetall(id) for id in side.scan_iter(pattern)]

    def setObjectAttr(self, id, field, value, *args, **kvargs):
        if field=='value':
            self.rdb.hmset(id, dict(value=value, **self.calc(self.rdb.hgetall(id))))
        else:
            self.rdb.hset(id, field, value)

    def setObjectAttrs(self, id, data, *args, **kvargs):
        side = self.rdb
        side.hmset(id, {k:v for k,v in data.items() if k in ['value', 'valueclc', 'lastCalcTime']})

    def getObjectAttr(self, id, field, *args, **kvargs):
        side = self.rdb
        attr = side.hget(id, field)
        if field in ['value', 'valueclc', 'lastCalcTime']:
            attr = float(attr)
        return attr

    @staticmethod
    def calc(data):
        _now = time()
        valueclc = float(data["valueclc"])
        valueclc += float(data["value"])*(_now-float(data["lastCalcTime"]))/3600.0
        return dict(lastCalcTime=_now, valueclc=valueclc)

    def makeslice(self, getslice=False):
        dataslice = []
        for id in self.rdb.keys("1*"):
            data = self.calc(self.rdb.hgetall(id))
            self.bpipe.hmset(id, data)
            if getslice:
                dataslice.append(dict(id=id, **data))
        self.bpipe.execute()
        return slice

    def getdata(self, query):
        objects = []
        r = str(re.compile(r"@id\s*in\s*\((['\w,\s]+)\)|@id\s*==\s*('\w+')").findall(query))
        idList = re.compile(r"\d+").findall(r)
        for s_id in idList:
            objects.append(dict(id=s_id, value=float(self.rdb.hget(s_id, 'value'))))
        return objects

    def __del__(self):
        print 'mirror terminate'
