# -*- coding: utf-8 -*-
"""Точка входа CODESYS для tools_project/cds_plcopen.py (IronPython 2.7): шаги import, plcopen, build, test.

Модули шаблона (tools/codesys: cds_common, import_sources, build, run_tests) только импортируются и не
меняются; шаг plcopen (импорт PLCopen XML) добавляется в таблицу действий cds_common.ACTION_MODULES.
Путь к tools/codesys — в переменной окружения S7_TOOLS_CODESYS (её ставит cds_plcopen.py).
"""
from __future__ import absolute_import, print_function, unicode_literals

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.environ.get('S7_TOOLS_CODESYS', os.path.join(HERE, '..', '..', 'tools', 'codesys')))
sys.path.insert(0, HERE)

import cds_common as C  # noqa: E402

C.ACTION_MODULES['plcopen'] = 'plcopen_step'

if __name__ == '__main__':
    C.run_main('test')
