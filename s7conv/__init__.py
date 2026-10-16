"""s7conv — частичный автоматический конвертер Siemens SCL (TIA Portal) в ST CODESYS V3.5.

Модули:
- lexer — лексер SCL (TIA Portal external source) с сохранением комментариев;
- nodes — модель AST (dataclasses);
- parser — рекурсивный спуск с восстановлением после ошибок;
- sclprint — печать выражений обратно в SCL (для тестов «разбор ∘ печать»);
- mapping — таблицы соответствий: типы, функции, литералы, имена;
- symbols — таблица символов проекта: блоки, DB, теги, адреса;
- emitter — генерация ST в раскладке шаблона (tools/codesys/stlayout.py);
- tasks — OB → задачи CODESYS;
- report — отчёт конвертации (Markdown, HTML);
- pipeline — входные файлы, таблица тегов, запуск, запись раскладки и tasks.json;
- testgen — генератор тестов coUnit по сценариям CSV (scenarios/) для сконвертированных блоков;
- corpus — сборка корпуса samples/scl в раскладку репозитория (`s7conv build-corpus`, `--check`);
- layout — доступ к tools/codesys/stlayout.py (единственная реализация раскладки шаблона);
- cli — командная строка `s7conv`.

Документация: docs/GRAMMAR.md (подмножество SCL), docs/MAPPING.md (таблица соответствий),
docs/CONVERSION_REPORT.md (отчёт по корпусу samples/scl/), docs/methodology.md (методика миграции).
"""

from __future__ import annotations

__version__ = "0.1.0"

__all__ = ["__version__"]
