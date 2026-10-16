# Отчёт конвертации SCL → ST CODESYS

Сгенерирован `s7conv 0.1.0` — не редактировать вручную, пересоздаётся командой
`s7conv report` (см. README). Вход: `s7conv/tests/fixtures`.

Единица учёта — **конструкция**: блок S7, объявление переменной или оператор (вложенные
операторы считаются отдельно). Статусы: **автоматически** — переведено без замечаний;
**требует проверки** — переведено, в коде пометка `// MIGRATION-CHECK: причина`;
**не поддерживается** — не переведено, в коде `// MIGRATION-TODO: причина` и закомментированный
исходный текст. Правила соответствия — [MAPPING.md](MAPPING.md), подмножество SCL —
[GRAMMAR.md](GRAMMAR.md).

## Итог

| Показатель | Значение |
|---|---:|
| Файлов SCL | 4 |
| Блоков S7 | 15 |
| Конструкций | 142 |
| Автоматически | 111 (78 %) |
| Требуют проверки | 18 (13 %) |
| Не поддерживаются | 13 (9 %) |

### По видам конструкций

| Вид | Всего | Автоматически | Требуют проверки | Не поддерживаются |
|---|---:|---:|---:|---:|
| Блоки | 15 | 11 | 3 | 1 |
| Объявления | 62 | 51 | 6 | 5 |
| Операторы | 65 | 49 | 9 | 7 |

## По файлам

| Файл | Блоков | Конструкций | Автоматически | Требуют проверки | Не поддерживаются | Авто, % |
|---|---:|---:|---:|---:|---:|---:|
| `s7conv/tests/fixtures/analog.scl` | 3 | 27 | 24 | 3 | 0 | 89 % |
| `s7conv/tests/fixtures/main.scl` | 6 | 21 | 20 | 1 | 0 | 95 % |
| `s7conv/tests/fixtures/motor.scl` | 3 | 46 | 45 | 1 | 0 | 98 % |
| `s7conv/tests/fixtures/unsupported.scl` | 3 | 37 | 13 | 11 | 13 | 35 % |
| `(проект: слой ввода-вывода, теги, экземпляры DB)` | 0 | 11 | 9 | 2 | 0 | 82 % |
| **Итого** | 15 | 142 | 111 | 18 | 13 | 78 % |

## Задачи CODESYS (из OB)

| Задача | Тип | Период, мс | Приоритет | POU (порядок вызова) | OB S7 |
|---|---|---:|---:|---|---|
| MainTask | cyclic | 10 | 15 | PRG_Startup, PRG_Main | Startup (OB100); Main (OB1) |
| Task_100ms | cyclic | 100 | 1 | PRG_Cyclic_interrupt_100ms | Cyclic interrupt 100ms (OB?) |

OB без задачи (настроить вручную): `PRG_Hardware_interrupt`.

Задачи записываются в `tasks.json` рядом с раскладкой (формат — MAPPING.md, «OB и задачи»).

## Слой совместимости S7Compat

Режимы: таймеры TON/TOF/TP — `standard`, F_TRIG — `standard` (`standard` — библиотека
Standard CODESYS, `s7compat` — рукописные ФБ с семантикой S7; [MAPPING.md](MAPPING.md),
«Слой совместимости S7Compat»).

Сконвертированный код вызывает рукописные объекты (не генерируются, лежат в `src/*/S7Compat`): `F_NormX`, `F_ScaleX`. Конструкции, переведённые через них, считаются «автоматически»: их поведение задают описания в
объявлениях этих объектов и тесты `tests/POUs/S7Compat`, результат прогона в CODESYS —
[TEST_REPORT.md](TEST_REPORT.md).

## Не поддерживается — причины

| Правило | Что | Пометок |
|---|---|---:|
| `type.unsupported` | тип S7 без аналога | 3 |
| `parse.stmt` | оператор не разобран | 2 |
| `addr.unsupported` | адрес не I/Q/M | 1 |
| `decl.at` | AT (наложение) | 1 |
| `func.unsupported` | функция S7 без аналога | 1 |
| `ob.event` | событийный OB | 1 |
| `parse.decl` | объявление не разобрано | 1 |
| `stmt.goto` | GOTO | 1 |
| `stmt.label` | метка перехода | 1 |
| `sym.unknown_db` | DB не найден в корпусе | 1 |

## Требует проверки — причины

| Правило | Что | Пометок |
|---|---|---:|
| `db.implicit_instance` | экземплярный DB выведен по вызову | 2 |
| `block.non_optimized` | неоптимизированный доступ | 1 |
| `conv.bitcast` | DWORD↔REAL: битовый образ | 1 |
| `expr.power` | ** → EXPT для целых | 1 |
| `expr.slice_read` | чтение среза .%B/.%W/.%D | 1 |
| `fb.counter` | счётчики CTU/CTD/CTUD (WORD) | 1 |
| `func.round` | ROUND → REAL_TO_DINT | 1 |
| `func.scale_x_int` | SCALE_X с целым результатом | 1 |
| `lit.time_negative` | отрицательный TIME | 1 |
| `name.renamed` | переименование (ключевое слово) | 1 |
| `name.undeclared` | необъявленная переменная | 1 |
| `ob.startup` | OB100 → флаг первого цикла | 1 |
| `section.db_specific` | реманентность DB_SPECIFIC | 1 |
| `section.fb_retain` | VAR RETAIN в ФБ: весь экземпляр | 1 |
| `sym.unknown` | символ не найден → GVL_Tags | 1 |
| `sym.unknown_decl` | тип символа выведен | 1 |
| `type.char` | Char → STRING(1) | 1 |
| `type.s5time` | S5Time → TIME | 1 |

## Подробно по файлам

### `s7conv/tests/fixtures/analog.scl`

Конструкций 27: автоматически 24, требуют проверки 3, не поддерживаются 0.

Блоки: FUNCTION «FC_ScaleAnalog» → `FC_ScaleAnalog`; DATA_BLOCK «DB_Settings» → `DB_Settings`; FUNCTION_BLOCK «FB_Level» → `FB_Level`.

| Строка | Статус | Блок | Правило | Причина |
|---:|---|---|---|---|
| 38 | ! требует проверки | DB_Settings | `type.s5time` | S5Time → TIME: в S7 S5TIME — BCD с шагом 10 мс…10 с, диапазон до 2h46m30s |
| 66 | ! требует проверки | FB_Level | `func.scale_x_int` | SCALE_X с целым OUT: REAL_TO_INT округляет — сверить с S7 |
| 69 | ! требует проверки | FB_Level | `sym.unknown` | символ "Alarm_Lamp" не найден в корпусе и таблице тегов — объявлен в GVL_Tags |

### `s7conv/tests/fixtures/main.scl`

Конструкций 21: автоматически 20, требуют проверки 1, не поддерживаются 0.

Блоки: ORGANIZATION_BLOCK «Main» → `PRG_Main`; ORGANIZATION_BLOCK «Cyclic interrupt 100ms» → `PRG_Cyclic_interrupt_100ms`; ORGANIZATION_BLOCK «Startup» → `PRG_Startup`; DATA_BLOCK «DB_Hmi» → `DB_Hmi`; DATA_BLOCK «Delay_DB» → `GVL_InstanceDBs.Delay_DB`; DATA_BLOCK «Level_DB» → `GVL_InstanceDBs.Level_DB`.

| Строка | Статус | Блок | Правило | Причина |
|---:|---|---|---|---|
| 34 | ! требует проверки | Startup | `ob.startup` | OB100 (Startup) → однократное выполнение по флагу первого цикла в MainTask: флаг (не RETAIN) сбрасывается загрузкой, Reset warm/cold и перезапуском ПЛК, но не командой Stop → Start CODESYS (в S7 OB100 выполняется при каждом STOP → RUN); задачи с более высоким приоритетом могут выполниться раньше |

### `s7conv/tests/fixtures/motor.scl`

Конструкций 46: автоматически 45, требуют проверки 1, не поддерживаются 0.

Блоки: TYPE «UDT_MotorCmd» → `UDT_MotorCmd`; FUNCTION_BLOCK «FB_Motor» → `FB_Motor`; DATA_BLOCK «Motor1_DB» → `GVL_InstanceDBs.Motor1_DB`.

| Строка | Статус | Блок | Правило | Причина |
|---:|---|---|---|---|
| 46 | ! требует проверки | FB_Motor | `section.fb_retain` | VAR RETAIN в ФБ: в CODESYS при RETAIN-переменной в retain-памяти хранится весь экземпляр ФБ, в S7 — только эти переменные (сверить с источником) |

### `s7conv/tests/fixtures/unsupported.scl`

Конструкций 37: автоматически 13, требуют проверки 11, не поддерживаются 13.

Блоки: FUNCTION_BLOCK «FB_Legacy» → `FB_Legacy`; FUNCTION_BLOCK «FB_Broken» → `FB_Broken`; ORGANIZATION_BLOCK «Hardware interrupt» → `PRG_Hardware_interrupt`.

| Строка | Статус | Блок | Правило | Причина |
|---:|---|---|---|---|
| 2 | ! требует проверки | FB_Legacy | `block.non_optimized` | стандартный (неоптимизированный) доступ S7: абсолютная адресация и порядок байтов не переносятся |
| 6 | ✕ не поддерживается | FB_Legacy | `type.unsupported` | Variant — нет аналога в CODESYS; переписать (ANY, POINTER или перегрузка) |
| 7 | ✕ не поддерживается | FB_Legacy | `type.unsupported` | DTL — структура S7 (YEAR, MONTH, ...), в CODESYS нет; заменить на DT или свою структуру |
| 8 | ! требует проверки | FB_Legacy | `name.renamed` | имя «time» переименовано в «time_» (ключевое слово CODESYS или повтор) |
| 12 | ✕ не поддерживается | FB_Legacy | `decl.at` | AT (наложение переменных S7) — переписать через UNION или битовый доступ |
| 13 | ! требует проверки | FB_Legacy | `fb.counter` | счётчик S7 → CTU (CODESYS Standard): PV и CV — WORD (0…65535), в S7 — тип счётчика; проверить диапазон |
| 15 | ! требует проверки | FB_Legacy | `type.char` | Char → STRING(1): в CODESYS нет типа CHAR, сравнения и CHAR_TO_* проверить |
| 17 | ✕ не поддерживается | FB_Legacy | `type.unsupported` | TONR (таймер с накоплением) — в CODESYS Standard нет |
| 19 | ! требует проверки | FB_Legacy | `section.db_specific` | реманентность задаётся в экземпляре DB (DB_SPECIFIC) — объявлено VAR |
| 26 | ✕ не поддерживается | FB_Legacy | `stmt.goto` | GOTO — переходы не переносятся (переписать структурно) |
| 28 | ✕ не поддерживается | FB_Legacy | `func.unsupported` | PEEK_WORD: нет прямого аналога в CODESYS Standard |
| 29 | ! требует проверки | FB_Legacy | `expr.slice_read` | срез .%B1 → WORD_TO_BYTE(SHR(...)): нумерация срезов S7 от младшей части — сверить с источником |
| 30 | ✕ не поддерживается | FB_Legacy | `parse.stmt` | оператор не разобран: ожидалось ';', найдено 'ENO' |
| 33 | ! требует проверки | FB_Legacy | `func.round` | ROUND → REAL_TO_DINT: правило округления половины (x.5) сверить с источником |
| 34 | ✕ не поддерживается | FB_Legacy | `addr.unsupported` | адрес %DB1.DBX0.0 не поддерживается (только %I, %Q, %M) |
| 35 | ! требует проверки | FB_Legacy | `lit.time_negative` | отрицательный TIME: в CODESYS TIME беззнаковый (UDINT мс) |
| 39 | ! требует проверки | FB_Legacy | `conv.bitcast` | REAL_TO_DWORD: в S7-1200/1500 переносится битовый образ, в CODESYS — числовое значение |
| 40 | ! требует проверки | FB_Legacy | `expr.power` | ** → EXPT: тип результата для целых операндов сверить (в S7 — REAL/LREAL) |
| 41 | ✕ не поддерживается | FB_Legacy | `stmt.label` | метка перехода — переходы не переносятся |
| 42 | ✕ не поддерживается | FB_Legacy | `sym.unknown_db` | DB "Unknown_DB" не найден в корпусе — добавьте его исходник |
| 43 | ✕ не поддерживается | FB_Legacy | `parse.stmt` | оператор не разобран: ожидалось выражение, найдено ':=' |
| 49 | ✕ не поддерживается | FB_Broken | `parse.decl` | объявление не разобрано: ожидалось ';', найдено 'END_VAR' |
| 52 | ! требует проверки | FB_Broken | `name.undeclared` | #a не объявлена в блоке |
| 55 | ✕ не поддерживается | Hardware interrupt | `ob.event` | номер OB не определён: событийный OB — задача по событию не создаётся, настроить вручную |
| 58 | ! требует проверки | Hardware interrupt | `db.implicit_instance` | экземплярный DB "FB_Legacy_DB" не найден в корпусе — создан в GVL_InstanceDBs с типом FB_Legacy |

### `(проект: слой ввода-вывода, теги, экземпляры DB)`

Конструкций 11: автоматически 9, требуют проверки 2, не поддерживаются 0.

| Строка | Статус | Блок | Правило | Причина |
|---:|---|---|---|---|
| — | ! требует проверки | FB_Legacy_DB | `db.implicit_instance` | экземплярный DB FB_Legacy_DB выведен по вызову (исходника DB в корпусе нет) |
| — | ! требует проверки | Alarm_Lamp | `sym.unknown_decl` | символ "Alarm_Lamp" не найден — тип BOOL выведен по использованию (s7conv/tests/fixtures/analog.scl:69) |
