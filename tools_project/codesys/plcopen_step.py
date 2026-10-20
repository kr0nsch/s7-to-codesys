# -*- coding: utf-8 -*-
"""Шаг plcopen задания cds_plcopen.py: импорт файлов PLCopen XML в приложение проекта (IronPython 2.7).

Шаг выполняется в одном процессе CODESYS после шага import (ST из раскладки) и перед build/test:
    {"action": "plcopen", "project": "<.project>", "files": ["<file>.xml", ...], "log": ..., "report": ...}
Импорт — `app.import_xml(reporter, path, True)` (пространство имён tc6_0200, проверено на CODESYS 3.5.17.30).
Ошибки и предупреждения импорта пишутся в отчёт; ошибка импорта — StepError (сборка не начинается).
Общее подмножество Python 2.7 и 3: без f-строк и аннотаций.
"""
from __future__ import absolute_import, print_function, unicode_literals

import os

import cds_common as C


class _Reporter(object):
    """Обёртка над ImportReporter CODESYS: сообщения в список, конфликт имён — замена."""

    def __init__(self):
        self.messages = []

    def make(self):
        se = C.api()
        outer = self

        class Reporter(se.ImportReporter):
            def error(self, message):
                outer.messages.append({'level': 'error', 'text': C._text(message)})

            def warning(self, message):
                outer.messages.append({'level': 'warning', 'text': C._text(message)})

            def resolve_conflict(self, obj):
                outer.messages.append({'level': 'conflict', 'text': C.obj_name(obj)})
                return se.ConflictResolve.Replace

            def added(self, obj):
                outer.messages.append({'level': 'added', 'text': C.obj_name(obj)})

            def replaced(self, obj):
                outer.messages.append({'level': 'replaced', 'text': C.obj_name(obj)})

            def skipped(self, objectname):
                outer.messages.append({'level': 'skipped', 'text': C._text(objectname)})

            @property
            def aborting(self):
                return False

        return Reporter()


def run(ctx, step):
    log = C.Log(step.get('log'))
    proj, _created = ctx.open_project(step['project'], log=log)
    app = C.application(proj)
    report = {'files': [], 'added': [], 'errors': [], 'warnings': []}
    for path in step.get('files') or []:
        if not os.path.isfile(path):
            raise C.StepError('нет файла PLCopen %s' % path)
        holder = _Reporter()
        log.info('импорт PLCopen %s' % path)
        try:
            app.import_xml(holder.make(), path, True)
        except Exception as exc:
            raise C.StepError('импорт %s: %s' % (path, C.squash_ws(C._text(exc))))
        report['files'].append(path)
        for msg in holder.messages:
            level = msg['level']
            if level in ('added', 'replaced'):
                report['added'].append(msg['text'])
            elif level == 'error':
                report['errors'].append(msg['text'])
            elif level == 'warning':
                report['warnings'].append(msg['text'])
            log.info('  %s: %s' % (level, msg['text']))
    if step.get('export'):
        C.ensure_dir(os.path.dirname(step['export']))
        proj.export_xml([app], path=step['export'], recursive=True, export_folder_structure=True,
                        declarations_as_plaintext=True)
        report['export'] = step['export']
    proj.save()
    if step.get('report'):
        C.write_json(step['report'], report)
    if report['errors']:
        raise C.StepError('ошибки импорта PLCopen: %s' % '; '.join(report['errors']))
    return {'ok': True, 'added': report['added'], 'warnings': report['warnings']}
