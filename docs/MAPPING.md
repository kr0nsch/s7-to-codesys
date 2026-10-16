# Таблица соответствий S7/SCL → ST CODESYS V3.5

Правила, по которым `s7conv` переводит SCL (TIA Portal) в ST CODESYS 3.5.17. Код правил — в
`s7conv/mapping.py` (таблицы) и `s7conv/emitter.py` (решения, зависящие от контекста); подмножество
SCL — [GRAMMAR.md](GRAMMAR.md); итог по корпусу — [CONVERSION_REPORT.md](CONVERSION_REPORT.md).

Обозначения в столбце «Статус»: **авто** — перевод без пометки; **проверка** — перевод с пометкой
`// MIGRATION-CHECK: причина (стр. N)` над конструкцией; **TODO** — не переводится: в коде
`// MIGRATION-TODO: причина (стр. N)` и закомментированный исходный текст. В скобках — идентификатор
правила из отчёта.

Всё, что ниже помечено «сверить с источником», не проверено по документации производителя или
сборкой в CODESYS — это допущение, его надо проверить до ввода в эксплуатацию.

## Блоки и объекты раскладки

| S7 | CODESYS (раскладка шаблона) | Статус | Примечание |
|---|---|---|---|
| `FUNCTION_BLOCK "FB_X"` | `src/POUs/FB_X/FB_X.decl.st` + `.impl.st` — `FUNCTION_BLOCK FB_X` | авто | имя сохраняется (на имена завязаны HMI/SCADA) |
| `FUNCTION "FC_X" : Real` | `FUNCTION FC_X : REAL` | авто | `: Void` → функция без типа результата (сверить с компилятором CODESYS) |
| `ORGANIZATION_BLOCK "Main"` | `PROGRAM PRG_Main` + задача в `tasks.json` | авто/проверка | префикс `PRG_` по CONTRIBUTING.md; см. «OB и задачи» |
| `DATA_BLOCK` с `VAR` (глобальный) | `src/GVLs/<DB>.gvl.st`: `{attribute 'qualified_only'}`, `VAR_GLOBAL` | авто | `"DB".m` → `DB.m`; имя GVL = имя DB |
| экземплярный `DATA_BLOCK "DB" "FB"` | переменная `DB : FB;` в `GVL_InstanceDBs` | авто | `"DB"(...)` → `GVL_InstanceDBs.DB(...)`, `"DB".out` → `GVL_InstanceDBs.DB.out` |
| `DATA_BLOCK "DB" "UDT_X"`, `DATA_BLOCK "DB" Array[...] of ...` | переменная `DB : UDT_X;` в `GVL_InstanceDBs` | авто | DB по типу не отличить от экземплярного по тексту — решает таблица символов |
| `DATA_BLOCK "T_DB" IEC_TIMER` | `T_DB : TON;` (тип — по вызову `"T_DB".TON(...)`) | авто | без вызова тип не определить → TODO (`db.generic`) |
| вызов `"X_DB"(...)` без исходника DB | `X_DB : FB_X;` в `GVL_InstanceDBs`, если есть `FB_X` (суффиксы `_DB`, `_IDB`, `_Instance`, `DB`) | проверка (`db.implicit_instance`) | эвристика по имени |
| `TYPE "UDT_X" STRUCT ... END_STRUCT` | `src/DUTs/UDT_X.dut.st` — `TYPE UDT_X : STRUCT ... END_STRUCT END_TYPE` | авто | |
| анонимный `Struct` в объявлении | DUT `ST_<блок>_<поле>` (вложенные — `ST_<блок>_<поле>_<поле>`) | авто (`type.struct_dut`) | в CODESYS нет анонимных структур в `VAR` |

Шапка каждого POU, GVL и DUT — комментарий по `CONTRIBUTING.md` (Назначение из `TITLE` или комментария
блока, Автор/Версия из `AUTHOR`/`VERSION`, Документ, Источник с файлом и строками), затем пометки
уровня блока и комментарий из начала исходного файла. Линтер `st_lint` правило STL001 принимает эту
шапку. Пустое тело — комментарий (раскладка не допускает пустых файлов тела).

## Секции переменных

| S7 | CODESYS | Статус |
|---|---|---|
| `VAR_INPUT`, `VAR_OUTPUT`, `VAR_IN_OUT` | то же | авто |
| `VAR` (статические ФБ) | `VAR` | авто |
| `VAR RETAIN` (в ФБ) | `VAR RETAIN` | проверка (`section.fb_retain`): по справке CODESYS RETAIN-переменная ФБ переносит в retain-память весь экземпляр, в S7 — только эти переменные (сверить с источником) |
| `VAR NON_RETAIN` | `VAR` | авто |
| `VAR DB_SPECIFIC` | `VAR` | проверка (`section.db_specific`): реманентность в S7 задаётся в экземпляре DB |
| `VAR_TEMP` в ФБ и OB | `VAR_TEMP` | авто |
| `VAR_TEMP` в FC | `VAR` | авто (у функции CODESYS временные — обычные `VAR`) |
| `VAR CONSTANT`, классический `CONST ... END_CONST` | `VAR CONSTANT` | авто |
| `VAR_INPUT` OB (стартовая информация: `Initial_Call`, `Remanence`, `LostRetentive`, ...) | `VAR` | проверка (`ob.start_info`): CODESYS их не заполняет |
| `Initial_Call` OB | эмуляция: `Initial_Call := NOT xS7convFirstCycleDone; xS7convFirstCycleDone := TRUE;` в начале тела | проверка (`ob.initial_call`) |
| атрибуты `InstructionName`, `LibVersion`, `S7_SetPoint` | опускаются | авто |
| `ExternalAccessible/Visible/Writable := 'False'` | опускаются | проверка (`decl.hmi_access`): видимость для HMI/OPC UA в CODESYS — символьная конфигурация |
| прочие атрибуты переменных | опускаются | проверка (`decl.attr`) |
| `x AT y : ...` (наложение) | — | TODO (`decl.at`): переписать через `UNION` или битовый доступ |
| имя — ключевое слово или оператор CODESYS (`time`, `max`, `R`, `S`, `ST`, `ret`, ...) | имя + `_` (`time_`) | проверка (`name.renamed`) |
| символы вне ASCII, пробелы в именах | транслитерация, `_` | авто (`name.sanitized`) |

## Типы данных

| S7 | CODESYS | Статус | Примечание |
|---|---|---|---|
| `Bool`, `Byte`, `Word`, `DWord`, `LWord` | `BOOL`, `BYTE`, `WORD`, `DWORD`, `LWORD` | авто | |
| `SInt`, `USInt`, `Int`, `UInt`, `DInt`, `UDInt`, `LInt`, `ULInt` | то же | авто | |
| `Real`, `LReal` | `REAL`, `LREAL` | авто | |
| `Time` | `TIME` | авто | в S7 TIME знаковый (DINT мс), в CODESYS — беззнаковый (UDINT мс): отрицательные литералы, вычитание и унарный минус → проверка (`lit.time_negative`, `expr.time_sub`) |
| `LTime` | `LTIME` | авто | |
| `S5Time` | `TIME` | проверка (`type.s5time`) | S5TIME — BCD с шагом базы времени, 10 мс…2h46m30s; литерал `S5T#2s` → `T#2s` |
| `Date` | `DATE` | авто | внутреннее представление разное (сутки от 1990 / секунды от 1970), на уровне языка — одинаково |
| `Time_Of_Day`, `TOD` | `TOD` | авто | |
| `Date_And_Time`, `DT` | `DT` | авто | в S7 DT хранит миллисекунды (BCD), в CODESYS DT — секунды: доли секунды теряются |
| `LDT`, `LTOD` | `LDT`, `LTOD` | проверка | поддержка в CODESYS 3.5.17 — сверить с источником |
| `String` | `STRING(254)` | авто (`type.string_default`) | длина по умолчанию в S7 — 254, в CODESYS — 80 |
| `String[n]`, `WString[n]` | `STRING(n)`, `WSTRING(n)` | авто | `WString` без длины → `WSTRING(254)` |
| `Char`, `WChar` | `STRING(1)`, `WSTRING(1)` | проверка (`type.char`) | в CODESYS нет типов CHAR/WCHAR |
| `Array[a..b, c..d] of T` | `ARRAY[a..b, c..d] OF T` | авто | границы-константы `#N` → `N` |
| `Array[*] of T` | `ARRAY[*] OF T` | проверка (`type.array_star`) | в CODESYS — только в `VAR_IN_OUT` |
| `"UDT_X"`, `"FB_X"` | `UDT_X`, `FB_X` | авто | тип не из корпуса → по имени, проверка (`type.unknown`) |
| `DTL` | — | TODO | структура S7 (YEAR, MONTH, ...); заменить на DT или свою структуру |
| `Variant`, `Any`, `Pointer`, `DB_ANY`, `Block_FB/FC/DB`, `REF_TO` | — | TODO | |
| `Timer`, `Counter` (S5) | — | TODO | заменить на TON/TOF/TP, CTU/CTD |
| `HW_*`, `OB_*`, `EVENT_*`, `CONN_*` и др. системные | — | TODO | |

## Функциональные блоки инструкций

| S7 | CODESYS (библиотека Standard) | Статус | Примечание |
|---|---|---|---|
| `TON_TIME`, `TOF_TIME`, `TP_TIME`, `TON`, `TOF`, `TP` | `TON`, `TOF`, `TP`; с `--timers s7compat` — `FB_S7Ton`, `FB_S7Tof`, `FB_S7Tp` (S7Compat) | авто (`fb.timer`, `fb.timer_s7compat`) | входы `IN`, `PT`, выходы `Q`, `ET` совпадают; см. «Слой совместимости S7Compat» |
| `TON_LTIME`, `TOF_LTIME`, `TP_LTIME` | `LTON`, `LTOF`, `LTP` | проверка (`fb.ltimer`) | наличие в Standard — сверить с источником |
| `TONR_TIME` | — | TODO | таймера с накоплением в Standard нет |
| `IEC_TIMER` (переменная или DB) | `TON`/`TOF`/`TP` по вызову `#t.TON(...)` / `"DB".TON(...)` | авто/проверка (`fb.generic`) | вызов `.TON(...)` → вызов экземпляра |
| `R_TRIG` | `R_TRIG` | авто | |
| `F_TRIG` | `F_TRIG`; с `--f-trig s7compat` — `FB_S7FTrig` (S7Compat) | проверка (`fb.f_trig`); с `s7compat` — авто (`fb.f_trig_s7compat`) | в S7 память фронта после запуска — FALSE, поэтому на первом вызове с `CLK = FALSE` спада нет. Даёт ли `F_TRIG` CODESYS Standard ложный спад на первом вызове (зависит от начального значения его памяти), не проверено — сверить с источником; первая строка сценария `FB_PumpAlternation/RotateOnStop` проверяет это в CODESYS. Корпус собирается со Standard `F_TRIG`, чтобы тест это показал; `FB_S7FTrig` готов на случай расхождения |
| `CTU`, `CTD`, `CTUD`, `CTU_INT`, `CTU_DINT`, ... | `CTU`, `CTD`, `CTUD` | проверка (`fb.counter`) | вход `R` → `RESET`, `LD` → `LOAD`; в CODESYS Standard `PV` и `CV` — WORD (0…65535), в S7 — тип счётчика (сверить с источником). Аргумент `PV` и присваивание `CV` переменной другого целого типа получают явное преобразование: `PV := INT_TO_WORD(x)`, `n := WORD_TO_INT(ctu.CV)` (`conv.instruction_type`) — без него CODESYS предупреждает о неявной смене знака |
| `SR`, `RS` | `SR`, `RS` | проверка (`fb.flipflop`) | `SR`: `S`/`R1`/`Q` → `SET1`/`RESET`/`Q1`; `RS`: `R`/`S1`/`Q` → `RESET1`/`SET`/`Q1` |
| `IEC_COUNTER` и варианты | `CTU`/`CTD`/`CTUD` по вызову | проверка | |

Вызов мультиэкземпляра `#inst(IN := x, PT := T#5s)` → `inst(IN := x, PT := T#5s)`; выходы `Q => #q` —
так же (`Q => q`). Параметры пользовательских ФБ и FC сопоставляются с их интерфейсом (имена после
переименования); параметр не из интерфейса → проверка (`call.param_unknown`). `EN`/`ENO` в вызове → TODO.

### Слой совместимости S7Compat

Рукописные объекты в папке проекта `S7Compat` (`src/POUs/S7Compat`, `src/GVLs/S7Compat`), не
генерируются; конвертер только проверяет, что нужные на месте (`s7conv build-corpus`), или копирует их
(`s7conv convert --emit-support`). Зависимости — `mapping.SUPPORT_DEPENDENCIES`.

| Объект | Нужен для | Семантика |
|---|---|---|
| `F_NormX`, `F_ScaleX` | `NORM_X`, `SCALE_X` | формулы Siemens без ограничения диапазоном (раздел «NORM_X и SCALE_X») |
| `FB_S7Ton`, `FB_S7Tof`, `FB_S7Tp` | таймеры при `--timers s7compat` | МЭК 61131-3 и S7 (описание — в объявлении каждого блока); время — `F_S7Now()`. `FB_S7Ton` копит прошедшее время по приращениям между вызовами с насыщением: при IN = TRUE дольше 2³² мс (≈ 49,7 суток) Q не падает (тест `KeepsQWhileInHeldAcrossWrap`) |
| `F_S7Now` | таймеры S7Compat | `TIME()`; при `GVL_S7Clock.xSimulation = TRUE` — моделируемые часы `GVL_S7Clock.tSimNow` |
| `GVL_S7Clock` | `F_S7Now` | `xSimulation`, `tSimNow` — меняют только тесты сценариев |
| `FB_S7FTrig` | `F_TRIG` при `--f-trig s7compat` | `Q = NOT CLK AND CLK прошлого вызова`, до первого вызова прошлое значение — FALSE |

Зачем таймеры S7Compat: тесты сценариев ставят часы на момент строки и проверяют поведение ровно на
пороге PT за один цикл ПЛК (выбор и сравнение с тестами в реальном времени — [methodology.md](methodology.md),
раздел 3). В рабочем приложении `xSimulation = FALSE`, и таймеры идут по тем же часам, что Standard;
совпадение со Standard проверяют тесты `MatchesStandardInRealTime`. Корпус собирается с
`--timers s7compat` (`s7conv build-corpus`), `s7conv convert` по умолчанию даёт таймеры Standard.

## Встроенные функции

| S7 | CODESYS | Статус | Примечание |
|---|---|---|---|
| `NORM_X(MIN := a, VALUE := v, MAX := b)` | `F_NormX(rMin := a, rValue := v, rMax := b)` | авто (`func.norm_x`) | см. «NORM_X и SCALE_X» |
| `SCALE_X(MIN := a, VALUE := v, MAX := b)` | `F_ScaleX(rMin := a, rValue := v, rMax := b)` | авто (`func.scale_x`) | результат в целую или битовую переменную или параметр (в S7 тип OUT задаёт цель) → `REAL_TO_<тип>(...)`, проверка (`func.scale_x_int`); так же `SCALE_X_<тип>` |
| `NORM_X_INT_REAL` и т. п. | как `NORM_X`/`SCALE_X` | проверка (`func.typed_variant`) | |
| `LIMIT(MN := a, IN := x, MX := b)` | `LIMIT(a, x, b)` | авто | операторы CODESYS не принимают именованные параметры — вызов приводится к позиционному. При MN > MX результат может различаться (по сведениям автора, S7 возвращает IN и ENO = FALSE, CODESYS по МЭК — `MIN(MAX(IN, MN), MX)` = MX) — сверить с источником |
| `MIN(IN1 := a, IN2 := b, ...)`, `MAX(...)` | `MIN(a, b, ...)`, `MAX(...)` | авто | |
| `SEL(G, IN0, IN1)`, `MUX(K, IN0, ...)` | то же позиционно | авто / `MUX` — проверка | вход `ELSE` у `MUX` не переносится |
| `ABS`, `SQRT`, `LN`, `LOG`, `EXP`, `SIN`, `COS`, `TAN`, `ASIN`, `ACOS`, `ATAN`, `TRUNC`, `EXPT` | то же | авто | |
| `SQR(x)` | `x * x` (операнд без вызовов функций); иначе `EXPT(x, 2.0)` | авто; с вызовом в операнде — проверка (`func.sqr`) | `x * x` точно повторяет SQR; результат `EXPT` CODESYS при отрицательном основании не проверен — сверить с источником |
| `ROUND(x)` | `REAL_TO_DINT(x)`; для LReal — `LREAL_TO_DINT(x)` (без сужения до REAL) | проверка (`func.round`) | правило округления половины (x.5) — сверить с источником; результат ограничен DINT |
| `CEIL`, `FLOOR`, `FRAC` | — | TODO | |
| `SHL(IN, N)`, `SHR`, `ROL`, `ROR` | то же позиционно | авто | |
| `CONCAT(IN1, IN2)`, `LEN(IN)`, `LEFT(IN, L)`, `RIGHT(IN, L)`, `MID(IN, L, P)`, `FIND`, `DELETE`, `INSERT`, `REPLACE` | то же позиционно | авто (`func.string`) | строковые функции CODESYS работают со STRING(255) |
| `X_TO_Y` (элементарные типы) | `X_TO_Y` | авто (`conv.std`) | |
| `REAL_TO_INT` и др. REAL → целое | то же | проверка (`conv.round`) | округление x.5 — сверить |
| `DWORD_TO_REAL`, `REAL_TO_DWORD`, `LWORD_TO_LREAL`, `LREAL_TO_LWORD` | то же | проверка (`conv.bitcast`) | в S7-1200/1500 переносится битовый образ, в CODESYS — числовое значение |
| `S5TI_TIM(x)`, `TIM_S5TI(x)`, `S5TIME_TO_TIME(x)` | `x` | проверка (`conv.s5time`) | S5TIME уже сопоставлен с TIME |
| `CHAR_TO_*`, `*_TO_CHAR`, `WORD_TO_BLOCK_DB`, BCD | — | TODO | BCD — `Util.BCD_TO_INT` (подключить вручную) |
| `TIME_TCK()` | `TIME()` | проверка (`func.time_tck`) | |
| `UPPER_BOUND`, `LOWER_BOUND` | то же | проверка (`func.bound`) | |
| `PEEK*`, `POKE*`, `MOVE_BLK`, `FILL_BLK`, `BLKMOV`, `RD_SYS_T`, `WR_SYS_T`, `RD_LOC_T`, `RUNTIME`, `T_ADD`, `T_DIFF`, `TypeOf`, `VariantGet`, `GET_ERROR`, `GEN_DIAG`, `S_ODT` и другие таймеры S5, ... | — | TODO (`func.unsupported`) | нет прямого аналога в CODESYS Standard |
| неизвестная функция без префикса | переносится как есть | проверка (`call.unknown`) | |

## Литералы

| S7 | CODESYS | Статус |
|---|---|---|
| `T#5s`, `TIME#1h30m` | `T#5s`, `T#1h30m` | авто |
| `T#-5s` | `T#-5s` | проверка: TIME в CODESYS беззнаковый |
| `LT#5s` | `LTIME#5s` | авто |
| `S5T#2s`, `S5TIME#200ms` | `T#2s`, `T#200ms` | проверка (`type.s5time`) |
| `D#2024-01-31`, `TOD#08:30:00`, `DT#2024-01-31-12:00:00` | то же (`DATE#` → `D#`, `TIME_OF_DAY#` → `TOD#`, `DATE_AND_TIME#` → `DT#`) | авто |
| `16#FF`, `2#1010`, `8#17` | то же | авто |
| `B#16#0F`, `W#16#FFFF`, `DW#16#...`, `LW#16#...` | `BYTE#16#0F`, `WORD#16#FFFF`, `DWORD#...`, `LWORD#...` | авто |
| `L#100` | `DINT#100` | авто |
| `INT#-5`, `REAL#1.5`, `BOOL#TRUE` | то же | авто |
| `'текст'` (экранирование `$`) | то же | авто |
| `WSTRING#'abc'` | `"abc"` | авто |
| `CHAR#'A'` | `'A'` | проверка |
| `C#5`, `P#M100.0 BYTE 16` | — | TODO |

## Выражения и операторы

| S7 | CODESYS | Статус |
|---|---|---|
| `#x` | `x` | авто |
| `&` | `AND` | авто |
| `a ** b` | `EXPT(a, b)` | авто; для целых операндов — проверка (`expr.power`) |
| `MOD`, `NOT`, `AND`, `OR`, `XOR`, сравнения | то же | авто; скобки расставляются по приоритетам МЭК |
| `a / b`, `a MOD b` для целых, битовых и TIME, делитель — не константа | то же | проверка (`expr.div_int`): делитель 0 в CODESYS — исключение и останов задачи, если в проекте нет функций неявной проверки `CheckDivDInt`/`CheckDivLInt`; в S7 CPU продолжает работу (результат и ENO — сверить с источником). Делитель-литерал, `VAR CONSTANT` и константа пользователя — авто |
| `a - b` для TIME, LTIME, TOD, DT, DATE; `-t` для TIME | то же | проверка (`expr.time_sub`): в S7 TIME со знаком, в CODESYS без знака — отрицательная разность переполняется (`t1 - t2 < T#0s` никогда не истинно) |
| `#s[i]` — символ строки (`String`, `WString`) | — | TODO (`expr.string_index`): в S7 — CHAR, нумерация с 1; в CODESYS индекс строки даёт BYTE (код символа), нумерацию сверить с источником; переписать через `MID`/`REPLACE` |
| `x += e`, `-=`, `*=`, `/=` | `x := x + e` (со скобками при необходимости) | авто |
| `x ?= e` | — | TODO |
| `#w.%X3` | `w.3` | авто |
| `#dw.%B1` (чтение) | `DWORD_TO_BYTE(SHR(dw, 8))` | проверка (`expr.slice_read`): нумерация срезов S7 — от младшей части (сверить с источником) |
| `#dw.%W0` (чтение) | `DWORD_TO_WORD(dw)` | проверка |
| запись в `.%B/.%W/.%D` | — | TODO (`expr.slice_write`) |
| `IF/ELSIF/ELSE`, `CASE` (списки, диапазоны `4..6`), `FOR ... BY`, `WHILE`, `REPEAT/UNTIL`, `EXIT`, `CONTINUE`, `RETURN` | то же (`END_IF` без `;`) | авто; пустой оператор `;` переносится как есть (с комментарием в строке), ветвь без операторов — `; // нет операторов` |
| `REGION Имя ... END_REGION` | `// REGION Имя` ... `// END_REGION Имя` | авто; прагма `{region}` CODESYS не используется: синтаксис для 3.5.17 не сверен |
| `GOTO`, метки | — | TODO |
| присваивание результата FC `#FC_X := ...` | `FC_X := ...` | авто |
| `ENO`, `EN`, `OK` | — | TODO |
| прагма в теле `{ ... }` | опускается | проверка |
| комментарии `//`, `(* *)` | переносятся (перед оператором, в конце строки) | авто |
| пустые строки между группами операторов | сохраняются | авто |

Длинные строки (больше 120 символов, правило STL003) переносятся: аргументы вызова — по одному на
строку с выравниванием по `(`, иначе — перед `AND`/`OR` верхнего уровня.

## Глобальные символы, теги, адреса

| S7 | CODESYS | Статус |
|---|---|---|
| `"DB".m` (глобальный DB) | `DB.m` (GVL с `qualified_only`) | авто |
| `"IDB".m`, `"IDB"(...)` | `GVL_InstanceDBs.IDB.m`, `GVL_InstanceDBs.IDB(...)` | авто; доступ к статическим (`VAR`) экземпляра снаружи — проверка (`access.fb_static`) |
| `"Тег"` с адресом из таблицы тегов | `GVL_IO.Тег` (`%I`, `%Q`) / `GVL_Markers.Тег` (`%M`) | авто |
| `"Тег"` без адреса (таблица тегов) | `GVL_Tags.Тег` с типом из таблицы | авто |
| константа пользователя (столбец `Value`) | `GVL_UserConstants.ИМЯ` (`VAR_GLOBAL CONSTANT`) | авто |
| `"X"`, которого нет ни в корпусе, ни в таблице тегов | `GVL_Tags.X`, тип выведен по использованию | проверка (`sym.unknown`); тип не вывести — TODO, принят BOOL |
| `"X".m`, где `X` — неизвестный DB | — | TODO (`sym.unknown_db`): добавить исходник DB |
| `%I0.0`, `%Q4.1`, `%M12.1` | переменная `I0_0 AT %IX0.0 : BOOL` (или тег с этим адресом) | авто |
| `%IB3`, `%IW64`, `%QW80`, `%MD20` | `IB3 AT %IB3`, `IW64 AT %IW32`, `QW80 AT %QW40`, `MD20 AT %MD5` | авто |
| `%MW11`, `%MD10` (не выровнены) | переменная без `AT` | проверка (`addr.unaligned`) |
| слово/двойное слово, перекрытое другими адресами | | проверка (`addr.overlap`): порядок байтов |
| `%IW272:P` (периферия), `%DB30.DBW0`, `%L`, `%T`, `%C` | — | TODO |

Таблица тегов — CSV из экспорта TIA Portal (столбцы `Name`, `Data Type`, `Logical Address`, `Comment`,
необязательный `Value`; разделитель `,`, `;` или TAB). Если к одному адресу обращаются и символьно, и
абсолютно (`"P101_ThermalOk"` и `%I0.2`), обе формы сводятся к одной переменной слоя ввода-вывода.

### Адресная модель

S7 адресует память **байтами**: `%MW10` — слово из байтов 10 и 11, `%MD10` — байты 10…13, порядок
байтов big-endian (старший байт — по младшему адресу). В CODESYS номер в `%MW`/`%MD` — номер **слова** и
**двойного слова**: `%MW5` — байты 10 и 11, `%MD2` — байты 8…11 (по справке CODESYS: D0 = B0…B3,
W0 = B0–B1, W1 = B2–B3), порядок байтов на x86/ARM — little-endian. Отсюда:

| S7 | Байты | CODESYS |
|---|---|---|
| `%I0.0` | бит 0 байта 0 | `%IX0.0` |
| `%IB3` | 3 | `%IB3` |
| `%IW64` | 64–65 | `%IW32` |
| `%MD20` | 20–23 | `%MD5` |
| `%MW11` | 11–12 | — (слово с нечётного байта не выражается) |

Битовые адреса совпадают при **байтовой** адресации битов. По справке CODESYS число перед точкой —
байт на устройствах с байтовой адресацией и слово — на устройствах со словной; для ПЛК210 и
CODESYS Control Win — сверить с источником (ожидается байтовая). `AT`-адреса в `GVL_IO` — заготовка:
на ПЛК210 каналы модулей обычно привязываются в дереве устройств (I/O mapping), а не через `AT`.

Смешанный доступ к одной области (`%MW10` и `%M10.0`) меняет смысл из-за порядка байтов: в S7
`%M10.0` — бит 8 слова `%MW10`, в CODESYS `%MX10.0` — бит 0 слова `%MW5`. Такие пары помечаются
`addr.overlap`.

## DB: реманентность и начальные значения

| S7 | CODESYS | Статус |
|---|---|---|
| `VAR RETAIN` в глобальном DB | `VAR_GLOBAL RETAIN` | авто (`db.retain`) |
| то же с `--retain persistent` | `VAR_GLOBAL PERSISTENT RETAIN` | проверка (`db.persistent`): постоянные переменные CODESYS объявляются в объекте Persistent Variables — сверить с источником |
| DB с `NON_RETAIN`, `VAR NON_RETAIN`, оптимизированный DB без `RETAIN` | `VAR_GLOBAL` | авто |
| стандартный DB (`S7_Optimized_Access := 'FALSE'`) без `NON_RETAIN` | `VAR_GLOBAL RETAIN` | проверка (`db.retain_standard`) |
| экземплярный DB | переменная в `GVL_InstanceDBs` (без RETAIN); `VAR RETAIN` самого ФБ остаётся в ФБ | авто |
| стандартный экземплярный или типизированный DB без `NON_RETAIN` (доступ экземплярного DB — как у его ФБ) | переменная в секции `VAR_GLOBAL RETAIN` (`PERSISTENT RETAIN` с `--retain persistent`) `GVL_InstanceDBs` | проверка (`db.retain_standard`): в S7 реманентен целиком, как стандартный глобальный DB |
| `BEGIN a := 5;` (глобальный DB) | начальное значение `a : INT := 5;` | авто |
| `BEGIN cfg.high := 16.0;` | `cfg : UDT_Cfg := (high := 16.0);` | авто |
| `BEGIN arr[1] := 0.5; arr[2] := 1.5;` | `arr : ARRAY[1..n] OF REAL := [0.5, 1.5];` | авто, если индексы подряд от нижней границы; иначе TODO (`db.begin_array`) |
| `BEGIN feedbackTime := T#5S;` (экземплярный DB) | `DB_P101 : FB_Motor := (feedbackTime := T#5S);` | авто; внутренние (не входы/выходы) — проверка (`db.begin_static`) |
| `BEGIN` типизированного DB | `DB : UDT := (поле := ...)` | авто |
| `READ_ONLY` | | проверка (`db.read_only`): запрет записи не переносится |

Смысл реманентности: в S7 реманентные данные переживают выключение питания и тёплый перезапуск и
сбрасываются при холодном пуске (сброс памяти). В CODESYS `RETAIN` переживает тёплый сброс и
выключение питания (если у ПЛК есть энергонезависимая память), но сбрасывается холодным сбросом и
полной загрузкой; `PERSISTENT` переживает и загрузку. Поведение конкретного ПЛК210 при сбросах —
сверить с документацией ОВЕН.

## OB и задачи

| S7 | CODESYS | Статус |
|---|---|---|
| OB1 «Main» (Program cycle; также OB ≥ 123 с «cycle» в имени) | PROGRAM в `MainTask`: циклическая 10 мс (`--main-task cyclic`, `--main-interval`), приоритет 15 | авто; номер не найден — проверка (`ob.main`) |
| OB30…OB38, OB с «cyclic» в имени | PROGRAM в задаче `Task_OB<n>` (или `Task_<период>ms`) с периодом OB | авто, если период из `--ob-config` или из имени/заголовка («100ms», «0,5 s»); период по умолчанию — проверка (`ob.cyclic`) |
| OB100 «Startup» | PROGRAM, первым в `MainTask`; тело выполняется один раз по флагу `xS7convStartupDone` | проверка (`ob.startup`) |
| OB10…OB17, OB20…OB23, OB40…OB47, OB8x, OB121/122 и прочие | PROGRAM без задачи | TODO (`ob.event`): задачу по событию создать вручную |

Номер OB во внешнем источнике TIA не выгружается. Порядок поиска: `--ob-config` (или `ob_config.json`
во входном каталоге), `OB<n>` в имени или заголовке, стандартные имена TIA («Main» → 1, «Startup» → 100,
«Cyclic interrupt» → 30). Период: `--ob-config`, подсказка в имени/заголовке/комментарии, значения
S7-300/400 по умолчанию (OB30 5 с, OB31 2 с, OB32 1 с, OB33 500 мс, OB34 200 мс, OB35 100 мс, OB36 50 мс,
OB37 20 мс, OB38 10 мс — сверить с конфигурацией CPU), иначе 100 мс.

Приоритеты: шкала S7 (больше — важнее) и CODESYS (0 — важнее всего) обратные. Циклическим задачам
приоритет назначается по периоду (короче период — выше приоритет: 1, 2, ...), `MainTask` — 15:
циклические прерывания вытесняют главный цикл, как в S7.

Почему OB100 — флаг первого цикла, а не `FB_init` или системное событие: `FB_init` есть только у ФБ, а
код OB100 — программа; системные события задач CODESYS зависят от рантайма. Флаг — переменная не RETAIN:
её сбрасывают загрузка приложения, Reset warm/cold и перезапуск ПЛК. **Команда Stop → Start CODESYS флаг
не сбрасывает** (остановка задач не инициализирует переменные), а в S7 OB100 выполняется при каждом
переходе STOP → RUN, и нереманентные данные при этом получают начальные значения. Код OB100 после
Stop → Start CODESYS не выполнится; если это важно, сброс флага по системному событию задачи — ручной
шаг (пометка `ob.startup`; то же для эмуляции `Initial_Call`, пометка `ob.initial_call`). Второе
ограничение: задачи с более высоким приоритетом могут выполниться раньше первого цикла `MainTask` — если
они зависят от инициализации, им нужна проверка флага (в S7 циклические прерывания стартуют только после
OB100).

Куда пишутся задачи. `s7conv convert` пишет `tasks.json` рядом с раскладкой (формат ниже).
`s7conv build-corpus` пишет задачи корпуса прямо в `tools/codesys/config.json` — ключ
`modes.normal.tasks` (`name`, `interval_ms`, `priority`, `pous`), остальной текст файла не меняется;
по нему `tools/codesys/cds.py import` создаёт задачи рабочего проекта. Для корпуса это `MainTask` 10 мс
(приоритет 15: `PRG_Startup`, `PRG_Main`) и `Task_OB30` 100 мс (приоритет 1: `PRG_Cyclic_interrupt`);
`PRG_Diagnostic_error_interrupt` (OB82) — без задачи, вручную. Тестовый режим (`modes.test`) не
меняется: `TestTask` 10 мс → `PRG_Tests`.

Формат `tasks.json`:

```json
{
  "generator": "s7conv 0.1.0",
  "tasks": [
    {"name": "MainTask", "type": "cyclic", "interval_ms": 10, "priority": 15,
     "pous": ["PRG_Startup", "PRG_Main"], "sources": ["Startup (OB100)", "Main (OB1)"]},
    {"name": "Task_OB30", "type": "cyclic", "interval_ms": 100, "priority": 1,
     "pous": ["PRG_Cyclic_interrupt"], "sources": ["Cyclic interrupt (OB30)"]}
  ],
  "obs": [{"name": "...", "program": "...", "number": 30, "number_origin": "ob-config", "kind": "cyclic",
           "task": "Task_OB30", "interval_ms": 100, "interval_origin": "ob-config", "file": "...", "line": 1,
           "notes": []}],
  "manual": ["PRG_Diagnostic_error_interrupt: ... — задача по событию не создаётся автоматически, настроить вручную"]
}
```

`type` — `cyclic` или `freewheeling`; `interval_ms` задан всегда: `tools/codesys/import_sources.py`
читает из каждой задачи `name`, `interval_ms`, `priority`, `pous` (ключ `tasks` режима в
`tools/codesys/config.json`) и создаёт циклические задачи — свободный цикл (`freewheeling`) там нужно
выставить вручную. Формат `--ob-config`:
`{"Имя OB": {"number": 30, "kind": "main|cyclic|startup|event", "interval_ms": 100, "priority": 3, "task": "FastTask"}}`.

## NORM_X и SCALE_X

Функции поддержки `F_NormX` и `F_ScaleX` (`src/POUs/S7Compat/F_NormX`, `src/POUs/S7Compat/F_ScaleX`)
написаны вручную и не генерируются; `s7conv convert --emit-support` копирует их в результат. Тесты CfUnit —
`tests/POUs/S7Compat/FB_F_NormX_Test`, `tests/POUs/S7Compat/FB_F_ScaleX_Test` (ожидаемые значения посчитаны по формулам
Siemens, это проверяет `s7conv/tests/test_support_functions.py`).

| | S7 (по документации) | CODESYS (`F_NormX` / `F_ScaleX`) |
|---|---|---|
| Формула NORM_X | `OUT = (VALUE - MIN) / (MAX - MIN)` | та же |
| Формула SCALE_X | `OUT = VALUE * (MAX - MIN) + MIN` | та же |
| VALUE вне MIN…MAX (NORM_X) | OUT линейно продолжается ниже 0.0 / выше 1.0, ENO = TRUE | так же, без ограничения |
| VALUE < 0.0 или > 1.0 (SCALE_X) | OUT линейно продолжается за MIN/MAX, ENO = TRUE | так же |
| OUT вне диапазона целого типа (SCALE_X) | ENO = FALSE, в OUT — «младшая часть» результата | `REAL_TO_<тип>` CODESYS — поведение при переполнении другое, сверить с источником |
| MIN ≥ MAX | ENO = FALSE; значение OUT не документировано (форум Siemens: границы меняются местами) | MIN > MAX — та же формула без перестановки; MIN = MAX: NORM_X → 0.0 (деления на ноль нет), SCALE_X → MIN. **Сверить с источником** |
| NaN на входе | ENO = FALSE | результат NaN (NORM_X при NaN в границах → 0.0) |
| Типы | NORM_X: MIN, VALUE, MAX — один тип (целые или вещественные), OUT — REAL/LREAL; SCALE_X: VALUE — REAL/LREAL, MIN, MAX, OUT — один тип | все параметры REAL; целые аргументы приводятся неявно, целый результат — `REAL_TO_<тип>` с пометкой |
| ENO | есть | не воспроизводится (вызовы с `ENO` — TODO) |

Номинальный диапазон аналоговых модулей S7 — 0…27648 (0…20 мА, 0…10 В, 4…20 мА); диапазоны
перегрузки (до 32511) и недогрузки (для 4…20 мА — до −4864) — сверить с руководством на конкретный
модуль. Типовой код S7
`NORM_X(MIN := 0, VALUE := raw, MAX := 27648)` переводится без изменений смысла; проверка достоверности
по NAMUR NE 43 остаётся задачей прикладного кода.

Источники: руководство S7-1200 System Manual, раздел «SCALE_X (Scale) and NORM_X (Normalize)»
([Siemens, A5E02486680, 03/2014](https://support.industry.siemens.com/cs/attachments/91696622/s71200_system_manual_en-US_en-US.pdf)) —
формулы, типы и поведение вне диапазона; PDF не удалось прочитать целиком при подготовке, текст
раздела сверялся по пересказам: [InstrumentationTools](https://instrumentationtools.com/scale-and-normalize-instructions-in-plc/)
(поведение вне диапазона, ENO), [PLCspace](https://sklep-plcspace.pl/en/blog/plc-siemens-instrukcja-scale-x/)
(условия ENO = FALSE для SCALE_X), [форум Siemens, тема 195505](https://support.industry.siemens.com/tf/WW/en/posts/norm-x-and-scale-x-bug-but-very-small/195505)
(поведение при MAX < MIN — сообщение пользователя). Перед вводом в эксплуатацию сверить с
TIA Portal Information System (F1 на инструкции) для своей версии.

## Не поддерживается (MIGRATION-TODO)

| Конструкция | Причина и что делать |
|---|---|
| `GOTO`, метки | переходов в выгрузке TIA быть не должно; переписать структурно |
| `AT`-наложения | `UNION` или битовые операции |
| `Variant`, `Any`, `Pointer`, `DB_ANY`, `REF_TO`, `TypeOf`, `VariantGet/Put` | переписать на `POINTER TO`/`REFERENCE TO` или перегрузку по типу |
| `DTL` | DT или своя структура |
| `PEEK`/`POKE`, `%DB30.DBW0`, `WORD_TO_BLOCK_DB(...).DW[...]` | абсолютная адресация DB — заменить символьной |
| `BLKMOV`, `MOVE_BLK`, `FILL_BLK`, `P#...` | `MEMCPY`/`MEMSET` из `SysMem` или цикл |
| `RD_SYS_T`, `WR_SYS_T`, `RD_LOC_T`, `T_ADD`, `T_DIFF`, `RUNTIME` | `SysTime`/`SysTimeRtc` (CAA), `TIME()` |
| `S_ODT` и таймеры/счётчики S5, теги `%T`, `%C` | TON/TOF/TP, CTU |
| `TONR_TIME` | свой ФБ накопления |
| `ENO`, `EN`, `OK` | обработку ошибок перенести явно |
| `%IW272:P` | в CODESYS — образ процесса задачи; при необходимости — опция «Always update variables» модуля |
| событийные OB (прерывания, ошибки) | задача по событию или обработчик рантайма — вручную |
| запись в срезы `.%B/.%W/.%D`, `?=`, `CEIL`, `FLOOR`, `FRAC` | маска и сдвиг; явный код |
| символ строки по индексу `#s[i]` | `MID(s, 1, i)` для чтения, `REPLACE` для записи — учесть тип (CHAR → STRING(1)) |
| неразобранные операторы | см. [GRAMMAR.md](GRAMMAR.md) |

## Расхождения, которые конвертер не помечает

Конвертер помечает то, что видно по тексту одной конструкции. Расхождения ниже зависят от данных во
время работы или от настроек проекта, и пометка на каждой арифметической операции утопила бы остальные.
Их закрывают решением на уровне проекта (чек-лист [methodology.md](methodology.md), раздел 4) и тестами.
Всё в этой таблице — по сведениям автора, **сверить с источником** для своей версии TIA Portal и CODESYS.

| Что | S7 | CODESYS | Что делать |
|---|---|---|---|
| Разрядность промежуточного результата целой арифметики | вычисление в типе операндов: `Int * Int` переполняется в Int, даже если результат присваивается DInt | промежуточные результаты — в разрядности регистра (не меньше 32 бит): `INT * INT`, присвоенное DINT, не переполняется | выражения, где переполнение возможно или нарочно используется (счётчики с переходом через ноль), переписать с явными `*_TO_*`; проверить сценариями |
| Индекс массива вне границ | ошибка программирования: OB121 или STOP CPU (S7-1500) | без проверки — запись в чужую память; проверка — функция неявной проверки `CheckBounds` | подключить `CheckBounds` на время наладки или ограничить индексы явно |
| Деление REAL на 0 | результат ±INF/NaN, ENO = FALSE | ±INF/NaN или исключение FPU — зависит от платформы; функции неявной проверки `CheckDivReal`/`CheckDivLReal` | делители проверять явно (как `FB_PIController` корпуса) |
| Значение счётчика FOR после цикла, вычисление конечного значения и шага | переносится дословно | то же | не использовать счётчик после цикла и не менять границы внутри; конечное значение, равное максимуму типа счётчика, в CODESYS даёт бесконечный цикл (справка CODESYS, FOR) |
| Неявные преобразования типов | без проверки IEC SCL допускает, например, Int ↔ Word, DInt → Int | часть — с предупреждением (смена знака, потеря данных), BOOL ↔ число и TIME ↔ число — ошибка компиляции (сверить) | разобрать предупреждения сборки CODESYS, ошибки — явными `*_TO_*` |
| Обновление выходов IEC-таймера | S7-1500 обновляет Q/ET и при обращении к ним вне вызова (сверить) | только при вызове | читать Q/ET сразу после вызова (так написан корпус) |

## Пометки MIGRATION-CHECK — сводка правил

`type.s5time`, `type.char`, `type.array_star`, `type.unknown`, `fb.counter`, `fb.ltimer`, `fb.f_trig`, `fb.flipflop`,
`fb.generic`, `func.round`, `func.scale_x_int`, `func.typed_variant`, `func.time_tck`, `func.bound`, `func.sqr`,
`conv.round`, `conv.bitcast`, `conv.s5time`, `lit.time_negative`, `lit.char`, `expr.power`, `expr.time_sub`,
`expr.div_int`, `expr.slice_read`, `call.unknown`, `call.param_unknown`, `call.member`, `call.instance_unknown`,
`decl.hmi_access`, `decl.attr`, `name.renamed`, `name.undeclared`, `name.plain`, `sym.unknown`,
`sym.unknown_decl`, `addr.unaligned`, `addr.overlap`, `access.fb_static`, `access.db_member`,
`db.retain_standard`, `db.persistent`, `db.read_only`, `db.implicit_instance`, `db.begin_static`,
`db.begin_member`, `block.non_optimized`, `block.know_how`, `section.db_specific`, `section.fb_retain`, `ob.start_info`,
`ob.initial_call`, `ob.startup`, `ob.cyclic`, `ob.main`, `stmt.pragma`. Расшифровка — в отчёте
конвертации (столбец «Что») и в тексте пометок.

## Источники

- Siemens, S7-1200 Programmable Controller System Manual (A5E02486680), раздел «SCALE_X and NORM_X»:
  <https://support.industry.siemens.com/cs/attachments/91696622/s71200_system_manual_en-US_en-US.pdf>.
- CODESYS Online Help, «Operands and addresses» (адресная модель, перекрытие областей):
  <https://content.helpme-codesys.com/en/CODESYS%20Development%20System/_cds_operands_addresses.html>.
- CODESYS Online Help, «Region pragma» (почему REGION переносится комментарием):
  <https://content.helpme-codesys.com/en/CODESYS%20Development%20System/_cds_pragma_region.html>.
- Пересказы раздела Siemens о NORM_X/SCALE_X и форум Siemens — см. «NORM_X и SCALE_X».
- Сигнатуры CODESYS Standard (TON/TOF/TP, CTU/CTD/CTUD, SR/RS) — по библиотеке Standard 3.5;
  WORD-тип `PV`/`CV` счётчиков — сверить с источником (см. также `tools/README.md`, замена R12).
