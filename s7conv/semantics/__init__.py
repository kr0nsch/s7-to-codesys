"""Эталон поведения S7 по руководствам Siemens — независимо от понижения (s7conv/lower) и эмиттера.

net_eval — поток питания LAD/FBD (справочник LAD S7-300/400, s7kop__b.pdf), stl_machine — машина STL
S7-300 (справочник STL, AWL_e.pdf). Тест test_semantics_independent запрещает здесь импорт lower, emitter,
plcopen и mapping: эталон и транслятор делят только разбор XML (риск общих ошибок — docs/EQUIVALENCE.md).
"""
