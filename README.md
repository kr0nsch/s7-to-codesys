<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/media/banner-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="docs/media/banner-light.svg">
    <img alt="Баннер s7-to-codesys: код SCL слева и сконвертированный ST CODESYS справа" src="docs/media/banner-light.svg" width="100%">
  </picture>
</p>

<p align="center">
  <a href="https://github.com/kr0nsch/s7-to-codesys/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/kr0nsch/s7-to-codesys/actions/workflows/ci.yml/badge.svg"></a>
  <a href="LICENSE"><img alt="Лицензия MIT" src="https://img.shields.io/badge/license-MIT-56677D?style=flat-square&labelColor=1B2736"></a>
  <img alt="CODESYS 3.5.17" src="https://img.shields.io/badge/CODESYS-3.5.17-C2410C?style=flat-square&labelColor=1B2736">
  <img alt="IEC 61131-3" src="https://img.shields.io/badge/IEC%2061131--3-56677D?style=flat-square">
  <a href="#тесты-и-проверки"><img alt="Тесты: coUnit 74 из 74 в CODESYS Control Win, pytest 1027" src="https://img.shields.io/badge/tests-coUnit%2074%2F74%20%C2%B7%20pytest%201027-3A4B60?style=flat-square&labelColor=1B2736"></a>
  <img alt="Язык: Python" src="https://img.shields.io/badge/Python-3A4B60?style=flat-square&logo=python&logoColor=white">
  <img alt="Язык: Structured Text" src="https://img.shields.io/badge/Structured%20Text-3A4B60?style=flat-square">
</p>

<p align="center">
  <a href="#демонстрация">Демо</a> ·
  <a href="#архитектура">Архитектура</a> ·
  <a href="#быстрый-старт-без-железа">Быстрый старт</a> ·
  <a href="docs/">Документация</a> ·
  <a href="#summary-en">Summary (EN)</a>
</p>

**Миграция с Siemens S7 на CODESYS без иллюзий.** Инструмент и методика частичной миграции программ
S7 (SCL из TIA Portal) на CODESYS V3.5. Конвертер `s7conv` переводит исходники SCL в ST в раскладке
CODESYS и считает, что переведено автоматически, что требует проверки и что не поддерживается, — всё
неоднозначное остаётся в коде пометкой с причиной. Поведение сконвертированных блоков проверяют тесты
coUnit, построенные из сценариев по описанию логики, а не по результату конвертера: весь корпус собран в
CODESYS 3.5.17.30, все 74 теста пройдены в CODESYS Control Win.

## Демонстрация

Всё ниже — с реальных прогонов на машине разработки: `s7conv` на корпусе `samples/scl`, CODESYS
3.5.17.30 и CODESYS Control Win V3. Код на картинках — файлы репозитория как есть. Макетов нет.

<p align="center">
  <img alt="Терминал: s7conv переводит 20 файлов SCL (998 конструкций, 94 % автоматически), build-corpus --check сверяет репозиторий, cds.py test --clean — сборка без ошибок и 74 из 74 тестов coUnit" src="docs/media/demo-convert-test.gif" width="900">
</p>
<p align="center"><sub>Конвертация корпуса → сверка с закоммиченным результатом → тестовый проект CODESYS с нуля и прогон coUnit в Control Win. Реальная сессия 19.10.2026, снято term2gif; ожидание CODESYS (46 с) в записи сокращено</sub></p>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/media/shot-scl-vs-st-dark.png">
    <source media="(prefers-color-scheme: light)" srcset="docs/media/shot-scl-vs-st-light.png">
    <img alt="FB_Motor рядом: исходник SCL и результат s7conv в ST CODESYS с настоящими номерами строк; отмечены замены TON_TIME на FB_S7Ton, REGION на комментарии и сборка вызова в одну строку" src="docs/media/shot-scl-vs-st-light.png" width="100%">
  </picture>
</p>
<p align="center"><sub>Один блок корпуса: <code>samples/scl/FB_Motor.scl</code> и <code>src/POUs/Converted/FB_Motor</code> без правок (подсветка и выноски добавлены при отрисовке); его 7 сценариев пройдены в Control Win</sub></p>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/media/shot-migration-marks-dark.png">
    <source media="(prefers-color-scheme: light)" srcset="docs/media/shot-migration-marks-light.png">
    <img alt="Пометки ручной работы: срезы .%W0 и .%B1 переведены с пометкой MIGRATION-CHECK, а BLKMOV и абсолютные адреса DB закомментированы с пометкой MIGRATION-TODO и причиной" src="docs/media/shot-migration-marks-light.png" width="100%">
  </picture>
</p>
<p align="center"><sub>Что конвертер не решает за инженера: <code>MIGRATION-CHECK</code> — переведено, но сверить; <code>MIGRATION-TODO</code> — аналога нет, исходный текст закомментирован</sub></p>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/media/shot-conversion-report-dark.png">
    <source media="(prefers-color-scheme: light)" srcset="docs/media/shot-conversion-report-light.png">
    <img alt="HTML-отчёт конвертации корпуса: 94 % конструкций переведены автоматически (942 из 998), 26 требуют проверки, 30 не поддерживаются, 20 файлов и 44 блока, доли по видам конструкций" src="docs/media/shot-conversion-report-light.png" width="100%">
  </picture>
</p>
<p align="center"><sub>Верх отчёта <code>s7conv report --html</code> по корпусу, снимок страницы в браузере (тёмная и светлая тема отчёта). Разбор по файлам и причинам — в самом отчёте и в <a href="docs/CONVERSION_REPORT.md">CONVERSION_REPORT.md</a></sub></p>

<details>
<summary>Тот же принцип текстом: <code>FB_AnalogIn</code> и <code>FB_LegacyTelegram</code></summary>

SCL (`samples/scl/FB_AnalogIn.scl`):

```text
#rawClamped := LIMIT(MN := #RAW_NOMINAL_LOW, IN := #raw, MX := #RAW_NOMINAL_HIGH);
#normalized := NORM_X(MIN := #RAW_NOMINAL_LOW, VALUE := #rawClamped, MAX := #RAW_NOMINAL_HIGH);
#value := SCALE_X(MIN := #rangeLow, VALUE := #normalized, MAX := #rangeHigh);
```

ST после `s7conv` (`src/POUs/Converted/FB_AnalogIn/FB_AnalogIn.impl.st`) — имена и структура исходника
сохранены, NORM_X/SCALE_X заменены функциями слоя совместимости с той же формулой:

```text
rawClamped := LIMIT(RAW_NOMINAL_LOW, raw, RAW_NOMINAL_HIGH);
normalized := F_NormX(rMin := RAW_NOMINAL_LOW, rValue := rawClamped, rMax := RAW_NOMINAL_HIGH);
value := F_ScaleX(rMin := rangeLow, rValue := normalized, rMax := rangeHigh);
```

То, что перевести нельзя, остаётся закомментированным с причиной (`FB_LegacyTelegram`):

```text
// MIGRATION-TODO: BLKMOV: нет прямого аналога в CODESYS Standard (стр. 98)
// #retVal := BLKMOV(SRCBLK := #source, DSTBLK => P#DB30.DBX4.0 BYTE 16);
```

</details>

## Архитектура

```mermaid
flowchart LR
    subgraph conv["s7conv: перевод"]
        scl["samples/scl/*.scl<br/>PlcTags.csv, ob_config.json"] --> parse["лексер + парсер<br/>рекурсивный спуск"]
        parse --> ast["AST"]
        ast --> emit["эмиттер ST<br/>таблицы соответствий"]
        emit --> layout["раскладка ST<br/>src/*/Converted"]
        emit --> rep["отчёт конвертации<br/>Markdown и HTML"]
        emit --> tasks["задачи из OB<br/>config.json"]
    end
    subgraph beh["проверка поведения"]
        desc["описание логики<br/>в заголовке .scl"] --> models["эталонные модели<br/>scenarios/reference"]
        models --> csv["сценарии CSV<br/>scenarios/*.csv"]
        csv --> gen["генератор тестов<br/>s7conv gen-tests"]
        gen --> suites["наборы coUnit<br/>tests/POUs/Scenarios"]
    end
    compat["S7Compat, рукописный<br/>F_NormX, F_ScaleX,<br/>FB_S7Ton/Tof/Tp"] -.-> layout
    layout --> cds["CODESYS 3.5.17.30<br/>cds.py build, test"]
    tasks --> cds
    suites --> cds
    cds --> trep["TEST_REPORT.md"]
```

- **Разбор** — рукописный рекурсивный спуск с восстановлением после ошибок и переносом комментариев
  ([docs/GRAMMAR.md](docs/GRAMMAR.md)); **соответствия** S7 → CODESYS — [docs/MAPPING.md](docs/MAPPING.md).
- **Перенос один к одному**: имена, числа и структура исходника сохраняются, чтобы код сверялся с SCL, а
  теги HMI и SCADA — по именам. Глобальный DB → GVL с тем же именем, экземплярные DB → `GVL_InstanceDBs`,
  OB → программы и задачи, `%I/%Q/%M` → слой ввода-вывода с пересчитанными адресами.
- **Слой совместимости S7Compat** — рукописные `F_NormX`/`F_ScaleX` (формулы NORM_X/SCALE_X) и таймеры
  `FB_S7Ton/Tof/Tp` с подменяемым источником времени: тесты ставят часы на момент строки сценария и
  проверяют поведение ровно на пороге таймера за один цикл ПЛК.
- **Проверка поведения** — сценарии CSV для 6 блоков (39 сценариев, 263 вызова) посчитаны эталонными
  моделями по описанию логики; генератор строит из них наборы coUnit для сконвертированного кода.

Подробно — [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md); методика миграции и выбор способа тестирования —
[docs/methodology.md](docs/methodology.md).

## Быстрый старт без железа

Нужен Python 3.11+ (в CI — 3.12). CODESYS не нужен.

```bash
python -m pip install -r requirements-dev.txt

python -m s7conv check samples/scl                    # разбор: ошибки со строками
python -m s7conv convert samples/scl --out build/converted --emit-support \
       --report-html build/report.html                # перевод в раскладку + отчёт HTML
python -m s7conv build-corpus --check                 # закоммиченный результат воспроизводится
python -m s7conv --help                               # все команды и параметры

python -m pytest                                      # тесты конвертера, генератора, настроек
python tools/check/st_lint.py --strict                # линтер ST
python tools/check/run_iec_checker.py --tests         # статанализ (iec_checker v0.4: --binary или IEC_CHECKER)
python tools/check/run_rusty.py                       # необязательно: RuSTy plc --check
```

`s7conv convert` пишет раскладку `src/{DUTs,GVLs,POUs}/...` и `tasks.json`; таблицы тегов `*.csv` и
`ob_config.json` во входном каталоге подхватываются сами. `--timers s7compat` и `--f-trig s7compat`
включают объекты S7Compat вместо TON/TOF/TP и F_TRIG Standard, `--retain persistent` — `PERSISTENT` вместо
`RETAIN`. После `python -m pip install -e .` доступна команда `s7conv`.

**Корпус в репозитории** собирается одной командой — `python -m s7conv build-corpus`: код в папку проекта
`Converted`, отчёт, задачи в `tools/codesys/config.json`, тесты сценариев и `PRG_Tests`. CI проверяет
`--check`: сгенерированное не правится руками и всегда совпадает с выводом конвертера.

## Границы автоматизации

Корпус `samples/scl/` — 20 файлов, 44 блока (ФБ, FC, OB, глобальные и экземплярные DB, UDT; вымышленная
водопроводная станция), 998 конструкций ([docs/CONVERSION_REPORT.md](docs/CONVERSION_REPORT.md)):

| Статус | Конструкций | Что в коде |
|---|---:|---|
| переведено автоматически | **942 (94 %)** | ST без замечаний; сюда входят конструкции, переведённые через рукописный S7Compat — его поведение покрыто тестами |
| требует проверки | **26 (3 %)** | ST + `// MIGRATION-CHECK: причина` (30 пометок: у блока OB их бывает несколько) |
| не поддерживается | **30 (3 %)** | `// MIGRATION-TODO: причина` и закомментированный исходный текст |

**Не поддерживается (30)** — то, что требует решения инженера, а не замены текста:

| Категория | Пометок |
|---|---:|
| системные функции без аналога в Standard: `RD_SYS_T`, `WR_SYS_T`, `RUNTIME`, `PEEK`, `POKE`, `BLKMOV`, `S_ODT`, `TypeOf` | 8 |
| типы без аналога: `Any` (2), `Variant`, `DTL`, `HW_ANY` | 5 |
| наложения `AT` (2), абсолютные адреса DB `%DB30.DBW0/2` (2), доступ к периферии `:P` (1) | 5 |
| `GOTO` и метки переходов | 4 |
| следствия неперенесённых объявлений: использование переменной (4), аргумент вызова (2) | 6 |
| `EN/ENO` | 1 |
| событийный OB82 — задача по событию | 1 |

16 из 30 приходятся на `FB_LegacyTelegram`: блок нарочно собран из конструкций STEP 7 V5.x, которые
автоматически не переносятся (`ANY`-указатель, `AT`, `BLKMOV`, абсолютная и косвенная адресация DB, `S_ODT`,
`GOTO`), и его заголовок описывает логику для ручного переноса.

**Требует проверки (26 конструкций, 30 пометок)** — переведено, но смысл зависит от платформы или проекта:
S5TIME → TIME (7), стартовая информация OB, `Initial_Call` и OB100 → флаг первого цикла (7), начальное
состояние `F_TRIG` (5 — у Standard 3.5.17.0 проверено, совпадает с S7; пометка остаётся для других версий
библиотеки), нумерация срезов `.%B/.%W` (3), неоптимизированные блоки и их реманентность (3),
переименование имён-ключевых слов (2), разные типы — `CTU` с `WORD` и `SCALE_X` с целым результатом (2),
`VAR RETAIN` в ФБ — весь экземпляр (1).

Доля конструкций — не доля труда: восемь системных функций и OB82 могут потребовать больше работы, чем
сотни автоматически переведённых присваиваний, а
расхождения, которые проявляются только во время работы (разрядность промежуточных результатов, индекс
вне границ, деление REAL на 0), конвертер не помечает вовсе — они в чек-листе
([methodology.md](docs/methodology.md), «Оценка трудоёмкости»; [MAPPING.md](docs/MAPPING.md), «Расхождения,
которые конвертер не помечает»).

## Тесты и проверки

**CODESYS 3.5.17.30 + CODESYS Control Win V3** (локально, Windows; 2026-10-16, повторено с чистого
`build/`) — [docs/TEST_REPORT.md](docs/TEST_REPORT.md):

| Команда `python tools/codesys/cds.py …` | Итог |
|---|---|
| `build` — рабочий проект: корпус, S7Compat, задачи из OB | ошибок 0, предупреждений 0 |
| `library` — «Проверить все объекты пула» (39 объектов, в том числе OB82 без задачи) | ошибок 0, предупреждений 0 |
| `build --tests` — тестовый проект с coUnit 1.2.0.0 | ошибок 0, предупреждений 0 |
| `test` — загрузка в Control Win, `TestTask` 10 мс | 13 наборов, 74 теста: **пройдено 74**, упало 0; все наборы завершились за 1,2 с |
| `roundtrip` — импорт → экспорт → сравнение | 242 файла совпадают побайтно; повторный импорт — 0 изменений |

Перед выпуском 1.0.0, 19.10.2026, повторены `cds.py check --tests` (54 объекта `src/` и `tests/`: 0 ошибок,
0 предупреждений) и `cds.py test --clean` (тестовый проект с нуля: импорт 138 объектов) — тот же итог,
74 из 74; такой прогон снят в GIF раздела [«Демонстрация»](#демонстрация).

Тесты не пустые: искажённые ожидания в CSV (в том числе в строке ровно на пороге таймера) CODESYS ловит
ровно теми тестами и сообщениями, а ошибка, внесённая в OB82 без задачи, видна в `library`, хотя `build`
её не компилирует (контрольные эксперименты — в TEST_REPORT.md). Что значат «0 предупреждений» (смена знака —
C0195, сужение — ошибка C0032) — [docs/STATIC_ANALYSIS.md](docs/STATIC_ANALYSIS.md).

**Без CODESYS** (CI и локально):

| Проверка | Итог |
|---|---|
| ruff, `ruff format --check`, mypy (strict, 63 файла) | без замечаний |
| pytest | 1027 тестов: разбор, эмиттер, генератор тестов, снапшоты фикстур, снапшот корпуса, RuSTy и iec_checker по всему `src/` и `tests/` (если инструмент установлен), интерпретатор ST `stsim` — те же наборы coUnit против сконвертированного кода и мутации логики |
| `s7conv build-corpus --check`, `gen-tests --check` | сгенерированное совпадает с конвертером побайтно |
| `st_lint --strict` | 242 файла, 0 замечаний |
| iec_checker 0.4 (`run_iec_checker.py --tests`) | `ParserError` 0, необоснованных находок 0; обоснования — в STATIC_ANALYSIS.md |
| RuSTy 1.0.6 `plc --check` (необязательно) | 51 файл, 0 ошибок (3 исключены с причинами) |

`stsim` и CODESYS дали одинаковый итог по всем 39 сценариям; окончательный результат — прогон в Control Win.

## Документация

- [methodology.md](docs/methodology.md) — этапы миграции, риски (время цикла, приоритеты OB, retain,
  аналоги, HMI, SCADA), чек-лист, оценка трудоёмкости, выбор способа тестирования
- [MAPPING.md](docs/MAPPING.md), [GRAMMAR.md](docs/GRAMMAR.md), [CONVERSION_REPORT.md](docs/CONVERSION_REPORT.md) —
  таблица соответствий, подмножество SCL, отчёт по корпусу
- [scenarios/README.md](scenarios/README.md) — формат сценариев и эталонные модели
- [ARCHITECTURE.md](docs/ARCHITECTURE.md), [LAYOUT.md](docs/LAYOUT.md) — устройство проекта и раскладка ST
- [TEST_REPORT.md](docs/TEST_REPORT.md), [STATIC_ANALYSIS.md](docs/STATIC_ANALYSIS.md) — результаты CODESYS и
  статанализа
- [MANUAL_STEPS.md](docs/MANUAL_STEPS.md) — что делает инженер в IDE: установка, проект для ПЛК210,
  обработчик OB82, Persistent Variables, привязка ввода-вывода
- [ASSUMPTIONS.md](docs/ASSUMPTIONS.md) — допущения и что из них подтверждено прогоном

## Ограничения и дальнейшие шаги

- **Проверено в CODESYS 3.5.17.30 и Control Win V3, а не на ПЛК210.** На ПЛК210 (свой таргет-файл и
  версия Standard) прогон нужно повторить; тест `StandardFTrigMatchesS7` покажет, совпадает ли там `F_TRIG`
  с S7.
- Разбирается только SCL: блоки LAD/FBD/STL сначала переводят в SCL в TIA Portal или вручную.
- Корпус написан по формату внешних источников TIA Portal и в TIA не компилировался; эталон поведения —
  описание логики блоков и модели, а не прогон на S7.
- Не создаются автоматически: задача или обработчик для OB82, объект Persistent Variables, привязка
  каналов ПЛК210 — пошагово в [MANUAL_STEPS.md](docs/MANUAL_STEPS.md), раздел 4. Слой ввода-вывода
  `GVL_IO` — заготовка с пересчитанными адресами.
- OB100 эмулируется флагом первого цикла, который команда Stop → Start CODESYS не сбрасывает (в S7 OB100
  выполняется при каждом STOP → RUN).
- Дальше: прогон на ПЛК210 со стендовой проверкой retain и ввода-вывода; импорт корпуса в TIA Portal
  (допущение S1).

## Summary (EN)

s7-to-codesys is a partial, honest converter from Siemens S7 SCL (TIA Portal external sources) to
CODESYS V3.5 Structured Text, plus a migration methodology. A hand-written recursive-descent parser
handles a 20-file SCL corpus (44 blocks, 998 constructs): 94 % convert automatically, 26 constructs
need review (`MIGRATION-CHECK`) and 30 are unsupported (`MIGRATION-TODO`: system functions, ANY/Variant,
AT overlays, GOTO, event OBs), each counted in a per-file report. Behaviour is verified with coUnit suites
generated from CSV scenarios whose expected values come from reference models of the block descriptions,
not from the converter output. Verified in CODESYS 3.5.17.30 with Control Win V3: the whole corpus
compiles with 0 errors and 0 warnings and all 74 coUnit tests pass; not yet run on target hardware.
Documentation is in Russian.

## Лицензия

[MIT](LICENSE) © 2026 kr0nsch

---

<p align="center"><b>Портфолио АСУ ТП</b></p>
<table>
<tr><td width="33%"><a href="https://github.com/kr0nsch/plc-repo-template">01 · plc-repo-template</a><br><sub>ST в git, сборка проекта скриптом, CI</sub></td><td width="33%"><a href="https://github.com/kr0nsch/plc-process-lib">02 · plc-process-lib</a><br><sub>ФБ: AI, двигатель, ПЧ, задвижка, ПИД, тревоги</sub></td><td width="33%"><span data-repo="kns-pump-station">03 · kns-pump-station</span> <sub>(готовится)</sub><br><sub>флагман: КНС, три насоса с ПЧ, модель, HMI</sub></td></tr>
<tr><td width="33%"><span data-repo="kns-port-domestic">04 · kns-port-domestic</span> <sub>(готовится)</sub><br><sub>перенос на Astra.IDE / MasterSCADA 4D</sub></td><td width="33%"><span data-repo="plc-iiot-stack">05 · plc-iiot-stack</span> <sub>(готовится)</sub><br><sub>OPC UA / MQTT → InfluxDB → Grafana</sub></td><td width="33%"><span data-repo="iolistgen">06 · iolistgen</span> <sub>(готовится)</sub><br><sub>перечень сигналов → ST, карты Modbus, SCADA</sub></td></tr>
<tr><td width="33%"><a href="https://github.com/kr0nsch/plc-ci-toolkit">07 · plc-ci-toolkit</a><br><sub>линтеры, сборка CODESYS, тесты, JUnit</sub></td><td width="33%"><a href="https://github.com/kr0nsch/s7-to-codesys"><b>08 · s7-to-codesys</b></a><br><sub>конвертер SCL → ST с отчётом о переносе</sub></td><td width="33%"><a href="https://github.com/kr0nsch/sis-interlock-demo">09 · sis-interlock-demo</a><br><sub>ПАЗ: MooN, матрица причин и следствий</sub></td></tr>
</table>
