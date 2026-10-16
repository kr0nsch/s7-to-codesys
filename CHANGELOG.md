# Changelog

Все заметные изменения проекта записываются в этот файл.

Формат — [Keep a Changelog](https://keepachangelog.com/ru/1.1.0/), версии — по
[Semantic Versioning](https://semver.org/lang/ru/spec/v2.0.0.html).

## [Unreleased]

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
- `tools_project/iec_checker_gate.py`: статанализ через `run_iec_checker.py` шаблона, `ParserError`
  допускается только в описанных местах (`tools_project/iec_checker_parser_gaps.toml`).
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

### Changed

- `tools/check/st_lint.toml`: с `src/*/Converted/*` сняты правила STL004, STL006, STL007, STL008,
  STL011 (имена, числа и пометки исходного SCL сохраняются); форматные правила действуют.
- `tools/check/iec_checker_allow.toml` и `tools/check/rusty_exclude.txt` — под сгенерированный код и
  слой совместимости, с причинами.
- `pyproject.toml`: три теста шаблона, сравнивающие настройки с шаблоном, заменены проектными; ещё семь
  тестов `cds.py`, рассчитанных на пустой `library.libraries`, выполняются против config.json без ссылки на
  Standard (`tools_project/test_repo_config.py`).
- Пометка `fb.f_trig` называет проверенную версию (Standard 3.5.17.0) и тест для повторной проверки вместо
  «сверить с источником или тестом».
- Отчёт HTML: значения плиток итога выровнены по нижнему краю, счётчики в «Подробно по файлам» — по
  колонкам.
- Пометка `db.persistent` (`--retain persistent`) называет проверенное предупреждение CODESYS C0244 (в
  приложении нет объекта Persistent Variables) вместо «сверить с источником».
- README: границы автоматизации по категориям, результаты CODESYS, плейсхолдеры для картинок и GIF.

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
