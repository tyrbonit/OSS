# -*- coding: utf-8 -*-
from gluon.serializers import json

def index(): return dict(message="hello from fastBridge.py")


def updateData():
    if 'data' in request.vars:
        s_data = cPickle.loads(request.vars.get('data'))
        for item in s_data:
            try:
                databridge.setObjectAttr(item[0], 'value', item[1])
            except:
                pass
        return 'update OK'
    return 'not update'

def queryData():
    queryString = request.vars.get('queryString', '')
    dataType = request.vars.get('dataType', 'xml')
    data = databridge.getdata(queryString)
    if dataType=='json':
        return XML(json(data))
    if dataType=='xml':
        from cStringIO import StringIO
        result = StringIO()
        result.write("<?xml version='1.0' encoding='utf-8'?>\n<objects type='list'>\n")
        for item in data:
            try:
                result.write("<object id='%s'>\n<value>%s</value></object>\n" % (str(item['id']), str(item['value'])))
            except Exception as e:
                #result.write(str(e))
                pass
            else:
                result.write('')
        result.write('</objects>')
        return XML(result.getvalue())
    return str(data)
