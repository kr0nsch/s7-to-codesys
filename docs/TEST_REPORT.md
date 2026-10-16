# Отчёт о тестировании

Результаты юнит-тестов CfUnit (coUnit 1.2.0.0) в CODESYS Control Win V3 и проверок без CODESYS.
Запись «проверено в CODESYS» появляется только после реального прогона.

<!-- cds:test-report:begin (раздел обновляет `python tools/codesys/cds.py report`) -->
## Последний прогон в CODESYS

_Не запускалось._ Прогон: `python tools/codesys/cds.py test`, затем `python tools/codesys/cds.py report`
(раздел между маркерами перезаписывается).
<!-- cds:test-report:end -->

## Наборы тестов

13 наборов, 73 теста, 2019 проверок. Все наборы объявлены в `tests/POUs/PRG_Tests` (генерируется
`s7conv build-corpus` вместе с тестами сценариев; рукописные наборы находятся по `EXTENDS
coUnit.FB_TestSuite`).

| Набор | Папка | Тестов | Проверок | Что проверяет | Итог |
|---|---|---:|---:|---|---|
| `FB_F_NormX_Test` | `tests/POUs/S7Compat` | 8 | 8 | `F_NormX` по формуле Siemens NORM_X: середина, границы, вне диапазона, обратный и вырожденный диапазон | не запускалось |
| `FB_F_ScaleX_Test` | `tests/POUs/S7Compat` | 8 | 8 | `F_ScaleX` по формуле SCALE_X | не запускалось |
| `FB_S7Ton_Test` | `tests/POUs/S7Compat` | 7 | 48 | `FB_S7Ton`: отсчёт с фронта и с первого вызова, Q ровно на PT, насыщение ET, сброс, PT = 0, переход TIME через 2³² мс, Q при IN = TRUE дольше 2³² мс (`KeepsQWhileInHeldAcrossWrap`, добавлен ревью); `MatchesStandardInRealTime` — совпадение со Standard.TON в реальном времени (~700 мс) | не запускалось |
| `FB_S7Tof_Test` | `tests/POUs/S7Compat` | 4 | 28 | `FB_S7Tof`: отсчёт со спада, порог PT, возврат IN раньше PT, выход до первого TRUE; совпадение со Standard.TOF | не запускалось |
| `FB_S7Tp_Test` | `tests/POUs/S7Compat` | 3 | 24 | `FB_S7Tp`: импульс по фронту, порог PT, ET после импульса, фронты во время импульса; совпадение со Standard.TP | не запускалось |
| `FB_S7FTrig_Test` | `tests/POUs/S7Compat` | 2 | 6 | `FB_S7FTrig`: нет спада на первом вызове с CLK = FALSE, спад ровно на одном вызове | не запускалось |
| `FB_F_S7Now_Test` | `tests/POUs/S7Compat` | 2 | 2 | `F_S7Now`: моделируемые часы; в реальном времени идёт как ET Standard.TON (~300 мс) | не запускалось |
| `FB_AlarmDelay_ScenarioTest` | `tests/POUs/Scenarios` | 8 | 275 | `scenarios/FB_AlarmDelay.csv`: задержки появления и снятия, квитирование по фронту, состояния, вывод из работы | не запускалось |
| `FB_AnalogIn_ScenarioTest` | `tests/POUs/Scenarios` | 6 | 470 | `scenarios/FB_AnalogIn.csv`: NORM_X/SCALE_X, зоны перегрузки, неисправность канала, гистерезис уставок, имитация, слово состояния | не запускалось |
| `FB_Motor_ScenarioTest` | `tests/POUs/Scenarios` | 7 | 364 | `scenarios/FB_Motor.csv`: авто/ручной, контроль обратной связи (TON), коды аварий, сброс, счётчик пусков | не запускалось |
| `FB_PumpAlternation_ScenarioTest` | `tests/POUs/Scenarios` | 6 | 186 | `scenarios/FB_PumpAlternation.csv`: смена ведущего (R_TRIG, F_TRIG), подхват резервным, нехватка | не запускалось |
| `FB_Sequencer_ScenarioTest` | `tests/POUs/Scenarios` | 6 | 420 | `scenarios/FB_Sequencer.csv`: шаги CASE, переходы по времени (ET таймера) и уровням, аварии по времени, `STRING` | не запускалось |
| `FB_Totalizer_ScenarioTest` | `tests/POUs/Scenarios` | 6 | 180 | `scenarios/FB_Totalizer.csv`: интегрирование LREAL, отсечка, сброс, импульсы | не запускалось |

Наборы сценариев сгенерированы (`AUTO-GENERATED`): один тест на сценарий, проверка каждого выхода в
каждой строке, ожидаемые значения — из CSV (их считают эталонные модели по описанию логики блоков, не по
коду). Все таймерные строки, включая строки ровно на пороге (`boundary`), проверяются с моделируемым
временем `GVL_S7Clock` за один цикл — способ и его обоснование: [methodology.md](methodology.md), раздел 3.

## Предварительная проверка без CODESYS

`s7conv/tests/test_scenarios_simulated.py` исполняет те же наборы интерпретатором ST
(`s7conv/tests/stsim.py`) против закоммиченного `src/` — это модель CODESYS, не CODESYS
([methodology.md](methodology.md), раздел 3).

| Что | Итог (2026-10-16) |
|---|---|
| 6 наборов сценариев (39 тестов, 1895 проверок), F_TRIG с семантикой S7 | все проходят; каждая проверка выполняется один раз за три цикла (флаг `xDone`) |
| те же наборы, F_TRIG Standard по гипотезе «ложный спад на первом вызове» | падает только `FB_PumpAlternation_ScenarioTest.RotateOnStop`, первая проверка — `RotateOnStop#1 leadPump: Expected 1, Actual 2` |
| 7 рукописных наборов S7Compat, 100 циклов по 10 мс (тесты в реальном времени — с моделью Standard по МЭК) | все проходят и завершаются |
| мутации логики: `FB_Motor`, `FB_AlarmDelay` (счёт и квитирование уровнем), `FB_AnalogIn` (гистерезис), порог `FB_S7Ton` (`>=` → `>`) | каждая роняет тесты |
| `FB_S7Ton` 0.1.0 (разность «сейчас − старт») против нового теста `KeepsQWhileInHeldAcrossWrap` | тест падал (`after wrap Q: Expected True, Actual False`) — ошибка найдена ревью; `FB_S7Ton` 0.2.0 проходит |

## Что ожидать при первом прогоне

| Где | Что может разойтись | Как разбирать |
|---|---|---|
| `FB_PumpAlternation_ScenarioTest`, сценарий `RotateOnStop`, строка 1 (единственный, что начинается с `demand = 0`) | если `F_TRIG` CODESYS Standard даёт ложный спад на первом вызове с `CLK = FALSE`, ведущий насос сменится раньше времени (`leadPump` = 2 вместо 1) | это расхождение семантики платформы, а не ошибка теста (MAPPING.md, `fb.f_trig`): пересобрать корпус с `--f-trig s7compat` (`s7conv/corpus.py`, `corpus_options`) и повторить прогон; записать результат сюда и в ASSUMPTIONS.md (S4, K18) |
| `MatchesStandardInRealTime` (3 теста), `AdvancesLikeStandardTimer` | расхождение таймеров S7Compat и Standard в граничном случае (например, `ET` у `TP` в цикле окончания импульса) или джиттер больше допуска 5 мс | сообщение теста называет таймер; сравнить с семантикой в объявлении блока S7Compat (ASSUMPTIONS.md, K19) |
| любые наборы | тесты на несколько циклов и однократный запуск сценария рассчитаны на то, что раннер coUnit вызывает тесты каждый цикл до `TEST_FINISHED()` (ASSUMPTIONS.md, C10) | если поведение раннера другое — тест «застрянет» или завершится раньше |

## Упавшие тесты

_Нет данных._ Формат: набор, тест, сообщение CfUnit (Expected / Actual), причина, исправление.

## Проверки без CODESYS

| Проверка | Итог | Примечание |
|---|---|---|
| `ruff check`, `ruff format --check`, `mypy` | пройдено, 2026-10-16, локально | mypy strict: 62 файла |
| `pytest` | пройдено, 2026-10-16, локально | 803 теста (3 теста шаблона заменены проектными — STATIC_ANALYSIS.md), включая интеграционные с настоящими `plc` и iec_checker |
| `python -m s7conv build-corpus --check` | пройдено, 2026-10-16, локально | `src/*/Converted`, отчёт, задачи в `config.json`, тесты сценариев воспроизводятся побайтно |
| `tools/assemble.py --tests` | пройдено, 2026-10-16, локально | 54 объекта `src/` и `tests/` |
| `tools/check/st_lint.py --strict` | пройдено, 2026-10-16, локально | 240 файлов, 0 замечаний |
| iec_checker 0.4 (`tools_project/iec_checker_gate.py`) | пройдено, 2026-10-16, локально | необоснованных 0, известных пробелов разборщика 6, обоснованных 858 — [STATIC_ANALYSIS.md](STATIC_ANALYSIS.md) |
| RuSTy 1.0.6 (`run_rusty.py`) | пройдено, 2026-10-16, локально | 44 файла (10 исключены, причины — STATIC_ANALYSIS.md), 0 ошибок; весь `src/` и `tests/` с прокладками — в pytest |
