# Changelog

Все заметные изменения проекта записываются в этот файл.

Формат — [Keep a Changelog](https://keepachangelog.com/ru/1.1.0/), версии — по
[Semantic Versioning](https://semver.org/lang/ru/spec/v2.0.0.html).

## [Unreleased]

### Added

- Таймеры и счётчики S5 из STL S7-300/400: SP, SE, SD, SS, SF, FR, R, `A/L/LC T n`; CU, CD, S, R, FR,
  `A/L/LC C n`. Слой S7Compat — структуры `ST_S5Timer`, `ST_S5Counter` и функции `F_S5*` с VAR_IN_OUT над
  элементами генерируемых `GVL_S5Timers.aTimer[n]` / `GVL_S5Counters.aCounter[n]` (в S7 таймер — глобальный
  объект CPU); время — `F_S7Now()`, остаток пересчитывается при обращении, `L T` — единицы шкалы (вверх),
  `LC T` — BCD со шкалой, `F_S5TimeWord` — S5T# с выбором шкалы. Пуск таймера — `MIGRATION-CHECK`
  `s5.timebase`. Наборы coUnit `FB_S5Timer_Test` (10 тестов) и `FB_S5Counter_Test` (5).
- Эталон S5 `s7conv/semantics/s5.py` в машине STL и `equiv`; сверка эталона с awlsim 0.77.1 (внешнее средство,
  GPL; в CI ставится отдельно, без него тест пропускается) на случайных последовательностях — совпадает.
- Корпус: `FB_ConveyorStl` — конвейер на STL с пятью видами таймеров S5, FR и счётчиком; сценарии
  `scenarios/lang/FB_ConveyorStl.csv` (7 сценариев, 58 вызовов) по описанию логики; генератор тестов
  обнуляет глобальные слова S5 в начале каждого сценария.
- `stsim`: VAR_IN_OUT функций по ссылке, присваивание структур копией, `SHL`/`SHR`.

### Changed

- Матрица токенов STL: SP, SE, SD, SS, SF — `check` (`s5.timebase`), FR, LC, CU, CD — `auto`.

## [1.1.0] - 2026-10-20

Все языки S7, кроме GRAPH: блоки LAD, FBD и STL из экспорта SimaticML переводятся в тот же ST CODESYS,
что и SCL, с трассой до сети и UId и сверкой с эталоном S7 (`s7conv equiv`). Цель — ОВЕН ПЛК210/СПК
(CODESYS V3.5 SP17 Patch 3) и REGUL (Astra.IDE 1.7.2.2). Проверено в CODESYS 3.5.17.30 с Control Win V3:
21 набор coUnit, 128 тестов, все пройдены; `src/` компилируется под REGUL R500 и ПЛК210 без ошибок и
предупреждений (компиляция, не запуск на ПЛК). Корпус SCL 1.0.0 (`src/*/Converted`, отчёт, снапшоты)
побайтно не изменился. Версия конвертера остаётся 0.1.0: она стоит в заголовке каждого сгенерированного
файла, и её подъём изменил бы корпус 1.0.0.

### Added

- Модели SR, RS, CTU, CTD и CTUD библиотеки Standard в интерпретаторе `stsim` (`builtin_flipflop`,
  `builtin_counter`; формулы и раздел справки — в docstring), независимые от таблиц `mapping.py`. Рукописный
  набор coUnit `FB_StandardCounter_Test` проверяет на той же платформе то, чего справка Standard не описывает:
  предел 65535, нижнюю границу CTD, приоритет RESET над LOAD и одновременные фронты CU и CD у CTUD.
- Источники блоков данных и типов данных PLC с расширениями `.db` и `.udt` читаются из каталога как SCL —
  выгрузку TIA Portal больше не нужно переименовывать.
- Вход SimaticML (экспорт TIA Portal Openness, `*.xml`): блоки FB, FC, OB, глобальные и экземплярные DB,
  типы данных PLC; сети LAD, FBD, STL и SCL переводятся в тот же ST, что и SCL 1.0.0 (`s7conv/frontends`,
  `s7conv/ir`, `s7conv/lower`). Разбор — `xml.etree` стандартной библиотеки, документы с DOCTYPE и сущностями
  отклоняются, непонятный XML даёт пометку, а не падение.
- LAD/FBD → ST: поток питания (последовательно — AND, ветви — OR), общий участок — во временной
  `xNet<N>_<k>`; SR/RS с битом-операндом в порядке S7, фронты P/N с явным битом памяти, сравнения, MOVE,
  арифметика с ENO через функции S7Compat `F_S7Eno<Оп><Тип>`, таймеры и счётчики с экземпляром, вызовы FB/FC
  с цепочкой EN → ENO, прыжок вперёд через сети → `IF`. Словарь элементов с происхождением каждой строки —
  `PARTS` в `lower/net_to_ast.py`; элемент, форма XML которого не подтверждена открытым экспортом, получает
  пометку `vocab_unverified`.
- STL → ST, символьный подъём (режим A): логика с «AND перед OR» и скобками, `=`/`S`/`R`, `FP`/`FN`, `L`/`T`
  с правилами типов (дополнение нулями — `stl.zero_extend`), арифметика и сравнения INT/DINT/REAL, `CALL`
  инструкций и блоков. Переходы `JC`/`JCN`/`JU` восстанавливаются в `IF`/`ELSE` без `JMP`; несводимый поток
  и ключ `--stl-jumps pc` — автомат `CASE` в `WHILE`. Матрица 172 токенов XSD V21 — `lower/stl_tokens.py`.
- Ключи `--cpu s7-300|s7-1500`, `--stl-jumps structured|pc`, `--global-suffix`. Пометки в ST и отчёте
  ссылаются на файл, сеть и UId (`(FB_StarterLad.xml, сеть 1, UId 32)`).
- Корпус всех языков `samples/lang/`: XML строит `build_xml.py` из описания блоков `blocks.py`
  (детерминированные UId, `--check`); `FB_Starter` на LAD, FBD, STL и SCL, `FB_PumpInterlockLad`,
  `FC_ClampPctLad`, `DB_Process` (стандартный доступ, смещения), `UDT_Valve`.
- S7Compat: `F_S7EnoAddInt` … `F_S7EnoMulDint` — ENO арифметики S7 (EN AND NOT переполнение) и набор
  `FB_F_S7Eno_Test`.
- `build-corpus` собирает и корпус всех языков: ST — в `src/{DUTs,GVLs,POUs}/Lang/Converted/` (папка
  проекта `Lang/Converted`, генерируемые GVL с суффиксом `_Lang`; корпус SCL 1.0.0 в `src/*/Converted/` не
  меняется), отчёт `docs/CONVERSION_REPORT_LANG.md` с разделом «По языкам» (элементы и сети LAD/FBD,
  инструкции STL), тесты сценариев — `tests/POUs/ScenariosLang/` (в `PRG_Tests` — после рукописных наборов).
  Сборка проверяет, что имена объектов и членов GVL двух корпусов не совпадают (CODESYS — плоское
  пространство имён, RuSTy — E004). Тест 1.0.0 `test_write_into_fresh_copy_then_check_is_clean` копирует в
  свой мини-репозиторий и корпус `samples/lang`: без него `PRG_Tests` копии не совпал бы с репозиторием.
- Сценарии `scenarios/lang/`: `FB_Starter.csv` (9 сценариев, 47 вызовов) проверяет все четыре перевода
  пускателя через `aliases.json`, `FB_PumpInterlockLad.csv` (5 сценариев, 25 вызовов); модели —
  `scenarios/lang/reference/`, контрольные точки посчитаны вручную. Мутация «S7 SR → одноимённый SR CODESYS»
  роняет сценарий `StartAndStopTogether`.
- Эталон поведения S7 `s7conv/semantics/` — независимо от понижения и эмиттера (тест запрещает импорт
  `lower`, `emitter`, `plcopen`, `mapping`): `net_eval` — поток питания LAD/FBD (SR/RS с операндом, фронты,
  ENO = EN AND NOT переполнение, прыжки, вызовы FC), `stl_machine` — машина STL S7-300 (/FC, OR-бит «AND перед
  OR», стек скобок до 7 уровней, 2 ACCU с дополнением нулями при `L`, OV/OS, переходы, CALL таймеров IEC).
- `s7conv equiv <вход> [--scenarios DIR] [--random N --seed S]`: эталон против интерпретатора ST на одних
  входах по вызовам, сравниваются все выходы и статика; семейство блоков из `aliases.json` сверяется с одним
  эталоном (перевод SCL — с эталоном LAD). Первое расхождение — с трассой до сети и UId или строки STL, код 1.
  На корпусе: сценарии и 500 случайных вызовов на блок, переходы STL `structured` и `pc` — расхождений нет.
- `s7conv ir <файл> --format json` — NetIR и StlIR с трассой до сети, UId и строки.
- `samples/lang/EXTERNAL.json`: XSD SimaticML V21 (dotnetprojects/DotNetSiemensPLCToolBoxLibrary @ bbe5bec, SHA-256
  каждого файла) и открытые экспорты TIA — lad-cookbook (MIT, LAD V21) и Smart_Factory (Apache-2.0, STL V18).
  Тесты скачивают их в `.cache/` (в git не кладутся): фрагменты корпуса (`Sections`, `FlgNet`, `StatementList`,
  `StructuredText`) валидны по XSD V21; образцы конвертируются без `RawBlock` и без `MIGRATION-TODO`. Порча
  XML (удалённый провод или операнд, повтор UId, неизвестный элемент, обрезанный файл) не роняет разбор.
- Генерируемые справочники `docs/MAPPING_LADFBD.md` (словарь элементов с уровнем подтверждения и источником
  строки) и `docs/MAPPING_STL.md` (172 из 172 токенов XSD V21 с классом, правилом и тестами); матрица
  «правило → тест» `samples/rules_matrix.py` падает, если у правила выпуска нет теста.
- CI: шаг «корпус всех языков» — `check samples/lang`, `build_xml.py --check`, `generate_lang_csv.py --check`,
  `equiv` со сценариями и 500 случайными вызовами (и в режиме переходов `pc`); `lxml` — в
  `requirements-dev.txt` для проверки XSD.
- Тесты эквивалентности: случайные цепочки STL со скобками до 7 уровней и случайные сети LAD (hypothesis) —
  эталон против понижения; мутации «старое SR→SR», «ENO = EN» и «знаковое расширение вместо дополнения
  нулями» ловятся.

- GRAPH в 1.1.0 не переводится: сеть GRAPH закомментирована с `MIGRATION-TODO` (`xml.unit_unsupported`) и
  ссылкой на файл и сеть (тест `test_graph_network_is_todo_with_network_reference`).
- Документация всех языков: `docs/STRATEGIES.md` (почему ST, а не LD/FBD/IL; режимы переходов STL),
  `docs/EQUIVALENCE.md` (оракулы, мутации, чего проверка не доказывает), `docs/SIMATICML_VERSIONS.md`
  (матрица «версия TIA × язык» и чем подтверждено), `docs/SOURCES.md`, допущения L1–L12 в
  `docs/ASSUMPTIONS.md`, раздел «Все языки» в `docs/ARCHITECTURE.md`; `docs/USAGE.md` — экспорт SimaticML,
  ключи `--stl-jumps`, `--cpu`, `--global-suffix`, сценарии и `equiv` для своих блоков, копия репозитория со
  своими XML; `docs/MANUAL_STEPS.md` — компиляция под REGUL R500 и ПЛК210 и ручные шаги по LAD/FBD/STL.
- Медиа README: баннер всех языков, GIF реальной сессии `check` → `convert` → `equiv` → `cds.py test`, снимки
  трассы STL → ST и раздела «По языкам», график покрытия языков; обёртка `tools_project/make_media.py` над
  медиа-китом портфолио (`MEDIA_KIT`), снятая сессия терминала — `tools_project/media/`.
- `docs/USAGE.md` — перенос своей программы S7 по шагам: выгрузка из TIA Portal и форматы входных файлов
  (таблица тегов, `ob_config.json`), `check`, `report`, `convert` и его ключи, разбор пометок
  `MIGRATION-CHECK`/`MIGRATION-TODO`, свои сценарии и `gen-tests`, сборка в CODESYS через копию репозитория
  с `build-corpus`, частые ошибки. Выводы команд — с учебного набора из четырёх файлов демокорпуса;
  пример сценария `FB_Debounce` проверен генератором и интерпретатором ST.

### Changed

- `build-corpus`: корпус всех языков собирается, только если в `samples/lang` есть `*.xml`, а наборы
  сценариев — только если в `scenarios/lang` есть `*.csv`. Копия репозитория со своими блоками SimaticML и без
  сценариев собирается (проверено: `build-corpus` и `cds.py check --tests` — 64 объекта, 0 ошибок).
- README: конвертер всех языков S7 — первый экран, демо, быстрый старт с корпусом `samples/lang`, путь своих
  XML, границы автоматизации по языкам, тесты 1.1.0 (Control Win, R500, ПЛК210), Summary (EN).
- Интерпретатор ST `stsim` переехал из `s7conv/tests/stsim.py` в пакет `s7conv/sim/stsim.py`: им пользуются
  `equiv` и тесты нового корпуса. Старый путь остаётся реэкспортом — соседние проекты, закреплённые на 1.0.0,
  импортируют его без изменений.
- README перестроен для читателя без контекста: что это, зачем и для кого — на первом экране; быстрый
  старт с ожидаемым выводом каждой команды, отдельно без CODESYS и с CODESYS; раздел «Как использовать в
  своём проекте»; таблицы «каталог → назначение» и «вопрос → документ»; бейджи выпуска и Python 3.11+.
  Команды записаны одной строкой, без продолжения строки `\`, которое не работает в cmd и PowerShell.
- `docs/MANUAL_STEPS.md`: шаги сопровождения репозитория (зеркало, превью для ссылок) перенесены в
  `CONTRIBUTING.md`; ссылки на допущения пояснены словами. `CONTRIBUTING.md`: порядок разделов README.
- `pyproject.toml`: пакет называется `s7-to-codesys` (было имя пакета инструментов шаблона), версия пакета —
  версия конвертера 0.1.0.
- Статанализ: необязательное задание CI с образом iec_checker `nightly` — находки образа разобраны и обоснованы
  (было 7: все PLCOPEN-CP17 «неиспользуемый параметр» — новое правило образа; сохранённый интерфейс блоков S7).
  Дефектов в коде нет, ST не менялся; разбор — `docs/STATIC_ANALYSIS.md`. С новым файлом обоснований подтверждено
  прогоном CI 39254560322: 0 необоснованных, 925 обоснованных.
- `run_iec_checker.py`: ключ `checker` (`v0.4` или `nightly`) в файле обоснований — запись применяется и
  проверяется на использование только для своей версии разборщика; `--checker`, по умолчанию `nightly` с
  `--docker`, иначе `v0.4`. Записи, которые образ nightly не использует, помечены `checker = "v0.4"`.

### Fixed

- **Меняет вывод.** Экземпляры SR и RS в SCL переводились одноимёнными блоками CODESYS, а приоритет у них
  противоположный: S7 SR — сброс главнее, CODESYS SR — установка главнее. При `S = R = 1` перевод давал
  обратный результат. Теперь S7 `SR(S, R1)` → CODESYS `RS(SET := S, RESET1 := R1)`, S7 `RS(R, S1)` → CODESYS
  `SR(SET1 := S1, RESET := R)`; строка `docs/MAPPING.md` исправлена. SR/RS, сконвертированные 1.0.0,
  нужно перегенерировать и проверить. В демокорпусе 1.0.0 SR/RS нет — его результат не изменился. Проверка:
  тест конвертера, модели SR/RS в `stsim` при `S = R = 1` и набор `FB_StandardFlipFlop_Test` в Control Win.
- CI: сводка заданий iec_checker (обязательного и nightly) — без раздела обоснованных находок: он может
  превысить предел сводки шага GitHub (1024k), и тогда GitHub отбрасывает сводку целиком. В сводке —
  таблица статусов, необоснованные находки и неиспользованные обоснования; полный список — в
  `iec_checker.md` артефакта задания.
- README, шаг 7 «Как использовать в своём проекте», и `docs/USAGE.md`, шаг 8: копия репозитория для сборки
  своего проекта создаётся рядом с первым клоном (`cd ..` перед `git clone`). Из корня клона копия
  оказывалась внутри него, пути `..\s7-to-codesys\my_plc\…` не находились, и `build-corpus` оставался без
  входа. В README к шагу 7 добавлен `cds.py check --tests`: без OB во входе у `build` нет задач, и весь код
  компилирует только эта команда. Порядок проверен в cmd на чистом клоне до `build-corpus` включительно.
- `docs/TEST_REPORT.md`: записан повторный прогон перед выпуском (2026-10-19: `check --tests` — 54 объекта,
  0 ошибок и 0 предупреждений; `test --clean` — 74 из 74), на который ссылается README; счётчик pytest —
  1030. README: бейдж тестов без слова coUnit на первом экране, ожидаемый вывод `cds.py runtime init`.

## [1.0.0] - 2026-10-19

Первый выпуск: конвертер `s7conv` 0.1.0 (эта версия стоит в `s7conv --version` и в заголовках
сгенерированных файлов), корпус SCL со сконвертированным результатом, слой S7Compat, тесты сценариев и
методика миграции. Проверено в CODESYS 3.5.17.30 с Control Win V3; на ПЛК210 не запускалось.

### Added

- Раскладка исходников ST в `src/` и `tests/` и её формальный контракт `docs/LAYOUT.md` (из шаблона).
- Инструменты шаблона: `tools/assemble.py`, `tools/check/` (линтер `st_lint.py`, запуск iec_checker и
  RuSTy), `tools/codesys/cds.py` (импорт, сборка, тесты coUnit в Control Win, экспорт).
- CI GitHub Actions: ruff, mypy, pytest, сборка ST, линтер (`--strict`), iec_checker v0.4 (закреплён
  по размеру и SHA-256); необязательно — iec_checker `nightly` (образ закреплён по дайджесту) и RuSTy.
- Корпус SCL `samples/scl/`: 20 исходников в стиле внешних источников TIA Portal (44 блока: UDT, DB,
  FB, FC, OB1/OB30/OB100/OB82) с описанием логики в заголовке каждого файла, таблица тегов
  `PlcTags.csv`, свойства блоков `BlockProperties.csv`, `ob_config.json`, каталог и матрица покрытия
  (`samples/coverage_matrix.py`).
- Конвертер `s7conv/` SCL (TIA Portal) → ST CODESYS: лексер и разборщик рекурсивным спуском с
  восстановлением после ошибок и переносом комментариев; эмиттер в раскладку (DUT, GVL с
  RETAIN/PERSISTENT, экземплярные DB в `GVL_InstanceDBs`, POU с шапкой, слой ввода-вывода
  `GVL_IO`/`GVL_Markers` с `AT`, `GVL_Tags`); OB → задачи, OB100 — флаг первого цикла; пометки
  `MIGRATION-CHECK`/`MIGRATION-TODO`; отчёт Markdown и HTML; CLI `s7conv convert|report|check`.
- Сценарии поведения `scenarios/*.csv` для шести блоков (39 сценариев, 263 вызова) и эталонные модели
  `scenarios/reference/` с проверкой формата, запаса времени и ручными контрольными точками.
- `s7conv build-corpus [--check]`: корпус → `src/{DUTs,GVLs,POUs}/Converted/` (папка проекта
  `Converted`), `docs/CONVERSION_REPORT.md`, задачи из OB в `tools/codesys/config.json`
  (`modes.normal.tasks`), тесты сценариев и `PRG_Tests`; `--check` сверяет репозиторий побайтно.
- `s7conv gen-tests СЦЕНАРИИ --out tests [--check]`: наборы coUnit `FB_<Блок>_ScenarioTest` по сценариям
  CSV — один тест на сценарий, проверка каждого выхода в каждой строке (ожидаемые значения — из CSV),
  моделируемое время для таймеров, имена ST по таблицам конвертера, проверка направления и типа
  столбцов; `PRG_Tests` с рукописными и сгенерированными наборами.
- Слой совместимости S7Compat (`src/*/S7Compat`, рукописный): `F_NormX`, `F_ScaleX` (перенесены из
  `src/POUs`), таймеры `FB_S7Ton`, `FB_S7Tof`, `FB_S7Tp` с источником времени `F_S7Now` /
  `GVL_S7Clock`, детектор спада `FB_S7FTrig` с семантикой S7; параметры конвертера `--timers s7compat`,
  `--f-trig s7compat`.
- Тесты coUnit S7Compat: `FB_S7Ton_Test`, `FB_S7Tof_Test`, `FB_S7Tp_Test` (пороги, фронты, сброс,
  переход TIME через 2³² мс, сверка со Standard в реальном времени на несколько циклов),
  `FB_S7FTrig_Test`, `FB_F_S7Now_Test`; `FB_F_NormX_Test`, `FB_F_ScaleX_Test` перенесены в
  `tests/POUs/S7Compat`.
- Сценарий `FB_AlarmDelay/AckHeldDuringActivation` (квитирование по фронту, кнопка удерживается во время
  появления): закрывает пробел, найденный мутационной проверкой.
- Интерпретатор ST для тестов (`s7conv/tests/stsim.py`) и `test_scenarios_simulated.py`: сгенерированные и
  рукописные наборы coUnit исполняются против закоммиченного кода без CODESYS, с проверкой гипотезы о
  F_TRIG и мутациями логики.
- pytest: снапшот корпуса (`build-corpus` воспроизводит закоммиченное), генератор тестов (формат CSV,
  сверка с эталонным читателем, имена, текст ST, ожидаемые значения из CSV), RuSTy по всему `src/` и
  `tests/`, проверки настроек репозитория (`tools_project/test_repo_config.py`).
- Документы: `docs/methodology.md` (этапы миграции, риски, чек-лист, оценка трудоёмкости, выбор способа
  тестирования), переработаны README, ARCHITECTURE, MAPPING, STATIC_ANALYSIS, TEST_REPORT,
  MANUAL_STEPS, ASSUMPTIONS.
- Сборка и прогон в CODESYS 3.5.17.30 с Control Win V3 (`cds.py build`, `library`, `build --tests`, `test`,
  `roundtrip`): весь корпус — 0 ошибок и 0 предупреждений, 13 наборов coUnit, 74 теста — все пройдены,
  roundtrip без диффа; разбор результатов и сравнение с интерпретатором ST — `docs/TEST_REPORT.md`.
- Тест `FB_S7FTrig_Test.StandardFTrigMatchesS7`: характеризация `F_TRIG` библиотеки Standard (на первом
  вызове с CLK = FALSE спада нет — как в S7); stsim-тест, что он различает гипотезы о начальном состоянии.
- Генератор тестов отказывается выпускать набор больше 900 проверок или 100 тестов: лимиты coUnit 1.2.0.0
  (1000 и 100 на набор) библиотека не проверяет.
- Повторная проверка с чистого `build/` в CODESYS 3.5.17.30 и контрольные зонды: ошибка в OB82 без задачи
  видна только проверке пула (`cds.py library`), искажённые ожидания (в том числе в строке на пороге
  таймера) ловятся ровно теми тестами, `#Standard` разрешается в Standard 3.5.17.0 (`docs/TEST_REPORT.md`).
- `docs/MANUAL_STEPS.md`, раздел 4: пошаговые действия в IDE — проект для ПЛК210, обработчик OB82,
  Persistent Variables, привязка ввода-вывода к каналам ПЛК210.
- Оформление README: баннер для тёмной и светлой темы, бейджи, навигация, подвал портфолио; раздел
  «Демонстрация» с реальными медиа в `docs/media/` — GIF прогона (`s7conv convert`, `build-corpus --check`,
  `cds.py test --clean`: 74 из 74 в Control Win, 19.10.2026), FB_Motor «SCL рядом с ST», примеры пометок
  `MIGRATION-CHECK`/`MIGRATION-TODO`, верх HTML-отчёта конвертации; `social-preview.png` (загрузка —
  `docs/MANUAL_STEPS.md`, раздел 8).
- Подготовка к публикации: автор — `kr0nsch` (LICENSE, README, заголовки рукописных POU и тестов S7Compat,
  Project Information библиотеки в `tools/codesys/config.json`, фикстуры и эталоны тестов шаблона); подвал
  README ссылается только на опубликованные репозитории портфолио, бейдж CI — встроенный бейдж GitHub
  Actions. Повторный прогон 19.10.2026: `cds.py check --tests` — 54 объекта, 0 ошибок и 0 предупреждений;
  `cds.py test --clean` — 74 из 74 (`docs/TEST_REPORT.md`).

### Changed

- `tools/check/st_lint.toml`: с `src/*/Converted/*` сняты правила STL004, STL006, STL007, STL008,
  STL011 (имена, числа и пометки исходного SCL сохраняются); форматные правила действуют.
- `tools/check/iec_checker_allow.toml` и `tools/check/rusty_exclude.txt` — под сгенерированный код и
  слой совместимости, с причинами.
- Инструменты синхронизированы с шаблоном: понижение `iec-checker` для `TIME()`, `a[i].b`, пустого оператора
  `;` и массива с начальным значением в структуре, прокладка RuSTy `rusty_shims/codesys_conversions.st`
  (`TIME_TO_DINT` и другие преобразования TIME), проверка ключей `st_lint.toml`, составные префиксы массивов
  в STL007.
- Статанализ — `python tools/check/run_iec_checker.py --tests` шаблона, без обёртки проекта: `ParserError` 0
  (раньше шесть мест допускала обёртка `tools_project/iec_checker_gate.py`, она удалена вместе со списком
  мест). В блоках, которые раньше не разбирались (`FB_EventLogger`, `FB_Ramp`, `FB_Valve`, `PRG_Main`), —
  98 новых находок, все обоснованы (всего 962, было 864); среди них `EXIT` в `FB_EventLogger`
  (PLCOPEN-L10) — перенесён из SCL как есть.
- `tools/check/rusty_exclude.txt`: исключены 3 файла вместо 10, `run_rusty.py` проверяет 51 файл из 54 (было
  44); тесты `s7conv/tests/test_rusty_check.py` больше не добавляют своё объявление `TIME_TO_DINT`.
- `pyproject.toml`: тесты шаблона выполняются полностью, без `--deselect`; отличия настроек проекта от
  шаблона проверяет `tools_project/test_repo_config.py`.
- Пометка `fb.f_trig` называет проверенную версию (Standard 3.5.17.0) и тест для повторной проверки вместо
  «сверить с источником или тестом».
- Отчёт HTML: значения плиток итога выровнены по нижнему краю, счётчики в «Подробно по файлам» — по
  колонкам.
- Пометка `db.persistent` (`--retain persistent`) называет проверенное предупреждение CODESYS C0244 (в
  приложении нет объекта Persistent Variables) вместо «сверить с источником».
- README: границы автоматизации по категориям, результаты CODESYS.

### Fixed

- s7conv: стартовая информация событийных OB (`IO_State`, `Channel`, … у OB82) объявлялась `VAR`, а в `VAR`
  программы извне записать нельзя (CODESYS 3.5.17.30: C0037) — передать её из обработчика события можно
  было только правкой сгенерированного кода. Теперь у событийных OB она остаётся `VAR_INPUT`; у циклических
  OB и OB100 — `VAR`, как раньше.
- Ссылки на правила оформления в `.editorconfig` и `.gitattributes` указывают на `CONTRIBUTING.md`.
- `tools/codesys/config.json`: не было ссылки на библиотеку Standard — первая сборка в CODESYS дала 89 ошибок
  (`Неизвестный тип: 'R_TRIG'`, `'TON'`, `'CTU'`, `CONCAT`); добавлен плейсхолдер `Standard` в
  `library.libraries`.
- s7conv: начальные значения `BEGIN` для элементов массива в поле UDT сохраняют остальные элементы из
  объявления типа (`DB_RecipeActive.doseStep` — `[0.8, 1.2, 1.5, 2.0]`, было `[0.8, 1.2, 2(0.0)]`).
- s7conv: `CTU_INT.PV`/`CV` (INT в S7, WORD в CODESYS) — явные `INT_TO_WORD`/`WORD_TO_INT` вместо
  неявного преобразования со сменой знака.
- s7conv: пустой оператор `;` переносится как есть вместе с комментарием в строке.
- s7conv: названия правил `decl.dropped_use`, `call.param_dropped` в отчёте.
- `FB_S7Ton` 0.2.0: при IN = TRUE дольше 2³² мс (≈ 49,7 суток) Q падал на время PT — прошедшее время
  считалось разностью «сейчас − старт», которая после перехода TIME через ноль становится малой. Теперь
  оно копится по приращениям между вызовами с насыщением; тест `FB_S7Ton_Test.KeepsQWhileInHeldAcrossWrap`.
- s7conv: конструкции, смысл которых в S7 и CODESYS расходится, больше не переносятся молча — пометки
  `expr.time_sub` (вычитание TIME/TOD/DT и унарный минус TIME: в CODESYS без знака), `expr.div_int`
  (целое деление и MOD на не-константу: делитель 0 в CODESYS — исключение), TODO `expr.string_index`
  (символ строки по индексу: CHAR с 1 в S7, BYTE в CODESYS).
- s7conv: `SCALE_X` с целым OUT получает `REAL_TO_<тип>` и пометку и в параметре вызова, и в
  типизированном варианте `SCALE_X_<тип>` (раньше — только в присваивании `SCALE_X`).
- s7conv: `ROUND` от LReal → `LREAL_TO_DINT` (было `REAL_TO_DINT`: сужение до REAL до округления).
- s7conv: `SQR(x)` → `x * x` для операнда без вызовов (точно); `EXPT(x, 2.0)` — только для операнда с
  вызовом и с пометкой `func.sqr` (поведение EXPT при отрицательном основании не проверено).
- s7conv: пометки `ob.startup`/`ob.initial_call` и MAPPING.md говорили, что флаг первого цикла сбрасывается
  «при каждом запуске, как OB100 при переходе в RUN»; в CODESYS Stop → Start флаг не сбрасывает — текст
  исправлен, расхождение — в методике и чек-листе.
- s7conv: стандартный (неоптимизированный) экземплярный или типизированный DB без `NON_RETAIN` молча
  становился нереманентным, хотя по тому же правилу для глобальных DB в S7 он реманентен целиком; теперь —
  секция `VAR_GLOBAL RETAIN` в `GVL_InstanceDBs` и пометка `db.retain_standard` (в корпусе — `DB_LegacyTlg`).
- Отчёт конвертации называет режимы семантики (таймеры, F_TRIG) и рукописные объекты S7Compat, через
  которые переведены «автоматические» конструкции. MAPPING.md: раздел «Расхождения, которые конвертер не
  помечает» (разрядность промежуточных результатов, индекс вне границ, деление REAL на 0, FOR,
  неявные преобразования); заметка о LIMIT при MN > MX.

### Removed

- Пример шаблона: `E_DeviceMode`, `ST_ExampleCmd`, `ST_ExampleSts`, `GVL_Const`, `I_Resettable`,
  `F_Clamp`, `FB_Example`, `PRG_Main`, наборы `FB_F_Clamp_Test`, `FB_Example_Test`.
- Снапшот корпуса с настройками по умолчанию в `s7conv/tests/snapshots/corpus` — его заменил
  закоммиченный результат `build-corpus`.
