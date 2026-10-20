# Архитектура

Проект — конвертер `s7conv` (Python) и его результат: сконвертированный корпус SCL в раскладке ST
CODESYS ([LAYOUT.md](LAYOUT.md)), слой совместимости S7Compat и тесты поведения по сценариям. Источник
истины — тексты: корпус `samples/scl/`, сценарии `scenarios/*.csv`, рукописный ST и код конвертера;
всё сгенерированное воспроизводится командой `python -m s7conv build-corpus` и проверяется в CI.

## Поток данных

```mermaid
flowchart LR
    subgraph inp["Вход (выгрузка TIA Portal)"]
        scl["samples/scl/*.scl<br/>FB, FC, OB, DB, UDT"]
        tags["PlcTags.csv,<br/>ob_config.json"]
    end
    subgraph conv["s7conv (Python)"]
        parse["lexer + parser<br/>рекурсивный спуск → AST"]
        sym["symbols<br/>блоки, DB, теги, адреса"]
        emit["emitter<br/>ST, пометки MIGRATION-*"]
        gen["testgen<br/>сценарии → coUnit"]
    end
    subgraph out["Репозиторий"]
        convd["src/*/Converted/<br/>(генерируется)"]
        compat["src/*/S7Compat/<br/>F_NormX, F_ScaleX,<br/>FB_S7Ton/Tof/Tp, F_S7Now"]
        rep["docs/CONVERSION_REPORT.md"]
        cfg["tools/codesys/config.json<br/>задачи из OB"]
        tst["tests/POUs/Scenarios/<br/>tests/POUs/PRG_Tests<br/>(генерируются)"]
        hand["tests/POUs/S7Compat/<br/>рукописные тесты"]
    end
    subgraph sc["Сценарии"]
        desc["описание логики<br/>в заголовке .scl"]
        model["scenarios/reference/<br/>эталонные модели"]
        csv["scenarios/*.csv"]
    end
    scl --> parse --> sym --> emit
    tags --> sym
    emit --> convd
    emit --> rep
    emit --> cfg
    desc --> model --> csv --> gen
    sym --> gen
    gen --> tst
    convd -. вызывает .-> compat
```

| Модуль `s7conv/` | Роль |
|---|---|
| `lexer.py`, `parser.py`, `nodes.py` | разбор SCL TIA Portal в AST с восстановлением после ошибок ([GRAMMAR.md](GRAMMAR.md)) |
| `symbols.py` | таблица символов корпуса, модель адресов S7 → CODESYS, таблица тегов |
| `mapping.py` | таблицы соответствий: типы, ФБ инструкций, функции, литералы, имена; режимы таймеров и F_TRIG; объекты S7Compat и их зависимости ([MAPPING.md](MAPPING.md)) |
| `emitter.py` | генерация объектов раскладки через `tools/codesys/stlayout.py`, вывод типов, пометки и статусы |
| `tasks.py` | OB → задачи CODESYS |
| `report.py` | отчёт Markdown и HTML |
| `testgen.py` | чтение сценариев CSV, сопоставление имён по таблицам конвертера, наборы coUnit, `PRG_Tests` |
| `corpus.py` | `build-corpus`: корпус → `src/*/Converted`, отчёт, задачи в `config.json`, тесты; `--check` |
| `pipeline.py`, `cli.py` | входные файлы, запись раскладки; команды `convert`, `report`, `check`, `build-corpus`, `gen-tests` |

## Проект CODESYS

| Папка проекта | Каталог | Что |
|---|---|---|
| `Converted` | `src/DUTs/Converted`, `src/GVLs/Converted`, `src/POUs/Converted` | сконвертированный корпус: 7 DUT, 6 GVL (`DB_Plant`, `DB_Hmi`, `DB_Telegram`, `GVL_InstanceDBs`, `GVL_IO`, `GVL_Markers`), 14 ФБ, 1 функция, 4 программы из OB |
| `S7Compat` | `src/POUs/S7Compat`, `src/GVLs/S7Compat` | рукописный слой совместимости ([MAPPING.md](MAPPING.md), «Слой совместимости S7Compat») |
| `Tests/S7Compat` | `tests/POUs/S7Compat` | юнит-тесты слоя совместимости, в том числе сверка таймеров со Standard в реальном времени |
| `Tests/Scenarios` | `tests/POUs/Scenarios` | тесты поведения сконвертированных блоков по сценариям CSV |
| `Tests` | `tests/POUs/PRG_Tests` | программа запуска тестов |

Задачи рабочего проекта (`tools/codesys/config.json`, режим `normal`) — из OB корпуса: `MainTask`
10 мс (`PRG_Startup`, `PRG_Main`) и `Task_OB30` 100 мс (`PRG_Cyclic_interrupt`); тестовый проект
(режим `test`) — `TestTask` 10 мс → `PRG_Tests` и библиотека coUnit. Импорт, сборка и прогон тестов —
`python tools/codesys/cds.py import | build | test` ([MANUAL_STEPS.md](MANUAL_STEPS.md)).

## Контуры проверок

| Контур | Где | Что ловит |
|---|---|---|
| Python | CI и локально: ruff, mypy, pytest | разбор, эмиттер, генератор тестов, снапшот корпуса (`build-corpus` воспроизводит закоммиченное побайтно), RuSTy по всему `src/` и `tests/`; наборы coUnit, исполненные интерпретатором ST (`s7conv/sim/stsim.py`) против закоммиченного кода, и мутации логики |
| ST без CODESYS | CI и локально: `st_lint`, `assemble.py`, iec_checker (`run_iec_checker.py --tests`), RuSTy | раскладка, оформление, синтаксис и типы, статанализ ([STATIC_ANALYSIS.md](STATIC_ANALYSIS.md)) |
| CODESYS | Windows, CODESYS 3.5.17.30 и Control Win V3 | компиляция CODESYS, тесты coUnit ([TEST_REPORT.md](TEST_REPORT.md)) |

## Каталоги

| Каталог | Содержимое |
|---|---|
| `s7conv/` | конвертер и его тесты (`s7conv/tests`, снапшоты фикстур) |
| `samples/scl/` | корпус SCL (20 файлов, 44 блока), таблица тегов, `ob_config.json`, матрица покрытия |
| `scenarios/` | сценарии CSV, эталонные модели и их тесты (`scenarios/reference`) |
| `src/`, `tests/` | раскладка ST: сгенерированное и рукописное (таблица выше) |
| `tools/` | инструменты шаблона: `assemble.py`, `check/` (линтер, iec_checker, RuSTy), `codesys/` (CODESYS из консоли) |
| `tools_project/` | проверки настроек репозитория проекта (`st_lint.toml`, `config.json`) |
| `docs/` | документация и отчёты |
| `build/` | артефакты сборки и проверок, в git не хранится |

## Все языки (выпуск 1.1.0)

С выпуска 1.1.0 вход — не только SCL, но и SimaticML (XML экспорта TIA Portal Openness) на LAD, FBD,
STL и SCL, с 1.2.0 — и S7-GRAPH. Новые модули понижают эти языки в текст SCL, дальше он идёт прежним путём;
из последовательности GRAPH дополнительно строится вариант SFC в PLCopen XML.

```mermaid
flowchart LR
    X["SimaticML *.xml"] --> FX["frontends/simaticml<br/>Document, Interface,<br/>CompileUnit"]
    FX --> N["ir/net: NetIR<br/>Part, Access, Wire"]
    FX --> T["ir/stl: StlIR<br/>токены XSD V21"]
    FX --> G["ir/seq: SeqIR<br/>шаги, переходы, ветви"]
    FX -->|сеть SCL| SCLT["текст SCL"]
    N -->|lower/net_to_ast| SCLT
    T -->|lower/stl_lift<br/>structured / pc| SCLT
    G -->|lower/seq_to_ast<br/>ST-двойник| SCLT
    G -->|plcopen/sfc| PO["plcopen/Lang/Converted<br/>SFC + обёртка"]
    S["*.scl, *.db, *.udt"] --> P["parser.py 1.0.0"]
    SCLT --> P
    P --> E["emitter, mapping,<br/>symbols, report 1.0.0"]
    E --> ST["src/*/Lang/Converted"] & R["отчёт «По языкам»"] & TG["testgen → coUnit"]
    N & T & G --> SEM["semantics: эталон S7<br/>net_eval, stl_machine, graph_seq"] --> EQ["equiv"]
    ST --> SIM["stsim"] --> EQ
```

| Модуль `s7conv/` | Роль |
|---|---|
| `frontends/simaticml.py` | разбор SimaticML (`xml.etree`, без внешних сущностей): блоки, интерфейс, сети по `ProgrammingLanguage`; `Access` → текст SCL |
| `ir/net.py`, `ir/stl.py`, `ir/seq.py` | NetIR (граф сети LAD/FBD), StlIR (инструкции STL по имени токена XSD), SeqIR (последовательность GRAPH и топология переходов) |
| `lower/net_to_ast.py` | LAD/FBD → SCL: поток питания, словарь элементов `PARTS`, прыжки вперёд → IF |
| `lower/stl_lift.py`, `lower/stl_tokens.py` | STL → SCL: символьный подъём, переходы `structured`/`pc`; матрица 172 токенов |
| `lower/seq_to_ast.py` | GRAPH → SCL ST-двойника: порядок цикла, ветви, действия, контроль, блокировка (`docs/MAPPING_GRAPH.md`) |
| `lower/block.py` | блок → текст SCL с трассой каждой строки (`сеть 3, UId 27`) и пометками понижения |
| `plcopen/` | вариант SFC блока GRAPH в PLCopen XML: POU SFC и ФБ-обёртка; импорт в CODESYS — `tools_project/cds_plcopen.py` |
| `semantics/` | эталон S7, независимый от понижения: `net_eval`, `stl_machine`, `s5` (таймеры и счётчики S5), `graph_seq` (последовательность GRAPH), таймеры и счётчики IEC |
| `sim/stsim.py` | интерпретатор ST (переехал из `s7conv/tests/stsim.py`, старый путь — реэкспорт) |
| `equiv.py`, `irdump.py`, `docs_gen.py` | команды `equiv` и `ir`; генерация `MAPPING_LADFBD.md`, `MAPPING_STL.md` |

### Почему так

- **AST SCL вместо нового промежуточного представления уровня ST.** Все языки понижаются в текст SCL,
  который разбирает `parser.py` 1.0.0: эмиттер (около 2600 строк), отчёт, таблицы соответствий и генератор
  тестов переиспользуются без копий. Происхождение строк (`Lowering.trace`) и пометки понижения
  (`Lowering.notes`) едут рядом с текстом и попадают в пометки ST и отчёт.
- **XML из стандартной библиотеки.** `xml.etree` без зависимостей: тот же код можно запустить в браузере
  (Pyodide) и в любом окружении CI; DOCTYPE и сущности отклоняются до разбора.
- **Структурные переходы вместо JMP.** RuSTy и iec_checker не разбирают `JMP` и метки — их нельзя было бы
  проверять статанализом; IF/ELSE и автомат CASE читаются и проверяются как обычный ST.
- **Один проект CODESYS на два корпуса.** Корпус всех языков лежит в `src/*/Lang/Converted`, генерируемые
  GVL — с суффиксом `_Lang` (`--global-suffix`); сборка проверяет, что имена объектов и членов GVL двух
  корпусов не совпадают. Папка `Lang/Converted` подпадает под шаблоны `src/*/Converted/*` настроек
  статанализа (`tools/check`), а `src/*/Converted` корпуса SCL 1.0.0 не меняется.
- **Эталон независим от понижения.** `semantics/` не импортирует `lower`, `emitter`, `mapping`: эталон и
  транслятор делят только разбор XML ([EQUIVALENCE.md](EQUIVALENCE.md)).

### Проект CODESYS: новые папки

| Папка проекта | Каталог | Что |
|---|---|---|
| `Lang/Converted` | `src/{DUTs,GVLs,POUs}/Lang/Converted` | корпус всех языков: 4 перевода `FB_Starter`, `FB_PumpInterlockLad`, `FC_ClampPctLad`, `DB_Process`, `UDT_Valve` |
| `S7Compat` | `src/POUs/S7Compat/F_S7Eno*` | функции ENO арифметики S7 |
| `Tests/ScenariosLang` | `tests/POUs/ScenariosLang` | наборы сценариев `scenarios/lang` (объявлены в `PRG_Tests`) |
