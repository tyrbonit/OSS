#!/usr/bin/env python
# -*- coding: utf-8 -*-

def queryParser(queryString):
    queryString = str(queryString).strip()
    s_operator = queryString.split(' ', 1)
    operatorLen = len(s_operator[0])
    if s_operator[0] == 'select':
        return parseSelect(queryString[operatorLen:len(queryString)].strip())
    return 'error'


def getparameters(paramsString):
    s_params = paramsString.replace('@', '').split(',')
    return s_params


def parseSelect(queryString):
    queryChildren = False
    queryString = queryString.strip()
    if queryString.startswith('withChildren'):
        queryChildren = True
        queryString = queryString[12:].strip()
    s_operator = queryString.split(']', 1)
    s_parameters = getparameters(s_operator[0][1:len(s_operator[0])])
    queryString = queryString[len(s_operator[0]):len(queryString)]
    s_words = queryString[1:len(queryString)].strip().split(' ', 1)
    if s_words[0].strip() != 'from':
        return 'error [from is not exist]'
    s_path = None
    s_conditions = None
    if s_words[1]:
        ss_words = s_words[1].split('[', 2)
        if len(ss_words):
            s_path = ss_words[0]
        if len(ss_words) > 1:
            s_conditions = ss_words[1][0:len(ss_words[1]) - 1]
    return (s_path, s_parameters, s_conditions, queryChildren)
