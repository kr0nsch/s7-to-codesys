# Инструменты шаблона (`tools/`)

Исходники ST лежат в `src/` и `tests/` в раскладке [docs/LAYOUT.md](../docs/LAYOUT.md). Инструменты ниже
читают эту раскладку, собирают из неё обычный ST и проверяют его без CODESYS.

| Инструмент | Что делает | Python |
|---|---|---|
| `codesys/stlayout.py` | единственный разбор и запись раскладки: лексер ST, заголовки, объекты, проверки | IronPython 2.7 и 3.8+ |
| `assemble.py` | склейка раскладки в `build/assembled/` (варианты `iec`, `rusty`, `iec-checker`) | 3.11+ |
| `st_flavors.py` | замены текста для вариантов `rusty` и `iec-checker` (используется `assemble.py`) | 3.11+ |
| `check/st_lint.py` | линтер ST по правилам `CONTRIBUTING.md` | 3.11+ |
| `check/run_iec_checker.py` | статанализ iec_checker с обоснованием находок | 3.11+ |
| `check/run_rusty.py` | проверка компилятором RuSTy (`plc --check`) | 3.11+ |
| `codesys/import_sources.py`, `export_sources.py`, `build.py`, `run_tests.py` | работа с проектом CODESYS (IronPython, CODESYS Scripting) — описаны в `docs/MANUAL_STEPS.md` | IronPython 2.7 |

Зависимости для разработки: `python -m pip install -r requirements-dev.txt` (ruff, mypy, pytest, hypothesis).
Настройки ruff, mypy и pytest — в `pyproject.toml`.

Быстрая проверка всего, что не требует CODESYS:

```
python -m ruff check .
python -m ruff format --check .
python -m mypy
python -m pytest
python tools/assemble.py
python tools/check/st_lint.py
python tools/check/run_iec_checker.py            # бинарник v0.4 (в CI — тоже); образ nightly: --docker IMAGE
python tools/check/run_rusty.py --optional       # если RuSTy не установлен — пропуск
```

## `codesys/stlayout.py` — контракт раскладки

Модуль написан на общем подмножестве Python 2.7 и 3.8+, чтобы его без изменений импортировали и
скрипты CODESYS (IronPython 2.7), и инструменты на Python 3: без f-строк, аннотаций (типы — в
комментариях `# type:`), `pathlib`, `dataclasses`; файлы — через `io.open(..., encoding='utf-8')`.
Совместимость проверяет `tools/tests/test_py27_compat.py` (разбор `ast`: интерпретатора 2.7 в окружении нет).
Формат кода скриптов `tools/codesys/*.py` ruff не трогает: форматтер рассчитан на Python 3.

Основной API:

```python
import stlayout as L

result = L.scan(root, "src")  # ScanResult: objects (детерминированный порядок), issues, errors, ok
for obj in result.objects:  # StObject
    obj.kind  # dut | gvl | pvl | itf | pou
    obj.pou_kind  # program | function_block | function (для pou)
    obj.name, obj.folder  # имя и папки проекта CODESYS внутри категории
    obj.decl, obj.impl  # тексты (нормализованные)
    obj.header  # DeclHeader: keyword, name, modifiers, extends, implements, return_type, type_kind
    obj.methods  # [StMethod: name, decl, impl (None у интерфейса и ABSTRACT без тела)]
    obj.properties  # [StProperty: name, decl, get_decl, get_impl, set_decl, set_impl, has_get, has_set]
L.write_objects(objects, root, "src", clean=True)  # экспорт: те же файлы; clean — удалить лишние *.st;
# регистр имён существующих каталогов и файлов приводится к именам объектов (переименование в IDE
# только регистром на Windows не теряет файлы)
L.object_files(obj)  # [(путь от корня, текст)] — какие файлы соответствуют объекту
L.parse_header(text), L.parse_var_blocks(text), L.parse_type_decl(text), L.tokenize(text)
L.normalize_text(text), L.read_text(path), L.write_text(path, text)
```

**Нормализация текста** (`normalize_text`, её применяют `scan` и `write_objects`): убирается BOM;
CRLF и одиночный CR заменяются на LF; у каждой строки срезаются хвостовые пробелы и табы; хвостовые
пустые строки убираются; непустой текст заканчивается ровно одним `\n`; текст из одних пробельных
символов становится пустым (пустой файл — 0 байт). Табы в начале и середине строк не меняются
(их ловит линтер). Цикл `scan → write_objects` для нормализованного входа даёт побайтно те же файлы;
для ненормализованного — нормализованные, и следующий цикл уже ничего не меняет.

**Разбор заголовков** пропускает комментарии `//`, `(* *)` (с вложенностью), `/* */` и прагмы `{...}`;
строки `'...'`/`"..."` с экранированием `$` и типизированные литералы (`T#5s`, `INT#3`, `E_Mode#Auto`)
лексер разбирает целиком, поэтому ключевые слова внутри них не мешают.

В раскладке игнорируются скрытые файлы (`.gitkeep`) и `*.md`. Замечания `scan()`:

| Код | Что не так |
|---|---|
| LAY001 | неизвестный вид файла (`Foo.txt`, `X.method.impl.st` в интерфейсе, `.decl.st` чужого объекта) |
| LAY002 | имя в тексте не совпадает с именем файла (`FB_A.decl.st` объявляет `FB_B`) |
| LAY003 | нет обязательного файла: тела POU, тела метода (кроме `ABSTRACT`), аксессоров свойства |
| LAY004 | файл без пары: тело метода без объявления, аксессор без `<P>.prop.decl.st` |
| LAY005 | недопустимое содержимое: `END_FUNCTION_BLOCK` и т. п. в объявлении или теле, нет `END_TYPE`/`END_VAR`, методы у `FUNCTION`; предупреждение — `.pvl.st` без `PERSISTENT` |
| LAY006 | имя повторяется (имена CODESYS — без учёта регистра): объекты, методы и свойства одного POU, `src/` и `tests/` |
| LAY007 | файл не в UTF-8 |
| LAY008 | не на своём месте: неизвестный каталог верхнего уровня, файл в папке без объекта, каталог внутри объекта |
| LAY009 | нет или неверный заголовок (`TYPE`, `VAR_GLOBAL`, `INTERFACE`, `METHOD`, `PROPERTY ... : тип`, ...) |
| LAY010 | имя файла или каталога — не идентификатор ST |
| ASM001 | (`assemble.py`) цикл наследования `EXTENDS` |

## `assemble.py` — склейка

```
python tools/assemble.py [--root R] [--src src] [--tests] [--tests-dir tests]
                         [--flavor iec|rusty|iec-checker] [--out DIR] [--strip-namespace NS]... [--check-only] [-q]
```

| Флаг | Смысл |
|---|---|
| `--src`, `--tests-dir` | каталоги раскладки (от `--root`, по умолчанию корень репозитория) |
| `--tests` | добавить объекты `tests/` (имена должны быть уникальны вместе с `src/`) |
| `--flavor` | вариант сборки, по умолчанию `iec` |
| `--out` | каталог результата; по умолчанию `build/assembled/` для `iec` и `build/assembled/<вариант>/` для остальных |
| `--strip-namespace` | убрать префикс библиотеки (`CfUnit.`, `PL.`); можно повторять; точка в конце не обязательна |
| `--check-only` | только проверить раскладку и сборку, ничего не писать |

Результат: `<Имя>.st` на каждый объект верхнего уровня, `all.st` и `sourcemap.json`. Перед записью из
каталога результата удаляются старые `*.st` (только верхнего уровня, подкаталоги вариантов не трогаются).
Порядок в `all.st`: DUT, GVL, интерфейсы, функции, функциональные блоки, программы; внутри группы
базовые типы раньше производных (`EXTENDS`), затем по имени. `sourcemap.json` — список сегментов
`[строка в собранном файле, число строк, исходный файл или null, строка в исходном файле]`;
`null` — строки, созданные сборкой. По карте `run_rusty.py` и `run_iec_checker.py` показывают находки в
строках исходников. Все замены сохраняют число строк фрагмента, поэтому карта точная.

Коды выхода: 0 — успех, 1 — ошибки раскладки или сборки (сообщения `путь:строка: КОД текст`), 2 — аргументы.

### Варианты сборки

| Вариант | Для чего | Что меняется |
|---|---|---|
| `iec` | чтение, `all.st`, основа других вариантов | ничего: объявление, методы (`METHOD ... END_METHOD`), свойства (`PROPERTY_GET`/`PROPERTY_SET ... END_PROPERTY`), тело, `END_...` — как в docs/LAYOUT.md |
| `rusty` | `run_rusty.py` | `iec` + замены совместимости RuSTy (таблица ниже) |
| `iec-checker` | `run_iec_checker.py` | понижение для разборщика iec_checker v0.4 (таблица ниже); **только для статанализа**, семантика приближённая |

### Замены совместимости RuSTy (`--flavor rusty`)

Найдены прогоном RuSTy 1.0.6 `plc --check` на реалистичном ST CODESYS
(`tools/tests/fixtures/sample/`, плюс пробные файлы).

| № | Конструкция CODESYS | Замена | Ошибка RuSTy без замены |
|---|---|---|---|
| R1 | `itfX <> 0`, `itfX = 0`, `0 <> itfX`; переменная с префиксом `itf` (также `THIS^.itfX`, `stCfg.itfX`) | `__ItfIsSet(ADR(itfX))`, `(NOT __ItfIsSet(ADR(itfX)))`; функция `__ItfIsSet` — в `__RustyCompat.st` и один раз в начале `all.st`, только если замена была | E031: `__FATPOINTER` и `DINT` несовместимы |
| R2 | `NS.Имя` для `--strip-namespace NS` | `Имя` (объявления — в прокладках `tools/check/rusty_shims/`) | E048: не найдено `CfUnit` |
| R3 | `GVL_Имя.переменная` (имена GVL/PVL проекта) | `переменная` — в RuSTy у `VAR_GLOBAL` нет имени; одинаковые имена в разных GVL дадут ошибку дубля | E048: не найдено `GVL_Const` |
| R4 | `x S= e;`, `x R= e;` | `IF e THEN x := TRUE; END_IF;` / `... := FALSE` | E007: разбор |
| R5 | `__ISVALIDREF(r)` | `(ADR(r) <> 0)` | E048 |
| R6 | `STRING(80)`, `WSTRING(80)` | `STRING[80]`, `WSTRING[80]` | предупреждение E014 |
| R7 | `VAR_INST`, `VAR_STAT` | `VAR` (тип тот же, время жизни — нет: только для проверки типов) | E007 |
| R8 | `VAR_GLOBAL PERSISTENT RETAIN` | `VAR_GLOBAL RETAIN` | E138/E006 |
| R9 | `UNION ... END_UNION` | `STRUCT ... END_STRUCT` (типы полей проверяются, раскладка памяти другая) | E007 |
| R10 | `TYPE ST_B EXTENDS ST_A : STRUCT` | поля `ST_A` (и её баз) одной строкой в начале `ST_B`, `EXTENDS` убирается; база не из проекта — без изменений | E006/E007 |
| R11 | `PROPERTY_GET PUBLIC Имя` (модификатор доступа свойства) | `PROPERTY_GET Имя` | E138, E001 |
| R12 | типы `CTU`, `CTD`, `CTUD` в объявлениях | `CDS_CTU`, `CDS_CTD`, `CDS_CTUD` из `rusty_shims/codesys_standard.st` (у CODESYS Standard входы `RESET`/`LOAD` и тип `WORD`, у RuSTy — `R`/`LD` и `INT`; сигнатуры CODESYS — сверить с источником) | E089, E048 |

Ожидаемые предупреждения RuSTy, которые не считаются ошибкой: E049 «Illegal access to private member» —
обращение производного ФБ к `VAR` базового (в CODESYS допустимо); E067 «Implicit downcast» для литералов.
RuSTy принимает без замен: `METHOD` внутри `FUNCTION_BLOCK`, `EXTENDS`, `IMPLEMENTS`, `ABSTRACT`, `SUPER^`,
`THIS^`, `REFERENCE TO`, `REF=`, `POINTER TO`, `ADR`, `LTIME`, прагмы `{attribute ...}`, `AT %IX0.0`,
`INT(0..100)`, `ARRAY[*]`, перечисления с базовым типом и `E_Mode.Auto`, WSTRING с кириллицей.

### Понижение для iec_checker (`--flavor iec-checker`)

iec_checker v0.4 разбирает подмножество МЭК 61131-3. Понижение проверено настоящим бинарником v0.4
на `tools/tests/fixtures/sample/`, на `src/` и `tests/` шаблона. С образом `nightly` понижение локально
не проверялось (Docker не установлен) — его проверяет необязательное задание CI `iec_checker_nightly`.

| Конструкция CODESYS | Понижение | Влияние на анализ |
|---|---|---|
| `FUNCTION_BLOCK`/`PROGRAM` с методами | тело ФБ без методов; метод → `FUNCTION <ФБ>__<Метод> : <тип или BOOL>`; в `VAR` — копии переменных ФБ (и базовых ФБ проекта), которые упоминает метод, и переменная-результат `<Метод>`; в конце `<ФБ>__<Метод> := <Метод>;` | **приближение**: состояние экземпляра не связано с методом; находки на сгенерированных строках — статус `artifact` |
| свойство ФБ | `FUNCTION <ФБ>__<Свойство>__get : <тип>` и `__set : BOOL` с `VAR_INPUT <Свойство>` | как для методов |
| свойство интерфейса | `METHOD <Свойство>__get : <тип>` / `METHOD <Свойство>__set` | — |
| `SUPER^.M(` | `<База>__M(` (база из проекта); `THIS^.x`, `SUPER^.x` → `x`; `p^` → `p` | разыменование не анализируется |
| `EXTENDS`, `IMPLEMENTS`, `ABSTRACT`, `FINAL`, `PUBLIC`, `INTERNAL` у ФБ | убираются | наследование не учитывается |
| `FUNCTION` без типа результата | `: BOOL` | — |
| прагмы `{...}` | удаляются | — |
| `/* ... */` | `(* ... *)` | — |
| GVL, PVL (`VAR_GLOBAL` вне конфигурации) | обёртка `CONFIGURATION <Имя> ... END_CONFIGURATION`; `PERSISTENT` убирается | — |
| `POINTER TO`, `REFERENCE TO` | `REF_TO`; `r REF= x;` → `r := ADR(x);` | — |
| `S=`, `R=` | `IF ... THEN ... END_IF;` | — |
| `VAR_INST`, `VAR_STAT` | `VAR` | — |
| `STRING(n)`, `INT(0..100)`, `ARRAY[*]` | `STRING[n]`, `INT`, `ARRAY[0..0]` | — |
| `UNION`; `STRUCT EXTENDS`; массив в `STRUCT`; базовый тип перечисления `) INT;` | `STRUCT`; поля базы в начале; тип элемента; `) ;` | массивы в структурах не анализируются |
| начальные значения не-литералы (`:= E_Mode.Auto`, `:= GVL_Const.X`, `:= (a := 1)`, `[3(0)]`) | удаляются | отсюда дополнительные PLCOPEN-CP3 |
| метки `CASE` `E_Mode.Auto`, `GVL_Const.STEP` | целое значение из DUT/GVL проекта | неизвестная метка остаётся — ParserError |
| строковые литералы: пробел, `$`, кавычки, не-ASCII | `$hh` (STRING; не-ASCII → `$3F`), `$hhhh` (WSTRING) | — |
| идентификаторы с ведущим `_` (`__NEW`, `__QUERYINTERFACE`); `__ISVALIDREF(x)` | `CDS__NEW`, ...; `(ADR(x) <> 0)` | — |

Не понижается — iec_checker v0.4 сообщит ParserError, конструкцию нужно переписать: пустой оператор `;`
и пустые ветви `IF`/`CASE`, `JMP` и метки переходов, метки `CASE` с неизвестными символами.

## `check/st_lint.py` — линтер

```
python tools/check/st_lint.py [пути...] [--root R] [--config FILE | --no-config] [--json] [--strict] [--list-rules]
```

Пути — каталоги раскладки от `--root` (по умолчанию `[lint] paths` = `src`, `tests`). Вывод:
`путь:строка:столбец: ПРАВИЛО [уровень] текст` и итоговая строка; `--json` — JSON
(`findings`, `summary`). Код выхода 1 — есть ошибки (с `--strict` — и предупреждения), 2 — ошибка настроек.
Замечания раскладки (LAYxxx) — всегда ошибки.

| Правило | Проверка | По умолчанию |
|---|---|---|
| STL001 | заголовок-комментарий POU (до первой секции `VAR`) упоминает «назначение», «автор», «версия», «документ» и путь `docs/...` | ошибка |
| STL002 | табуляция | ошибка |
| STL003 | строка длиннее `max_line_length` (120) символов | ошибка |
| STL004 | `TODO`/`FIXME` в комментарии без номера issue: нужно `TODO(#12)` | ошибка |
| STL005 | не-ASCII символ в идентификаторе или вне комментариев и строк | ошибка |
| STL006 | префиксы имён: `PRG_`, `FB_`, `F_`, `ST_`, `E_`, `U_`, `I_`, `GVL_` (PVL — `PVL_` или `GVL_`; псевдонимы типов не проверяются); методы и свойства — PascalCase (`^[A-Z][A-Za-z0-9]*$`, кроме `FB_init`, `FB_exit`, `FB_reinit`) | ошибка |
| STL007 | префикс переменной по типу (`x` BOOL, `i` INT, `di` DINT, `r` REAL, `s` STRING, `ws` WSTRING, `t` TIME, `a` массив, `p` указатель, `ref` ссылка, `e` `E_*`, `st` `ST_*`, `u` `U_*`, `fb` `FB_*` и TON/TOF/TP/R_TRIG/..., `itf` `I_*`; после префикса — заглавная буква или цифра); константы `VAR CONSTANT`/`VAR_GLOBAL CONSTANT` — UPPER_SNAKE_CASE; проверяются POU, методы, аксессоры, GVL, поля DUT; неизвестные типы пропускаются; исключения — `allow_names` | ошибка |
| STL008 | «магическое число»: десятичный литерал в теле (POU, метода, аксессора), кроме 0, 1, 2 (по значению, `-1` тоже); не проверяются индексы `[...]`, метки `CASE`, номер бита `x.3`, литералы с основанием (`16#FF`) и типизированные (`T#5s`, `INT#3`), объявления (начальные значения, границы массивов), `GVL_Const`, по умолчанию `tests/*` | ошибка |
| STL009 | файл не нормализован: не UTF-8, BOM, CRLF/CR, нет `\n` в конце, пустые строки в конце, хвостовые пробелы | ошибка |
| STL010 | не-ASCII в литерале `STRING '...'` — для кириллицы `WSTRING "..."` | ошибка |
| STL011 | эвристика «время счётом циклов»: `X := X + 1` (или `1 + X`), где имя `X` содержит `cycle`/`cyc`/`scan`/`tick`, или `X` сравнивается с идентификатором «времени» (`time`, `delay`, `timeout`, `_ms`, `_s`, `sec`) | предупреждение |
| STL012 | неверное подавление `lint:allow`: нет причины или неизвестное правило | ошибка |

**Формат заголовка POU** (STL001). Комментарий стоит перед строкой `PROGRAM`/`FUNCTION_BLOCK`/`FUNCTION`
или сразу после неё, до первой секции `VAR`; можно `(* *)` или строки `//`:

```
// Назначение: что делает POU и в каких режимах
// Автор:      <ИМЯ ФАМИЛИЯ>
// Версия:     0.1.0
// Документ:   docs/ARCHITECTURE.md, раздел «...»
FUNCTION_BLOCK FB_Example
```

**Подавление**: `// lint:allow STL008 причина` (или `(* lint:allow STL008, STL004 причина *)`) действует
на свою строку, а если комментарий стоит в строке один — и на следующую строку. Без причины подавление
не действует и само даёт STL012.

**Настройки** — `tools/check/st_lint.toml` (значения по умолчанию повторяют `st_lint.py`, тест
`test_toml_matches_defaults` следит за этим): `[lint]` (`paths`, `exclude`, `max_line_length`),
`[severity]` (`error`/`warning`/`off` для каждого правила), `[rules.STLxxx]` (параметры правила и
`exclude` — шаблоны fnmatch путей от корня; `*` захватывает и `/`).

## `check/run_iec_checker.py` — статанализ

```
python tools/check/run_iec_checker.py [--tests] [--binary PATH | --docker IMAGE] [--allow FILE]
                                     [--out DIR] [--json FILE] [--md FILE] [--strip-namespace NS]... [--optional]
```

1. Собирает вариант `iec-checker` (по умолчанию только `src/`, с `--tests` — и `tests/`) в
   `build/assembled/iec-checker/`.
2. Запускает iec_checker **по каждому файлу** (`-o json`): у находок, кроме ошибок разбора, iec_checker
   не заполняет поле `file`, поэтому общий запуск по каталогу не позволяет понять, где находка.
3. Пересчитывает строки на исходники по `sourcemap.json`; находки на весь файл (строка 0, например
   PLCOPEN-CP9) относятся к объявлению объекта.
4. Сверяет с `tools/check/iec_checker_allow.toml` и пишет `build/iec_checker.json` и `build/iec_checker.md`.

Бинарник: `--binary`, переменная `IEC_CHECKER`, `PATH` (`iec_checker`, `iec_checker_Linux_x86_64`,
`iec_checker_Windows_x86_64.exe`), `~/.local/plc-tools/iec-checker/`. Docker: `--docker jubnzv1/iec-checker:nightly`
(`docker run --rm -v <каталог>:/work -w /work <образ> -o json <файл>`; точка входа образа — `iec_checker`).

| Статус | Значение | Код выхода |
|---|---|---|
| `error` | необоснованная находка; ParserError, LexingError и сбой инструмента — всегда `error` | 1 |
| `allowed` | есть запись в файле обоснований | 0 |
| `artifact` | находка на строке, созданной сборкой (копии переменных ФБ в функциях-методах и т. п.) | 0 |

Файл обоснований:

```toml
[[allow]]
id = "PLCOPEN-CP3"          # правило iec_checker (шаблон fnmatch)
file = "src/POUs/F_Clamp/*" # путь исходника или имя собранного файла (шаблон fnmatch, * захватывает /)
match = "RVALUE|RMIN"       # необязательно: регулярное выражение по тексту сообщения
reason = "..."              # обязательно; подробный разбор — docs/STATIC_ANALYSIS.md
```

Неиспользованные записи выводятся предупреждением (записи для `tests/` — только при `--tests`).
`--optional`: нет бинарника или docker — предупреждение и код 0.

## `check/run_rusty.py` — проверка RuSTy

```
python tools/check/run_rusty.py [--plc PATH] [--stdlib DIR] [--no-tests] [--exclude-file FILE] [--shims DIR]
                                [--strip-namespace NS]... [--out DIR] [--log FILE] [--json FILE] [--optional]
```

Собирает вариант `rusty` (`src/` и `tests/`) в `build/assembled/rusty/` и запускает
`plc --check <файлы> -i <stdlib/*.st> -i <rusty_shims/*.st> --error-format clang` (компоновки нет — только
разбор и проверка типов). Диагностики выводятся в строках исходников; журнал — `build/rusty.log`,
сводка — `build/rusty.json`. Код выхода 1 — `plc` вернул ошибку (предупреждения не считаются).

| Что | Откуда |
|---|---|
| компилятор `plc` | `--plc`, `RUSTY_PLC`, `PATH`, `~/.local/plc-tools/rusty/plc[.exe]` |
| объявления stdlib (`*.st`) | `--stdlib`, `RUSTY_STDLIB_INCLUDE`, рядом с `plc`: `stdlib/stdlib/include`, `stdlib/include`, `include` |
| исключения | `tools/check/rusty_exclude.txt`: `<Имя>.st  # причина` на строку, причина обязательна |
| прокладки | `tools/check/rusty_shims/*.st` — только объявления для проверки |
| пространства имён | по умолчанию убираются `coUnit.` и `CfUnit.`; `--strip-namespace` задаёт свой список |

Прокладки:
- `cfunit.st` — CfUnit/coUnit: `FB_TestSuite` с методами `Assert*` и `AreAllTestsFinished`, функции `TEST`,
  `TEST_ORDERED`, `TEST_FINISHED`, `TEST_FINISHED_NAMED`, `IS_TEST_FINISHED`, `RUN`, `RUN_IN_SEQUENCE`,
  тип `T_MaxString`. Имена и сигнатуры взяты из исследования API coUnit 1.2.0.0
  (`_research/cfunit.md`, раздел 2, по исходнику библиотеки на CODESYS Forge); компилятором CODESYS они не
  проверялись. В коде namespace библиотеки v1.2 — `coUnit`, в v1.0/1.1 — `CfUnit`; убираются оба.
- `codesys_standard.st` — счётчики `CDS_CTU`, `CDS_CTD`, `CDS_CTUD` с сигнатурами CODESYS Standard (замена R12).

`--optional`: нет компилятора или stdlib — предупреждение и код 0 (необязательный шаг CI).

## Тесты инструментов

`python -m pytest` (каталог `tools/tests/`):

| Файл | Что проверяет |
|---|---|
| `test_stlayout.py` | лексер без потерь (hypothesis), комментарии и прагмы, заголовки, секции VAR, DUT, метки CASE, `scan` и все коды LAY, цикл `scan → write` побайтно, запись поверх файлов с другим регистром имён |
| `test_py27_compat.py` | `tools/codesys/*.py` без конструкций и модулей только Python 3 |
| `test_assemble.py` | эталоны всех вариантов (`tools/tests/golden/<вариант>/`), порядок `all.st`, карта строк, CLI, каждое правило замен rusty и понижения iec-checker |
| `test_st_lint.py` | каждое правило — срабатывание и отсутствие, подавления, настройки, CLI |
| `test_run_rusty.py`, `test_run_iec_checker.py` | поиск инструментов, команды, разбор вывода, обоснования, отчёты; интеграционные — с настоящими `plc` и iec_checker, в том числе `src/` и `tests/` шаблона: каждое обоснование `iec_checker_allow.toml` должно использоваться |

Интеграционные тесты помечены `@pytest.mark.integration` и пропускаются, если инструмента нет
(`python -m pytest -m integration` — только они). Эталоны обновляются так:
`UPDATE_GOLDEN=1 python -m pytest tools/tests/test_assemble.py` — после этого просмотрите дифф.
Реалистичный пример раскладки для тестов — `tools/tests/fixtures/sample/` (вымышленный двигатель
с контактором: наследование ФБ, интерфейсы со свойствами, UNION, STRUCT EXTENDS, PVL, тесты CfUnit).
