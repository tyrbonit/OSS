# -*- coding: utf-8 -*-

def index(): return dict(message="hello from bridge.py")

def getArc():
    import mx.DateTime as dtutils
    deltaDateTime = request.vars.get('deltaDateTime', '3600')
    startDate = request.vars.get('startDate', '')
    endDate = request.vars.get('endDate', '')
    queryString = request.vars.get('queryString', '')
    dataType = request.vars.get('dataType', 'xml')
    useScheme = request.vars.get('useScheme', None)
    shift = float(request.vars.get('shift', 0))

    endRT = dtutils.Parser.DateTimeFromString(endDate)
    startRT = dtutils.Parser.DateTimeFromString(startDate)
