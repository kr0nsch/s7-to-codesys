# Ручные шаги

Что делает человек: установка CODESYS и coUnit, импорт в проект, сборка и тесты в CODESYS Control Win,
ручные объекты проекта. Всё, что выполняется без CODESYS (конвертер, линтер, статанализ, RuSTy), — в
[README](../README.md#быстрый-старт-без-железа) и в CI.

Команды CODESYS выполняет `tools/codesys/cds.py` (подробно — [tools/README.md](../tools/README.md),
раздел «codesys/cds.py»). Скрипты проверены на CODESYS 3.5.17.30 при создании шаблона; **проект
s7-to-codesys в CODESYS ещё не собирался** — после первого прогона итог записывается в
[TEST_REPORT.md](TEST_REPORT.md), ошибки сборки — в [BUILD_ERRORS.md](BUILD_ERRORS.md).

## 1. Установка

1. CODESYS V3.5 SP17 Patch 3 (3.5.17.30) с сайта ОВЕН с компонентом CODESYS Control Win V3.
2. Для ПЛК210 — пакет таргет-файлов ОВЕН («Инструменты → Установщик пакетов»); версию таргет-файла
   сверить с прошивкой ПЛК.
3. Библиотека coUnit 1.2.0.0 (CfUnit, MIT; в коде пространство имён `coUnit`) — в репозиторий
   библиотек `System`. Если её нет, `cds.py` установит её из файла, заданного переменной
   `COUNIT_LIBRARY`. Параметры библиотеки — по умолчанию (на Control Win собирается без C0106 —
   [ASSUMPTIONS.md](ASSUMPTIONS.md), C7).
4. Переменные окружения пользователя (через `setx` их видит `cds.py` и без перезапуска консоли):

   | Переменная | Значение |
   |---|---|
   | `CODESYS_EXE` | путь к `CODESYS.exe` |
   | `CODESYS_PROFILE` | `CODESYS V3.5 SP17 Patch 3` |
   | `COUNIT_LIBRARY` | путь к `counit.library`, если библиотеки нет в репозитории |

5. Пользовательский процесс рантайма (без прав администратора): `python tools/codesys/cds.py runtime init`
   один раз, дальше `cds.py test` запускает рантайм сам.

## 2. Пересборка корпуса (если менялись конвертер, корпус или сценарии)

```bash
python -m s7conv build-corpus          # src/*/Converted, отчёт, задачи в config.json, тесты сценариев
python -m s7conv build-corpus --check  # то же без записи: код 1, если репозиторий устарел (так в CI)
```

Сгенерированное (`src/*/Converted`, `tests/POUs/Scenarios`, `tests/POUs/PRG_Tests`) руками не правится —
правка в IDE будет потеряна при следующей пересборке. Решение о `F_TRIG` (раздел 5) меняет настройки
сборки в `s7conv/corpus.py` (`corpus_options`).

## 3. Импорт, сборка, тесты

```bat
python tools\codesys\cds.py build            :: src/ → build\s7-to-codesys.project, сборка
python tools\codesys\cds.py test             :: src/ + tests/ → тестовый проект, Control Win, coUnit
python tools\codesys\cds.py report           :: итог прогона → docs/TEST_REPORT.md
```

- Рабочий проект получает задачи из `tools/codesys/config.json` (режим `normal`): `MainTask` 10 мс
  (`PRG_Startup`, `PRG_Main`), `Task_OB30` 100 мс (`PRG_Cyclic_interrupt`). Тестовый — `TestTask` 10 мс
  → `PRG_Tests` и библиотеку coUnit.
- Артефакты: `build/build.log`, `build/build.json` (сообщения компилятора с файлом и строкой раскладки),
  `build/test-results.json`, `build/junit.xml`.
- Без лицензии Control Win работает 2 часа; `cds.py test` перезапускает рантайм, если он работает
  дольше 100 минут.

## 4. Что создаётся только руками

- [ ] Дерево устройств ПЛК210 и привязка каналов ввода-вывода. `GVL_IO` и `GVL_Markers` (папка
      `Converted`) содержат пересчитанные адреса S7 как заготовку — на ПЛК210 каналы модулей
      привязываются в дереве устройств ([methodology.md](methodology.md), «Масштабирование аналоговых
      сигналов»).
- [ ] Задача по событию для `PRG_Diagnostic_error_interrupt` (OB82): автоматически не создаётся.
- [ ] Свободный цикл для `MainTask`, если он нужен вместо 10 мс (`tools/codesys` создаёт только
      циклические задачи).
- [ ] Объект Persistent Variables, если реманентные данные переводятся в `PERSISTENT`
      (`s7conv --retain persistent`): в SP17 скриптом не создаётся.
- [ ] Символьная конфигурация / OPC UA / Modbus для HMI и SCADA.
- [ ] Функции неявной проверки (Add Object → POUs for implicit checks: `CheckDivDInt`, `CheckDivLInt`,
      `CheckBounds` и др.) — подключить на время наладки или записать, почему не нужны (пометки
      `expr.div_int`, MAPPING.md «Расхождения, которые конвертер не помечает»).
- [ ] Поведение после Stop → Start в CODESYS: флаг первого цикла не сбрасывается, код OB100 (`PRG_Startup`)
      и эмуляция `Initial_Call` не выполняются повторно — проверить, приемлемо ли это для объекта
      (в S7 каждый STOP → RUN — тёплый пуск с OB100).

## 5. После первого прогона тестов

1. `python tools/codesys/cds.py report` и разбор упавших тестов в [TEST_REPORT.md](TEST_REPORT.md)
   (раздел «Что ожидать при первом прогоне»).
2. **F_TRIG.** Если падает строка 1 сценария `FB_PumpAlternation/RotateOnStop` (`leadPump` = 2 вместо 1),
   F_TRIG CODESYS Standard даёт ложный спад на первом вызове. Тогда: в `s7conv/corpus.py` в
   `corpus_options` поставить `f_trig=M.S7COMPAT`, выполнить `python -m s7conv build-corpus`, повторить
   `cds.py test`, записать вывод в ASSUMPTIONS.md (S4, K18) и MAPPING.md (`fb.f_trig`). Если строка
   проходит — отметить S4 как подтверждённое.
3. Тесты `MatchesStandardInRealTime` сверяют таймеры S7Compat со Standard: расхождение — разобрать по
   семантике в объявлении блока (ASSUMPTIONS.md, K19), при необходимости поправить блок S7Compat.
4. Обновить таблицы «Последний прогон» в [STATIC_ANALYSIS.md](STATIC_ANALYSIS.md) результатами CI.

## 6. Экспорт перед коммитом

Правки в IDE допустимы только в рукописном коде (`S7Compat`, `tests/POUs/S7Compat`). Перед коммитом:

```bat
python tools\codesys\cds.py export --tests
git diff --stat
python -m s7conv build-corpus --check
```

Последняя команда должна пройти: если экспорт изменил сгенерированное, правку нужно перенести в
конвертер или корпус. Цикл «импорт → экспорт» без правок не должен давать диффа
(`python tools\codesys\cds.py roundtrip`).

## 7. Зеркало на GitVerse или GitFlic

```bash
git remote add mirror <url-зеркала>
git push mirror --all
git push mirror --tags
```
