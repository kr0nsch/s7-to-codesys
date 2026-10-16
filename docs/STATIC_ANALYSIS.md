# Статический анализ

Компилятор CODESYS, линтер `st_lint`, статанализ `iec_checker` и проверка компиляции RuSTy для `src/` и
`tests/`: как они запускаются в этом проекте, что в них настроено иначе, чем в шаблоне, и почему; обоснования находок,
которые не исправлены в коде. Исправленные находки сюда не пишутся.

В `src/` две части с разными правилами:

- **`src/*/Converted/`** — код, который генерирует `s7conv build-corpus` из корпуса `samples/scl`. Он
  сохраняет имена, числа, структуру ветвлений и пометки исходного SCL (принцип переноса один к одному —
  [methodology.md](methodology.md)). Руками не правится: правка — в конвертере или корпусе.
- **`src/*/S7Compat/`** и **`tests/`** — рукописный код (слой совместимости и его тесты) и
  сгенерированные тесты сценариев; проверяются полностью, как в шаблоне.

## Как запускается

| Инструмент | Где | Вход | Отчёт |
|---|---|---|---|
| `python tools/codesys/cds.py build`, `build --tests`, `library` | локально (Windows, CODESYS 3.5.17.30) | рабочий проект, тестовый проект, все объекты `src/` («Проверить все объекты пула») | `build/build.log`, `build/build.json`, `build/library.log` |
| `python tools/codesys/cds.py check --tests` | локально (Windows, CODESYS 3.5.17.30) | все объекты `src/` и `tests/` в пуле проекта без устройства, в том числе без задачи | `build/check.log`, `build/check.json` |
| `python tools/check/st_lint.py --strict` | локально и в CI | `src/`, `tests/` | консоль; код выхода ≠ 0 при нарушениях |
| `python tools/check/run_iec_checker.py --tests` | локально и в CI (обязательно): iec_checker v0.4 | `build/assembled/iec-checker/` (вариант сборки `iec-checker`, `src/` и `tests/`) | `build/iec_checker.json`, `build/iec_checker.md` |
| то же с `--docker <образ nightly>` | CI, необязательное задание | то же | артефакт `iec-checker-nightly-reports` |
| `python tools/check/run_rusty.py` | локально и в CI (необязательное задание): RuSTy 1.0.6 `plc --check` | `build/assembled/rusty/` без файлов из `tools/check/rusty_exclude.txt` | `build/rusty.log`, `build/rusty.json` |
| `pytest s7conv/tests/test_rusty_check.py` | локально и в CI (pytest) | весь `src/` и `tests/`, у `GVL_Markers` сняты `AT` | результат теста |

iec_checker запускается тем же `run_iec_checker.py` шаблона, что и в других репозиториях, без обёртки
проекта: понижение `iec-checker` шаблона ([tools/README.md](../tools/README.md), «Понижение для
iec_checker») разбирает весь `src/` и `tests/` без `ParserError`. До 2026-10-16 шесть мест в коде
CODESYS (`TIME()`, `a[i].b`, пустой оператор `;`, массив с начальным значением в структуре) iec_checker 0.4
не разбирал, и проект проверялся обёрткой, которая принимала `ParserError` только в этих местах; теперь
их понижает шаблон (раздел «Конструкции, которые раньше не разбирались»), обёртка удалена.

## Последний прогон

| Дата | Инструмент | Вход | Итог |
|---|---|---|---|
| 2026-10-16 | CODESYS 3.5.17.30: `cds.py build` | рабочий проект (40 объектов `src/`, задачи из OB) | 0 ошибок, 0 предупреждений |
| 2026-10-16 | CODESYS 3.5.17.30: `cds.py library` (проверка пула) | 39 объектов `src/` (без `PRG_Main`) | 0 ошибок, 0 предупреждений |
| 2026-10-16 | CODESYS 3.5.17.30: `cds.py build --tests` | `src/` и `tests/`, coUnit 1.2.0.0 | 0 ошибок, 0 предупреждений |
| 2026-10-16 | CODESYS 3.5.17.30: `cds.py check --tests` | 54 объекта `src/` и `tests/` (пул без устройства) | 0 ошибок, 0 предупреждений |
| 2026-10-16 | `st_lint --strict` | `src/`, `tests/` (242 файла) | 0 ошибок, 0 предупреждений |
| 2026-10-16 | `run_iec_checker.py --tests` (iec_checker 0.4, Windows, локально) | 54 объекта `src/` и `tests/` | `ParserError` 0; необоснованных 0; обоснованных 962; артефактов сборки 163; неиспользованных обоснований нет |
| 2026-10-16 | `run_rusty.py` (RuSTy 1.0.6, Windows, локально) | 51 файл (3 исключены) | 0 ошибок, 1 предупреждение (E067 — см. «RuSTy») |
| 2026-10-16 | `test_repository_sources_pass_rusty_with_shims` | 53 файла из 54 (без `DB_Telegram`) | пройден |
| — | iec_checker 0.4 (CI, Linux) | то же | _перенести из отчёта CI_ |
| — | iec_checker `nightly` (CI, необязательно) | то же | _перенести из отчёта CI_ |

## Компилятор CODESYS

**Итог.** Сборка рабочего проекта, проверка всех объектов пула и сборка тестового проекта — 0 ошибок и
0 предупреждений (TEST_REPORT.md, «Сборка и прогон в CODESYS»). Обосновывать нечего; ошибок и
предупреждений в сконвертированном коде сборка не нашла. Зонд при повторной проверке показал другое:
в `VAR` программы извне записать нельзя (C0037), поэтому стартовая информация событийных OB теперь
остаётся `VAR_INPUT` (MAPPING.md, «Секции переменных»).

**Почему проверка пула.** `cds.py build` компилирует только объекты, достижимые из задач: в зонде
программа без задачи с ошибкой `iX := diZ;` (C0032) дала в `build` «0 ошибок» (так же записано в
допущении D34 шаблона). А у `PRG_Diagnostic_error_interrupt` (OB82) задачи нет. `cds.py library`
выполняет «Проверить все объекты пула» по всем объектам `src/`, кроме `PRG_Main` (он исключён из
библиотеки в `config.json` и компилируется `build`), — вместе они покрывают весь корпус. При повторной
проверке ошибка, внесённая в копии в `PRG_Diagnostic_error_interrupt`, в `build` не появилась, а `library`
показала её с файлом и строкой (TEST_REPORT.md, «Повторная проверка с чистого `build/`»).

**Что значат «0 предупреждений»** — зонд 2026-10-16 (отдельный проект во временном каталоге, те же
`tools/codesys` и настройки):

| Конструкция | Сообщение CODESYS 3.5.17.30 |
|---|---|
| `wY := iX;` (INT → WORD, неявно) | предупреждение **C0195** «Неявная конверсия типа со знаком 'INT' в тип без знака 'WORD': возможно изменение знака» |
| `iX := diZ;` (DINT → INT, неявно) | ошибка **C0032** «Невозможно конвертировать тип 'DINT' в тип 'INT'» |
| `iX := rR;` (REAL → INT, неявно) | ошибка **C0032** |
| неиспользуемая переменная `iUnused` | сообщения нет: проверка неиспользуемых переменных — правило статического анализа (Static Analysis), в обычной сборке её нет |

C0195, C0032 для DINT → INT и отсутствие сообщения о неиспользуемой переменной воспроизведены повторным
зондом в тот же день (TEST_REPORT.md, «Повторная проверка с чистого `build/`»).

Значит, неявное сужение в сконвертированном коде сборку бы не прошло, а неявная смена знака дала бы
C0195 — их нет. Явные преобразования, которые пишет конвертер (`INT_TO_WORD`, `WORD_TO_INT` для CTU,
`REAL_TO_<тип>` для SCALE_X), стоят под пометками `MIGRATION-CHECK` (`fb.counter`, `func.scale_x_int`).
Неиспользуемые переменные ищет iec_checker (UnusedVariable, ниже).

## st_lint

**Настройки.** `tools/check/st_lint.toml` = умолчания `st_lint.py` плюс исключение `src/*/Converted/*` для
пяти правил оформления по CONTRIBUTING.md (обоснование — и в шапке файла):

| Правило | Почему снято с `Converted` |
|---|---|
| STL004 — `TODO` без номера issue | пометки `MIGRATION-TODO` — механизм отчёта конвертера ([CONVERSION_REPORT.md](CONVERSION_REPORT.md)), а не задачи трекера |
| STL006 — префиксы объектов | имена S7 сохраняются: `UDT_AnalogCfg`, `DB_Plant`, `FC_Statistics` — так их ищут по исходнику и тегам HMI/SCADA |
| STL007 — префиксы переменных | то же для переменных: `condition`, `tonOn`, `feedbackTime` |
| STL008 — «магические числа» | числа — константы исходного SCL; вынос в `GVL_Const` — ручной этап после проверки поведения |
| STL011 — «время счётом циклов» (эвристика) | ложное срабатывание: `cycleCount` в `FB_Sequencer` — число циклов промывки, а не время |

Остальное — заголовок POU (STL001), табуляция, длина строки, ASCII в идентификаторах и строках,
нормализация файла, подавления (STL002, STL003, STL005, STL009, STL010, STL012) и раскладка (LAY*) —
проверяется и в `Converted`: конвертер обязан выдавать аккуратный текст. Тест
`tools_project/test_repo_config.py` следит, чтобы настройки отличались от шаблона только этим.

**Подавления в рукописном коде.** 14 строк `// lint:allow STL007` — входы и выходы таймеров и детектора
спада S7Compat (`IN`, `PT`, `Q`, `ET`, `CLK`): имена интерфейса TON/TOF/TP/F_TRIG нужны, чтобы
сгенерированный код вызывал `FB_S7Ton` так же, как `TON`, без правок вызовов.

## iec_checker

### Конструкции, которые раньше не разбирались

До понижения шаблона от 2026-10-16 iec_checker 0.4 давал `ParserError` в шести местах и дальше эти файлы не
анализировал. Код не переписывался ради анализатора (ASSUMPTIONS.md, B5): теперь эти конструкции понижает
шаблон, и файлы анализируются целиком. Что понижение при этом скрывает и добавляет — tools/README.md,
«Что понижение скрывает и добавляет»; для этих мест:

| Файл | Конструкция | Понижение и влияние на анализ |
|---|---|---|
| `src/POUs/S7Compat/F_S7Now/F_S7Now.impl.st` | оператор `TIME()` (единственный источник времени ПЛК без сторонних библиотек; тесты берут время через `F_S7Now()`) | `CDS__TIME()` — вызов без аргументов: значение и тип для iec_checker неизвестны |
| `src/DUTs/Converted/UDT_DosingRecipe.dut.st` | `doseStep : ARRAY[1..4] OF REAL := [0.5, 1.0, 1.5, 2.0]` в структуре | тип элемента без начального значения: OutOfBounds для этого списка не выдаётся (4 значения на 4 элемента; размер проверяет компилятор CODESYS) |
| `src/POUs/Converted/FB_EventLogger/FB_EventLogger.impl.st` | `buffer[i].code` — поле элемента массива | `buffer.code[i]`: массив `buffer` получает ложную UnusedVariable (ниже) |
| `src/POUs/Converted/PRG_Main/PRG_Main.impl.st` | `DB_Hmi.pump[1].startReq` | `DB_Hmi.pump.startReq[1]` |
| `src/POUs/Converted/FB_Ramp/FB_Ramp.impl.st` | пустой оператор `;` (ветка `ELSIF hold`) | ветка → `CDS__NOP();`: в PLCOPEN-CP9 на один оператор больше |
| `src/POUs/Converted/FB_Valve/FB_Valve.impl.st` | `;` в ветке `CASE` (ожидание сброса) | то же |

В этих объектах iec_checker нашёл 98 находок, которых раньше не было видно (в `FB_EventLogger`, `FB_Ramp`,
`FB_Valve`, `PRG_Main`; в `F_S7Now` и `UDT_DosingRecipe` находок нет): PLCOPEN-CP3 — 59, UnusedVariable —
18, PLCOPEN-L17 — 12, PLCOPEN-CP9 — 8, PLCOPEN-L10 — 1. Все они того же вида, что уже обоснованные в
сгенерированном коде (таблица ниже), кроме двух: `EXIT` в `FB_EventLogger` (PLCOPEN-L10) — для него
добавлено отдельное обоснование; UnusedVariable у массива `buffer` того же блока добавляет само понижение
(список UnusedVariable ниже).

### Обоснованные находки

Записи — `tools/check/iec_checker_allow.toml`; каждая используется (неиспользованную запись ловит
`test_run_iec_checker.py::test_integration_repository_sources` шаблона).

| Правило | Где | Число | Обоснование |
|---|---|---:|---|
| PLCOPEN-CP3 | `src/*` | 331 | Переменная без явного начального значения получает значение по умолчанию своего типа (МЭК 61131-3, как в CODESYS); вариант сборки `iec-checker` убирает неконстантные начальные значения |
| PLCOPEN-CP3 | `tests/*` | 162 | То же; результаты тестов присваиваются до чтения |
| PLCOPEN-CP9 | `src/*/Converted/*` | 27 | Сложность — как у исходного блока SCL; конвертер структуру не меняет. Пороги iec_checker 0.4 (сложность > 15, > 25 операторов) и завышенный подсчёт (одна конструкция `IF … ELSE` прибавляет 5 — проверено в шаблоне) |
| PLCOPEN-CP9 | `tests/*` | 111 | Наборы и методы-тесты — последовательности вызовов и проверок; классическая сложность 1–3 |
| PLCOPEN-L17 | `src/*/Converted/*` | 55 | `IF` без `ELSE` перенесены из SCL: «иначе» в исходной логике — сохранить состояние |
| PLCOPEN-L17 | `src/POUs/S7Compat/FB_S7T*` | 5 | В таймерах без ветки «иначе» выходы и момент отсчёта сохраняют значение — это и есть семантика TON/TOF/TP |
| PLCOPEN-L17 | `tests/*` | 58 | Однократный запуск сценария (`IF NOT xDone`) и тесты на несколько циклов (`IF NOT xRtDone`, `IF xRtDone`): в остальных циклах делать нечего |
| PLCOPEN-L10 | `FC_Statistics` | 1 | `CONTINUE` перенесён из SCL (блок проверяет `CONTINUE` и `RETURN` при конвертации) |
| PLCOPEN-L10 | `FB_EventLogger` | 1 | `EXIT` перенесён из SCL как есть: подсчёт записей `WHILE` с выходом на первой пустой (`samples/scl/FB_EventLogger.scl`, раздел `Count entries`). Точный перенос, поведение то же, что в S7; замена на условие цикла — ручной этап после проверки поведения |
| PLCOPEN-CP4 | `GVL_IO` | 3 | Ложное срабатывание: номер слова `%IW32`/`%IW33`/`%IW34` iec_checker считает номером байта; в CODESYS это байты 64–65, 66–67, 68–69 (S7 `%IW64`/`%IW66`/`%IW68`) — перекрытия нет |
| UnusedVariable | `src/*/Converted/*` | 49 | См. ниже |
| UnusedVariable | наборы тестов, `PRG_Tests` | 159 | Артефакт понижения (переменные набора используются в методах, которые сборка выносит в функции) и ложные срабатывания: экземпляры `fbDut`, `fbStandard`, `fbCompat` используются вызовом и чтением выходов; экземпляры наборов в `PRG_Tests` регистрируются объявлением и используются `AreAllTestsFinished()` |

**UnusedVariable в сгенерированном коде** (49 находок):

- ложные срабатывания iec_checker 0.4 — вызов экземпляра ФБ и чтение его выходов (`tonOn`, `edgeAck`,
  `ctuBatch`, `tonStep`, `debOpen`, `lostClosed`… — 27 находок в `FB_AlarmDelay`, `FB_BatchCounter`,
  `FB_Debounce`, `FB_Motor`, `FB_PumpAlternation`, `FB_Sequencer`, `FB_Valve`), аргумент во вложенном
  вызове (`TIME_TO_DINT(cycleTime)` в `FB_PIController`, `FB_Ramp`, `FB_Totalizer`, `TIME_TO_DINT(ti)`,
  `INT_TO_WORD(batchPreset)`, `LEFT(eventText, 18)` — 6), запись полей структуры (`status.running := …`),
  константа в границах `FOR` (`SAMPLE_COUNT`);
- ложное срабатывание, которое добавляет понижение: массив `buffer` в `FB_EventLogger`, к которому
  обращаются только как `buffer[i].code` (после понижения — `buffer.code[i]`, как поле структуры);
- переменные интерфейса S7, которые используют только непереведённые операторы (`MIGRATION-TODO`):
  `archiveDb`, `retryDelay`, `remaining`, `timerValue` в `FB_LegacyTelegram`, `ret_` в `PRG_Startup`,
  `telegramStatus`, `execTime`, `runtimeMem`, `TELEGRAM_DB`, `AREA_DB` в `FB_EventLogger` (`RUNTIME`,
  `PEEK`, `POKE`) — 10;
- стартовая информация OB, которую код OB не читает: `Event_Count` (`PRG_Cyclic_interrupt`),
  `MultiError` (`PRG_Diagnostic_error_interrupt`), `Remanence` (`PRG_Main`).

Удаление неиспользуемого — ручной этап после перевода TODO, а не задача конвертера.

**Артефакты сборки** (163: CP3 — 117, UnusedVariable — 46) — находки на строках, которые создало
понижение (копии переменных набора в функциях-методах); на код не указывают.

## RuSTy

Компилятор RuSTy 1.0.6 проверяет синтаксис и типы варианта сборки `rusty`; компоновки нет. Объявления
coUnit, блоков CODESYS Standard и преобразований `TIME_TO_DINT` и т. п. (в stdlib RuSTy их нет: там `TIME`
64-битный) — из прокладок `tools/check/rusty_shims/` шаблона (`codesys_conversions.st` — с 2026-10-16;
раньше `FB_PIController`, `FB_Ramp`, `FB_Totalizer` и пять зависящих от них файлов были исключены, а
pytest добавлял объявление `TIME_TO_DINT` сам).

**Что RuSTy отвергает и почему** (расхождения диалектов, а не ошибки кода; файлы — в
`tools/check/rusty_exclude.txt` с причинами). Каждое исключение проверено прогоном без него
(2026-10-16): без любого из трёх `run_rusty.py` завершается ошибкой.

| Причина | Файлы | Без исключения |
|---|---|---|
| RuSTy убирает имя GVL (замена R3 при `qualified_only`), одинаковое имя в двух GVL неоднозначно | `DB_Telegram` | E004 `heartbeat: Ambiguous global variable` (`heartbeat` есть и в `DB_Plant`) |
| `%MW5` и `%MD5` для RuSTy — одна аппаратная переменная; в CODESYS это байты 10–11 и 20–23 (S7 `%MW10` и `%MD20`) | `GVL_Markers` | E037 `cannot assign 'WORD' to ': DWORD'`, компиляция прерывается |
| зависит от исключённого объявления | `PRG_Main` | E048 — 5 ссылок на `HMI_DosingPacked`, `HMI_StatusPT101`, `HMI_P101Running`, `Clock_1Hz` из `GVL_Markers` |

`run_rusty.py` проверяет остальные 51 файл из 54 (было 44 из 54). Чтобы исключения не уменьшали покрытие,
`s7conv/tests/test_rusty_check.py::test_repository_sources_pass_rusty_with_shims` проверяет **весь**
`src/` и `tests/`: у `GVL_Markers` сняты `AT`, исключён только `DB_Telegram` — 53 файла из 54 проходят без
ошибок. Ещё два теста там же проверяют результат конвертера по фикстурам и по корпусу с настройками по
умолчанию; своих прокладок у тестов больше нет.

**Предупреждение E067** «Implicit downcast from 'DINT' to 'INT'» в `FB_PumpAlternation`
(`required := LIMIT(0, demand, PUMP_COUNT)`): в RuSTy литерал `0` — `DINT`, и `LIMIT` возвращает `DINT`;
в CODESYS литерал получает тип из контекста (`INT`). Оставлено как есть: сборка CODESYS 3.5.17.30 на этой
строке предупреждения не даёт (в корпусе 0 предупреждений, а неявное сужение DINT → INT там — ошибка C0032,
раздел «Компилятор CODESYS»).

Ошибка конвертера, найденная RuSTy и исправленная: `CTU_INT.PV`/`CV` в S7 — `INT`, в CODESYS Standard —
`WORD`; конвертер теперь пишет явные `INT_TO_WORD(...)` и `WORD_TO_INT(...)` (раньше — неявное
преобразование со сменой знака, на которое CODESYS выдаёт предупреждение).

## Тесты шаблона

Тесты `tools/tests/` шаблона выполняются полностью, без `--deselect` в `pyproject.toml`: настройки
проекта они проверяют только на разбор и схему, а исходники — с файлами проекта.

| Тест шаблона | Что проверяет в проекте |
|---|---|
| `test_st_lint.py::test_template_toml_matches_defaults` | умолчания `st_lint.py` против эталона шаблона `tools/tests/fixtures/st_lint_template.toml` (`st_lint.toml` проекта не сравнивается) |
| `test_st_lint.py::test_repository_toml_is_valid` | `st_lint.toml` проекта разбирается, каждый ключ известен |
| `test_run_iec_checker.py::test_integration_repository_sources` (`src`, `src+tests`) | `src/` и `tests/` проходят iec_checker с `tools/check/iec_checker_allow.toml` проекта: `ParserError` 0, необоснованных 0, с `tests/` каждое обоснование используется |
| `test_run_rusty.py::test_repository_exclude_file_is_valid` | у каждой строки `rusty_exclude.txt` есть причина |

Что проект отличается от шаблона ровно задуманным, проверяет `tools_project/test_repo_config.py`:
`st_lint.toml` = умолчания плюс исключения `src/*/Converted/*` для пяти правил оформления, форматные
правила в `Converted` включены; в `config.json` — задачи режима `normal` из OB корпуса и ссылка на
Standard (`test_codesys_config_is_template_config_with_corpus_tasks`,
`test_codesys_projects_reference_standard_and_counit`).

## Предложения в шаблон

Учтены в шаблоне: ссылка на Standard по умолчанию, тесты `cds.py` на собственной копии конфигурации,
полная проверка компиляции `cds.py check` (видит объекты без задачи, в том числе OB82), понижение
`iec-checker` для массива с начальным значением в структуре, `a[i].b` и пустого оператора `;`,
преобразования TIME в прокладках RuSTy. Остаются (оба — вариант сборки `rusty`):

- одинаковые имена в разных GVL с `qualified_only` (замена R3 убирает имя GVL, E004) — например,
  переносить имя GVL в имя переменной; тогда `DB_Telegram` не нужно исключать;
- перекрывающиеся по номеру адреса разного размера (`%MW5` и `%MD5`, E037) — тогда не нужно исключать
  `GVL_Markers` и `PRG_Main`.
