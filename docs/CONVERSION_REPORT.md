# Отчёт конвертации SCL → ST CODESYS

Сгенерирован `s7conv 0.1.0` — не редактировать вручную, пересоздаётся командой
`s7conv build-corpus` (см. README). Вход: `samples/scl`.

Единица учёта — **конструкция**: блок S7, объявление переменной или оператор (вложенные
операторы считаются отдельно). Статусы: **автоматически** — переведено без замечаний;
**требует проверки** — переведено, в коде пометка `// MIGRATION-CHECK: причина`;
**не поддерживается** — не переведено, в коде `// MIGRATION-TODO: причина` и закомментированный
исходный текст. Правила соответствия — [MAPPING.md](MAPPING.md), подмножество SCL —
[GRAMMAR.md](GRAMMAR.md).

## Итог

| Показатель | Значение |
|---|---:|
| Файлов SCL | 20 |
| Блоков S7 | 44 |
| Конструкций | 998 |
| Автоматически | 942 (94 %) |
| Требуют проверки | 26 (3 %) |
| Не поддерживаются | 30 (3 %) |

### По видам конструкций

| Вид | Всего | Автоматически | Требуют проверки | Не поддерживаются |
|---|---:|---:|---:|---:|
| Блоки | 44 | 36 | 7 | 1 |
| Объявления | 421 | 402 | 12 | 7 |
| Операторы | 533 | 504 | 7 | 22 |

## По файлам

| Файл | Блоков | Конструкций | Автоматически | Требуют проверки | Не поддерживаются | Авто, % |
|---|---:|---:|---:|---:|---:|---:|
| `samples/scl/DB_Plant.scl` | 22 | 72 | 69 | 2 | 1 | 96 % |
| `samples/scl/FB_AlarmDelay.scl` | 1 | 40 | 40 | 0 | 0 | 100 % |
| `samples/scl/FB_AnalogIn.scl` | 1 | 71 | 71 | 0 | 0 | 100 % |
| `samples/scl/FB_BatchCounter.scl` | 1 | 36 | 32 | 4 | 0 | 89 % |
| `samples/scl/FB_Debounce.scl` | 1 | 28 | 23 | 5 | 0 | 82 % |
| `samples/scl/FB_EventLogger.scl` | 1 | 60 | 53 | 1 | 6 | 88 % |
| `samples/scl/FB_LegacyTelegram.scl` | 1 | 45 | 26 | 3 | 16 | 58 % |
| `samples/scl/FB_ModeSelect.scl` | 1 | 43 | 42 | 1 | 0 | 98 % |
| `samples/scl/FB_Motor.scl` | 1 | 64 | 64 | 0 | 0 | 100 % |
| `samples/scl/FB_PIController.scl` | 1 | 49 | 49 | 0 | 0 | 100 % |
| `samples/scl/FB_PumpAlternation.scl` | 1 | 59 | 58 | 1 | 0 | 98 % |
| `samples/scl/FB_Ramp.scl` | 1 | 32 | 32 | 0 | 0 | 100 % |
| `samples/scl/FB_Sequencer.scl` | 1 | 80 | 80 | 0 | 0 | 100 % |
| `samples/scl/FB_Totalizer.scl` | 1 | 39 | 38 | 1 | 0 | 97 % |
| `samples/scl/FB_Valve.scl` | 1 | 75 | 73 | 2 | 0 | 97 % |
| `samples/scl/FC_Statistics.scl` | 1 | 40 | 40 | 0 | 0 | 100 % |
| `samples/scl/OB_Cyclic.scl` | 1 | 15 | 13 | 2 | 0 | 87 % |
| `samples/scl/OB_Main.scl` | 1 | 68 | 63 | 2 | 3 | 93 % |
| `samples/scl/OB_Startup.scl` | 2 | 25 | 19 | 2 | 4 | 76 % |
| `samples/scl/UDT_PlantTypes.scl` | 3 | 24 | 24 | 0 | 0 | 100 % |
| `(проект: слой ввода-вывода, теги, экземпляры DB)` | 0 | 33 | 33 | 0 | 0 | 100 % |
| **Итого** | 44 | 998 | 942 | 26 | 30 | 94 % |

## Задачи CODESYS (из OB)

| Задача | Тип | Период, мс | Приоритет | POU (порядок вызова) | OB S7 |
|---|---|---:|---:|---|---|
| MainTask | cyclic | 10 | 15 | PRG_Startup, PRG_Main | Startup (OB100); Main (OB1) |
| Task_OB30 | cyclic | 100 | 1 | PRG_Cyclic_interrupt | Cyclic interrupt (OB30) |

OB без задачи (настроить вручную): `PRG_Diagnostic_error_interrupt`.

Задачи записываются в `tools/codesys/config.json` (режим normal, `modes.normal.tasks`) (формат — MAPPING.md, «OB и задачи»).

## Слой совместимости S7Compat

Режимы: таймеры TON/TOF/TP — `s7compat`, F_TRIG — `standard` (`standard` — библиотека
Standard CODESYS, `s7compat` — рукописные ФБ с семантикой S7; [MAPPING.md](MAPPING.md),
«Слой совместимости S7Compat»).

Сконвертированный код вызывает рукописные объекты (не генерируются, лежат в `src/*/S7Compat`): `FB_S7Tof`, `FB_S7Ton`, `FB_S7Tp`, `F_NormX`, `F_S7Now`, `F_ScaleX`, `GVL_S7Clock`. Конструкции, переведённые через них, считаются «автоматически»: их поведение задают описания в
объявлениях этих объектов и тесты `tests/POUs/S7Compat`, результат прогона в CODESYS —
[TEST_REPORT.md](TEST_REPORT.md).

## Не поддерживается — причины

| Правило | Что | Пометок |
|---|---|---:|
| `func.unsupported` | функция S7 без аналога | 8 |
| `type.unsupported` | тип S7 без аналога | 5 |
| `decl.dropped_use` | использует неперенесённое объявление | 4 |
| `addr.unsupported` | адрес не I/Q/M | 2 |
| `call.param_dropped` | аргумент неперенесённого параметра | 2 |
| `decl.at` | AT (наложение) | 2 |
| `stmt.goto` | GOTO | 2 |
| `stmt.label` | метка перехода | 2 |
| `addr.peripheral` | доступ к периферии :P | 1 |
| `expr.eno` | EN/ENO/OK | 1 |
| `ob.event` | событийный OB | 1 |

## Требует проверки — причины

| Правило | Что | Пометок |
|---|---|---:|
| `fb.f_trig` | F_TRIG: начальное состояние памяти | 5 |
| `type.s5time` | S5Time → TIME | 5 |
| `ob.start_info` | стартовая информация OB | 4 |
| `expr.slice_read` | чтение среза .%B/.%W/.%D | 3 |
| `block.non_optimized` | неоптимизированный доступ | 2 |
| `conv.s5time` | S5TIME_TO_TIME | 2 |
| `name.renamed` | переименование (ключевое слово) | 2 |
| `ob.initial_call` | Initial_Call: эмуляция | 2 |
| `db.retain_standard` | стандартный DB: retain | 1 |
| `fb.counter` | счётчики CTU/CTD/CTUD (WORD) | 1 |
| `func.scale_x_int` | SCALE_X с целым результатом | 1 |
| `ob.startup` | OB100 → флаг первого цикла | 1 |
| `section.fb_retain` | VAR RETAIN в ФБ: весь экземпляр | 1 |

## Подробно по файлам

### `samples/scl/DB_Plant.scl`

Конструкций 72: автоматически 69, требуют проверки 2, не поддерживаются 1.

Блоки: DATA_BLOCK «DB_Plant» → `DB_Plant`; DATA_BLOCK «DB_Hmi» → `DB_Hmi`; DATA_BLOCK «DB_Telegram» → `DB_Telegram`; DATA_BLOCK «DB_RecipeActive» → `GVL_InstanceDBs.DB_RecipeActive`; DATA_BLOCK «DB_P101» → `GVL_InstanceDBs.DB_P101`; DATA_BLOCK «DB_P102» → `GVL_InstanceDBs.DB_P102`; DATA_BLOCK «DB_P103» → `GVL_InstanceDBs.DB_P103`; DATA_BLOCK «DB_PIC101» → `GVL_InstanceDBs.DB_PIC101`; DATA_BLOCK «DB_FQ101» → `GVL_InstanceDBs.DB_FQ101`; DATA_BLOCK «DB_Backwash» → `GVL_InstanceDBs.DB_Backwash`; DATA_BLOCK «DB_PT101» → `GVL_InstanceDBs.DB_PT101`; DATA_BLOCK «DB_LT101» → `GVL_InstanceDBs.DB_LT101`; DATA_BLOCK «DB_FT101» → `GVL_InstanceDBs.DB_FT101`; DATA_BLOCK «DB_AlarmPT101» → `GVL_InstanceDBs.DB_AlarmPT101`; DATA_BLOCK «DB_Mode» → `GVL_InstanceDBs.DB_Mode`; DATA_BLOCK «DB_PumpAlt» → `GVL_InstanceDBs.DB_PumpAlt`; DATA_BLOCK «DB_LS201» → `GVL_InstanceDBs.DB_LS201`; DATA_BLOCK «DB_XV201» → `GVL_InstanceDBs.DB_XV201`; DATA_BLOCK «DB_Dosing» → `GVL_InstanceDBs.DB_Dosing`; DATA_BLOCK «DB_Logger» → `GVL_InstanceDBs.DB_Logger`; DATA_BLOCK «DB_LegacyTlg» → `GVL_InstanceDBs.DB_LegacyTlg`; DATA_BLOCK «DB_RampSP» → `GVL_InstanceDBs.DB_RampSP`.

| Строка | Статус | Блок | Правило | Причина |
|---:|---|---|---|---|
| 53 | ✕ не поддерживается | DB_Plant | `type.unsupported` | DTL — структура S7 (YEAR, MONTH, ...), в CODESYS нет; заменить на DT или свою структуру |
| 111 | ! требует проверки | DB_Telegram | `block.non_optimized` | стандартный (неоптимизированный) доступ S7: абсолютная адресация и порядок байтов не переносятся |
| 266 | ! требует проверки | DB_LegacyTlg | `db.retain_standard` | стандартный (неоптимизированный) экземплярный или типизированный DB без NON_RETAIN: в S7 он реманентный целиком — объявлен в VAR_GLOBAL RETAIN GVL_InstanceDBs |

### `samples/scl/FB_AlarmDelay.scl`

Конструкций 40: автоматически 40, требуют проверки 0, не поддерживаются 0.

Блоки: FUNCTION_BLOCK «FB_AlarmDelay» → `FB_AlarmDelay`.

Пометок нет.

### `samples/scl/FB_AnalogIn.scl`

Конструкций 71: автоматически 71, требуют проверки 0, не поддерживаются 0.

Блоки: FUNCTION_BLOCK «FB_AnalogIn» → `FB_AnalogIn`.

Пометок нет.

### `samples/scl/FB_BatchCounter.scl`

Конструкций 36: автоматически 32, требуют проверки 4, не поддерживаются 0.

Блоки: FUNCTION_BLOCK «FB_BatchCounter» → `FB_BatchCounter`.

| Строка | Статус | Блок | Правило | Причина |
|---:|---|---|---|---|
| 54 | ! требует проверки | FB_BatchCounter | `fb.f_trig` | F_TRIG: в S7 на первом вызове с CLK = FALSE спада нет; у F_TRIG CODESYS Standard 3.5.17.0 — тоже (тест StandardFTrigMatchesS7 в Control Win); с другой версией Standard повторить этот тест |
| 55 | ! требует проверки | FB_BatchCounter | `fb.counter` | счётчик S7 → CTU (CODESYS Standard): PV и CV — WORD (0…65535), в S7 — тип счётчика; проверить диапазон |
| 90 | ! требует проверки | FB_BatchCounter | `expr.slice_read` | срез .%W0 → DWORD_TO_WORD(SHR(...)): нумерация срезов S7 от младшей части — сверить с источником |
| 91 | ! требует проверки | FB_BatchCounter | `expr.slice_read` | срез .%B1 → WORD_TO_BYTE(SHR(...)): нумерация срезов S7 от младшей части — сверить с источником |

### `samples/scl/FB_Debounce.scl`

Конструкций 28: автоматически 23, требуют проверки 5, не поддерживаются 0.

Блоки: FUNCTION_BLOCK «FB_Debounce» → `FB_Debounce`.

| Строка | Статус | Блок | Правило | Причина |
|---:|---|---|---|---|
| 37 | ! требует проверки | FB_Debounce | `type.s5time` | S5Time → TIME: в S7 S5TIME — BCD с шагом 10 мс…10 с, диапазон до 2h46m30s |
| 38 | ! требует проверки | FB_Debounce | `type.s5time` | S5Time → TIME: в S7 S5TIME — BCD с шагом 10 мс…10 с, диапазон до 2h46m30s |
| 52 | ! требует проверки | FB_Debounce | `fb.f_trig` | F_TRIG: в S7 на первом вызове с CLK = FALSE спада нет; у F_TRIG CODESYS Standard 3.5.17.0 — тоже (тест StandardFTrigMatchesS7 в Control Win); с другой версией Standard повторить этот тест |
| 64 | ! требует проверки | FB_Debounce | `conv.s5time` | S5TI_TIM: S5Time уже сопоставлен с TIME — преобразование убрано |
| 65 | ! требует проверки | FB_Debounce | `conv.s5time` | S5TI_TIM: S5Time уже сопоставлен с TIME — преобразование убрано |

### `samples/scl/FB_EventLogger.scl`

Конструкций 60: автоматически 53, требуют проверки 1, не поддерживаются 6.

Блоки: FUNCTION_BLOCK «FB_EventLogger» → `FB_EventLogger`.

| Строка | Статус | Блок | Правило | Причина |
|---:|---|---|---|---|
| 40 | ✕ не поддерживается | FB_EventLogger | `type.unsupported` | Variant — нет аналога в CODESYS; переписать (ANY, POINTER или перегрузка) |
| 67 | ! требует проверки | FB_EventLogger | `name.renamed` | имя «ret» переименовано в «ret_» (ключевое слово CODESYS или повтор) |
| 81 | ✕ не поддерживается | FB_EventLogger | `func.unsupported` | RUNTIME: нет прямого аналога в CODESYS Standard |
| 96 | ✕ не поддерживается | FB_EventLogger | `func.unsupported` | RD_SYS_T: нет прямого аналога в CODESYS Standard |
| 100 | ✕ не поддерживается | FB_EventLogger | `func.unsupported` | TypeOf: нет прямого аналога в CODESYS Standard |
| 126 | ✕ не поддерживается | FB_EventLogger | `func.unsupported` | PEEK: нет прямого аналога в CODESYS Standard |
| 128 | ✕ не поддерживается | FB_EventLogger | `func.unsupported` | POKE: нет прямого аналога в CODESYS Standard |

### `samples/scl/FB_LegacyTelegram.scl`

Конструкций 45: автоматически 26, требуют проверки 3, не поддерживаются 16.

Блоки: FUNCTION_BLOCK «FB_LegacyTelegram» → `FB_LegacyTelegram`.

| Строка | Статус | Блок | Правило | Причина |
|---:|---|---|---|---|
| 36 | ! требует проверки | FB_LegacyTelegram | `block.non_optimized` | стандартный (неоптимизированный) доступ S7: абсолютная адресация и порядок байтов не переносятся |
| 47 | ✕ не поддерживается | FB_LegacyTelegram | `type.unsupported` | Any (указатель S7) — нет аналога |
| 49 | ! требует проверки | FB_LegacyTelegram | `type.s5time` | S5Time → TIME: в S7 S5TIME — BCD с шагом 10 мс…10 с, диапазон до 2h46m30s |
| 62 | ✕ не поддерживается | FB_LegacyTelegram | `decl.at` | AT (наложение переменных S7) — переписать через UNION или битовый доступ |
| 67 | ✕ не поддерживается | FB_LegacyTelegram | `type.unsupported` | Any (указатель S7) — нет аналога |
| 68 | ✕ не поддерживается | FB_LegacyTelegram | `decl.at` | AT (наложение переменных S7) — переписать через UNION или битовый доступ |
| 75 | ! требует проверки | FB_LegacyTelegram | `type.s5time` | S5Time → TIME: в S7 S5TIME — BCD с шагом 10 мс…10 с, диапазон до 2h46m30s |
| 87 | ✕ не поддерживается | FB_LegacyTelegram | `stmt.goto` | GOTO — переходы не переносятся (переписать структурно) |
| 91 | ✕ не поддерживается | FB_LegacyTelegram | `decl.dropped_use` | использует «srcPtr», объявление которой не перенесено (Any (указатель S7) — нет аналога) |
| 92 | ✕ не поддерживается | FB_LegacyTelegram | `decl.dropped_use` | использует «srcView», объявление которой не перенесено (AT (наложение переменных S7)) |
| 98 | ✕ не поддерживается | FB_LegacyTelegram | `func.unsupported` | BLKMOV: нет прямого аналога в CODESYS Standard |
| 99 | ✕ не поддерживается | FB_LegacyTelegram | `addr.unsupported` | адрес %DB30.DBW0 не поддерживается (только %I, %Q, %M) |
| 101 | ✕ не поддерживается | FB_LegacyTelegram | `addr.unsupported` | адрес %DB30.DBW2 не поддерживается (только %I, %Q, %M) |
| 103 | ✕ не поддерживается | FB_LegacyTelegram | `decl.dropped_use` | использует «statusBits», объявление которой не перенесено (AT (наложение переменных S7)) |
| 109 | ✕ не поддерживается | FB_LegacyTelegram | `expr.eno` | ENO: флаги EN/ENO/OK S7 не поддерживаются |
| 110 | ✕ не поддерживается | FB_LegacyTelegram | `stmt.goto` | GOTO — переходы не переносятся (переписать структурно) |
| 116 | ✕ не поддерживается | FB_LegacyTelegram | `stmt.label` | метка перехода — переходы не переносятся |
| 117 | ✕ не поддерживается | FB_LegacyTelegram | `func.unsupported` | S_ODT: нет прямого аналога в CODESYS Standard |
| 128 | ✕ не поддерживается | FB_LegacyTelegram | `stmt.label` | метка перехода — переходы не переносятся |

### `samples/scl/FB_ModeSelect.scl`

Конструкций 43: автоматически 42, требуют проверки 1, не поддерживаются 0.

Блоки: FUNCTION_BLOCK «FB_ModeSelect» → `FB_ModeSelect`.

| Строка | Статус | Блок | Правило | Причина |
|---:|---|---|---|---|
| 106 | ! требует проверки | FB_ModeSelect | `expr.slice_read` | срез .%B1 → WORD_TO_BYTE(SHR(...)): нумерация срезов S7 от младшей части — сверить с источником |

### `samples/scl/FB_Motor.scl`

Конструкций 64: автоматически 64, требуют проверки 0, не поддерживаются 0.

Блоки: FUNCTION_BLOCK «FB_Motor» → `FB_Motor`.

Пометок нет.

### `samples/scl/FB_PIController.scl`

Конструкций 49: автоматически 49, требуют проверки 0, не поддерживаются 0.

Блоки: FUNCTION_BLOCK «FB_PIController» → `FB_PIController`.

Пометок нет.

### `samples/scl/FB_PumpAlternation.scl`

Конструкций 59: автоматически 58, требуют проверки 1, не поддерживаются 0.

Блоки: FUNCTION_BLOCK «FB_PumpAlternation» → `FB_PumpAlternation`.

| Строка | Статус | Блок | Правило | Причина |
|---:|---|---|---|---|
| 65 | ! требует проверки | FB_PumpAlternation | `fb.f_trig` | F_TRIG: в S7 на первом вызове с CLK = FALSE спада нет; у F_TRIG CODESYS Standard 3.5.17.0 — тоже (тест StandardFTrigMatchesS7 в Control Win); с другой версией Standard повторить этот тест |

### `samples/scl/FB_Ramp.scl`

Конструкций 32: автоматически 32, требуют проверки 0, не поддерживаются 0.

Блоки: FUNCTION_BLOCK «FB_Ramp» → `FB_Ramp`.

Пометок нет.

### `samples/scl/FB_Sequencer.scl`

Конструкций 80: автоматически 80, требуют проверки 0, не поддерживаются 0.

Блоки: FUNCTION_BLOCK «FB_Sequencer» → `FB_Sequencer`.

Пометок нет.

### `samples/scl/FB_Totalizer.scl`

Конструкций 39: автоматически 38, требуют проверки 1, не поддерживаются 0.

Блоки: FUNCTION_BLOCK «FB_Totalizer» → `FB_Totalizer`.

| Строка | Статус | Блок | Правило | Причина |
|---:|---|---|---|---|
| 61 | ! требует проверки | FB_Totalizer | `section.fb_retain` | VAR RETAIN в ФБ: в CODESYS при RETAIN-переменной в retain-памяти хранится весь экземпляр ФБ, в S7 — только эти переменные (сверить с источником) |

### `samples/scl/FB_Valve.scl`

Конструкций 75: автоматически 73, требуют проверки 2, не поддерживаются 0.

Блоки: FUNCTION_BLOCK «FB_Valve» → `FB_Valve`.

| Строка | Статус | Блок | Правило | Причина |
|---:|---|---|---|---|
| 74 | ! требует проверки | FB_Valve | `fb.f_trig` | F_TRIG: в S7 на первом вызове с CLK = FALSE спада нет; у F_TRIG CODESYS Standard 3.5.17.0 — тоже (тест StandardFTrigMatchesS7 в Control Win); с другой версией Standard повторить этот тест |
| 75 | ! требует проверки | FB_Valve | `fb.f_trig` | F_TRIG: в S7 на первом вызове с CLK = FALSE спада нет; у F_TRIG CODESYS Standard 3.5.17.0 — тоже (тест StandardFTrigMatchesS7 в Control Win); с другой версией Standard повторить этот тест |

### `samples/scl/FC_Statistics.scl`

Конструкций 40: автоматически 40, требуют проверки 0, не поддерживаются 0.

Блоки: FUNCTION «FC_Statistics» → `FC_Statistics`.

Пометок нет.

### `samples/scl/OB_Cyclic.scl`

Конструкций 15: автоматически 13, требуют проверки 2, не поддерживаются 0.

Блоки: ORGANIZATION_BLOCK «Cyclic interrupt» → `PRG_Cyclic_interrupt`.

| Строка | Статус | Блок | Правило | Причина |
|---:|---|---|---|---|
| 33 | ! требует проверки | Cyclic interrupt | `ob.start_info` | входы OB (стартовая информация S7) объявлены как VAR — CODESYS их не заполняет |
| 43 | ! требует проверки | Cyclic interrupt | `ob.initial_call` | вход OB Initial_Call эмулируется флагом первого цикла: флаг (не RETAIN) сбрасывается загрузкой, Reset warm/cold и перезапуском ПЛК, но не командой Stop → Start CODESYS (в S7 Initial_Call = TRUE после каждого STOP → RUN) |
| 67 | ! требует проверки | Cyclic interrupt | `func.scale_x_int` | SCALE_X с целым OUT: REAL_TO_INT округляет — сверить с S7 |

### `samples/scl/OB_Main.scl`

Конструкций 68: автоматически 63, требуют проверки 2, не поддерживаются 3.

Блоки: ORGANIZATION_BLOCK «Main» → `PRG_Main`.

| Строка | Статус | Блок | Правило | Причина |
|---:|---|---|---|---|
| 45 | ! требует проверки | Main | `ob.start_info` | входы OB (стартовая информация S7) объявлены как VAR — CODESYS их не заполняет |
| 53 | ! требует проверки | Main | `ob.initial_call` | вход OB Initial_Call эмулируется флагом первого цикла: флаг (не RETAIN) сбрасывается загрузкой, Reset warm/cold и перезапуском ПЛК, но не командой Stop → Start CODESYS (в S7 Initial_Call = TRUE после каждого STOP → RUN) |
| 67 | ✕ не поддерживается | Main | `addr.peripheral` | %IW272:P: прямой доступ к периферии (:P) не поддерживается |
| 137 | ! требует проверки | Main | `type.s5time` | S5Time → TIME: в S7 S5TIME — BCD с шагом 10 мс…10 с, диапазон до 2h46m30s |
| 189 | ✕ не поддерживается | Main | `call.param_dropped` | параметр extraInfo не перенесён (Variant — нет аналога в CODESYS; переписать (ANY, POINTER или перегрузка)) — аргумент опущен |
| 194 | ✕ не поддерживается | Main | `call.param_dropped` | параметр source не перенесён (Any (указатель S7) — нет аналога) — аргумент опущен |

### `samples/scl/OB_Startup.scl`

Конструкций 25: автоматически 19, требуют проверки 2, не поддерживаются 4.

Блоки: ORGANIZATION_BLOCK «Startup» → `PRG_Startup`; ORGANIZATION_BLOCK «Diagnostic error interrupt» → `PRG_Diagnostic_error_interrupt`.

| Строка | Статус | Блок | Правило | Причина |
|---:|---|---|---|---|
| 32 | ! требует проверки | Startup | `ob.startup` | OB100 (Startup) → однократное выполнение по флагу первого цикла в MainTask: флаг (не RETAIN) сбрасывается загрузкой, Reset warm/cold и перезапуском ПЛК, но не командой Stop → Start CODESYS (в S7 OB100 выполняется при каждом STOP → RUN); задачи с более высоким приоритетом могут выполниться раньше |
| 36 | ! требует проверки | Startup | `ob.start_info` | входы OB (стартовая информация S7) объявлены как VAR — CODESYS их не заполняет |
| 43 | ! требует проверки | Startup | `name.renamed` | имя «ret» переименовано в «ret_» (ключевое слово CODESYS или повтор) |
| 62 | ✕ не поддерживается | Startup | `func.unsupported` | WR_SYS_T: нет прямого аналога в CODESYS Standard |
| 67 | ✕ не поддерживается | Diagnostic error interrupt | `ob.event` | OB82: событийный OB — задача по событию не создаётся, настроить вручную |
| 71 | ! требует проверки | Diagnostic error interrupt | `ob.start_info` | входы событийного OB (стартовая информация S7) оставлены VAR_INPUT: CODESYS их не заполняет — их передаёт вызов из обработчика события |
| 73 | ✕ не поддерживается | Diagnostic error interrupt | `type.unsupported` | системный тип S7 HW_ANY не поддерживается |
| 81 | ✕ не поддерживается | Diagnostic error interrupt | `decl.dropped_use` | использует «LADDR», объявление которой не перенесено (системный тип S7 HW_ANY не поддерживается) |

### `samples/scl/UDT_PlantTypes.scl`

Конструкций 24: автоматически 24, требуют проверки 0, не поддерживаются 0.

Блоки: TYPE «UDT_AnalogCfg» → `UDT_AnalogCfg`; TYPE «UDT_DeviceStatus» → `UDT_DeviceStatus`; TYPE «UDT_DosingRecipe» → `UDT_DosingRecipe`.

Пометок нет.

### `(проект: слой ввода-вывода, теги, экземпляры DB)`

Конструкций 33: автоматически 33, требуют проверки 0, не поддерживаются 0.

Пометок нет.
