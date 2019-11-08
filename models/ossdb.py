# -*- coding: utf-8 -*-
import re, time

db.define_table('ossgroups',
                Field('name',
                      unique=True,
                      label='Наименование группы',
                      comment='Допускаются только латинские буквы, знак "_" вместо пробела и ":" для деления на подгруппы. Введеное значение будет преобразовано в нижний регистр.',
                      requires = [IS_LOWER(), IS_MATCH('^([\w_]+?)(\:[\w_]+?)*?$', error_message='Допускаются латинские буквы, знак "_" и ":"')]
                     ),
                Field('title', label='Описание группы'),
                format="%(name)s",
               )

SBSP = re.compile("([^_\^]+)|([_\^])([^_\^\n]+)")
def subsup(txt):
    if txt is None: return
    func = {"_":TAG.sub,"^":TAG.sup}
    return SPAN(*[func.get(x[1], lambda y:x[0])(x[2]) for x in SBSP.findall(txt)])

def param_representer(value=None, row=None):
    if row:
        return SPAN(subsup(row.label),
                    data=dict(toggle="tooltip"),
                    _title="(%s) %s"%(row.uuid, row.name))
    else:
        return value

db.define_table('ossbase',
                Field('group_id', 'reference ossgroups', label='Группа параметров'),
                Field('uuid', unique=True, label='uuid',
                      writable=False, readable=False,
                      default=int(time.time() * 100)),
                Field('name', label='Наименование'),
                Field('label', label='Обозначение'),
                Field('unit', label='Ед.изм.'),
                Field('agrt', label='Метод агрегации',
                      requires = IS_IN_SET([('a','Среднее'),('s','Сумма'),('w','Взвешивание')]),
                      default='a'),
                Field('weight', 'reference ossbase', label='По параметру',
                      filter_in = lambda uuid: db.ossbase(db.ossbase.uuid==uuid).id if uuid else None,
                      filter_out = lambda id: db.ossbase(id).uuid if id else None,
                     ),
                Field('caller', 'json', label='Источник', writable=False, readable=False, represent = BEAUTIFY),
                auth.signature,
                format=lambda row: param_representer(row=row),
               )

db.ossbase.name.represent=lambda v: DIV(v)
db.ossbase.label.represent=lambda v, r: param_representer(v, r)
db.ossbase.weight.show_if = (db.ossbase.agrt=='w')
db.ossbase.weight.requires = IS_EMPTY_OR(IS_IN_DB(db(db.ossbase.agrt=='c'), 'ossbase.uuid', lambda r: param_representer(row=r)))
