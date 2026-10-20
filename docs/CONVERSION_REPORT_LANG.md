# Отчёт конвертации S7 (LAD, FBD, STL, SCL) → ST CODESYS

Сгенерирован `s7conv 0.1.0` — не редактировать вручную, пересоздаётся командой
`s7conv build-corpus` (см. README). Вход: `samples/lang`.

Единица учёта — **конструкция**: блок S7, объявление переменной или оператор (вложенные
операторы считаются отдельно). Статусы: **автоматически** — переведено без замечаний;
**требует проверки** — переведено, в коде пометка `// MIGRATION-CHECK: причина`;
**не поддерживается** — не переведено, в коде `// MIGRATION-TODO: причина` и закомментированный
исходный текст. Правила соответствия — [MAPPING.md](MAPPING.md), подмножество SCL —
[GRAMMAR.md](GRAMMAR.md).

## Итог

| Показатель | Значение |
|---|---:|
| Файлов | 9 |
| Блоков S7 | 9 |
| Конструкций | 212 |
| Автоматически | 197 (93 %) |
| Требуют проверки | 15 (7 %) |
| Не поддерживаются | 0 (0 %) |

### По видам конструкций

| Вид | Всего | Автоматически | Требуют проверки | Не поддерживаются |
|---|---:|---:|---:|---:|
| Блоки | 9 | 6 | 3 | 0 |
| Объявления | 102 | 102 | 0 | 0 |
| Операторы | 101 | 89 | 12 | 0 |

## По файлам

| Файл | Блоков | Конструкций | Автоматически | Требуют проверки | Не поддерживаются | Авто, % |
|---|---:|---:|---:|---:|---:|---:|
| `samples/lang/DB_Process.xml` | 1 | 7 | 6 | 1 | 0 | 86 % |
| `samples/lang/FB_ConveyorStl.xml` | 1 | 39 | 33 | 6 | 0 | 85 % |
| `samples/lang/FB_PumpInterlockLad.xml` | 1 | 52 | 47 | 5 | 0 | 90 % |
| `samples/lang/FB_StarterFbd.xml` | 1 | 25 | 24 | 1 | 0 | 96 % |
| `samples/lang/FB_StarterLad.xml` | 1 | 25 | 24 | 1 | 0 | 96 % |
| `samples/lang/FB_StarterScl.xml` | 1 | 23 | 23 | 0 | 0 | 100 % |
| `samples/lang/FB_StarterStl.xml` | 1 | 28 | 27 | 1 | 0 | 96 % |
| `samples/lang/FC_ClampPctLad.xml` | 1 | 9 | 9 | 0 | 0 | 100 % |
| `samples/lang/UDT_Valve.xml` | 1 | 4 | 4 | 0 | 0 | 100 % |
| **Итого** | 9 | 212 | 197 | 15 | 0 | 93 % |

## По языкам

Единица учёта языка: LAD/FBD — элемент и сеть, STL — инструкция, GRAPH — шаг (ниже — независимо от
конструкций ST выше). Статус единицы — тяжелейший из её правил: **авто**, **проверка**
(`MIGRATION-CHECK`), **нет** (`MIGRATION-TODO`), **невозможно** (аналога в CODESYS нет).

| Язык | Единица | Блоков | Всего | Авто | Проверка | Нет | Невозможно |
|---|---|---:|---:|---:|---:|---:|---:|
| LAD | элемент | 3 | 58 | 52 | 6 | 0 | 0 |
| LAD | сеть | 3 | 19 | 15 | 4 | 0 | 0 |
| FBD | элемент | 1 | 11 | 7 | 4 | 0 | 0 |
| FBD | сеть | 1 | 4 | 1 | 3 | 0 | 0 |
| STL | инструкция | 2 | 74 | 69 | 5 | 0 | 0 |
| SCL | сеть | 1 | 1 | 1 | 0 | 0 | 0 |

### Блоки: язык, стратегия, переходы STL

| Блок | Язык | Стратегия | Профиль и переходы STL | Источник |
|---|---|---|---|---|
| `DB_Process` | DB | `st` | — | `samples/lang/DB_Process.xml` |
| `FB_ConveyorStl` | STL | `st` | по MemoryLayout; переходы: structured | `samples/lang/FB_ConveyorStl.xml` |
| `FB_PumpInterlockLad` | LAD | `st` | — | `samples/lang/FB_PumpInterlockLad.xml` |
| `FB_StarterFbd` | FBD | `st` | — | `samples/lang/FB_StarterFbd.xml` |
| `FB_StarterLad` | LAD | `st` | — | `samples/lang/FB_StarterLad.xml` |
| `FB_StarterScl` | SCL | `st` | — | `samples/lang/FB_StarterScl.xml` |
| `FB_StarterStl` | STL | `st` | по MemoryLayout; переходы: structured | `samples/lang/FB_StarterStl.xml` |
| `FC_ClampPctLad` | LAD | `st` | — | `samples/lang/FC_ClampPctLad.xml` |
| `UDT_Valve` | UDT | `st` | — | `samples/lang/UDT_Valve.xml` |

### Правила языков: проверка и ручная работа

| Правило | Что | Статус | Единиц |
|---|---|---|---:|
| `lad.vocab_unverified` | LAD: форма XML элемента не подтверждена экспортом | проверка | 8 |
| `fbd.vocab_unverified` | FBD: форма XML элемента не подтверждена экспортом | проверка | 7 |
| `s5.timebase` | S5: пуск таймера — время и шкала по модели S7Compat | проверка | 5 |
| `lad.eno_error` | LAD: ENO = EN AND NOT ошибка | проверка | 2 |


## Задачи CODESYS (из OB)

OB в исходниках нет.

Задачи записываются в — (OB в корпусе всех языков нет) (формат — MAPPING.md, «OB и задачи»).

## Слой совместимости S7Compat

Режимы: таймеры TON/TOF/TP — `s7compat`, F_TRIG — `standard` (`standard` — библиотека
Standard CODESYS, `s7compat` — рукописные ФБ с семантикой S7; [MAPPING.md](MAPPING.md),
«Слой совместимости S7Compat»).

Сконвертированный код вызывает рукописные объекты (не генерируются, лежат в `src/*/S7Compat`): `FB_S7Ton`, `F_S5BaseMs`, `F_S5Bcd`, `F_S5Bin`, `F_S5CountUp`, `F_S5CounterBcd`, `F_S5CounterBin`, `F_S5CounterReset`, `F_S5Enable`, `F_S5ExtPulse`, `F_S5FromBcd`, `F_S5OffDelay`, `F_S5OnDelay`, `F_S5Pulse`, `F_S5Q`, `F_S5Reset`, `F_S5RetOnDelay`, `F_S5Start`, `F_S5TimeWord`, `F_S5ToBcd`, `F_S5Update`, `F_S7EnoAddInt`, `F_S7Now`, `GVL_S7Clock`, `ST_S5Counter`, `ST_S5Timer`. Конструкции, переведённые через них, считаются «автоматически»: их поведение задают описания в
объявлениях этих объектов и тесты `tests/POUs/S7Compat`, результат прогона в CODESYS —
[TEST_REPORT.md](TEST_REPORT.md).

## Не поддерживается — причины

Нет.

## Требует проверки — причины

| Правило | Что | Пометок |
|---|---|---:|
| `lad.vocab_unverified` | LAD: форма XML элемента не подтверждена экспортом | 5 |
| `s5.timebase` | S5: пуск таймера — время и шкала по модели S7Compat | 5 |
| `block.non_optimized` | неоптимизированный доступ | 3 |
| `db.retain_standard` | стандартный DB: retain | 1 |
| `fbd.vocab_unverified` | FBD: форма XML элемента не подтверждена экспортом | 1 |
| `lad.eno_error` | LAD: ENO = EN AND NOT ошибка | 1 |

## Подробно по файлам

### `samples/lang/DB_Process.xml`

Конструкций 7: автоматически 6, требуют проверки 1, не поддерживаются 0.

Блоки: DATA_BLOCK «DB_Process» → `DB_Process`.

| Место | Статус | Блок | Правило | Причина |
|---:|---|---|---|---|
| SW.Blocks.GlobalDB «DB_Process» | ! требует проверки | DB_Process | `block.non_optimized` | стандартный (неоптимизированный) доступ S7: абсолютная адресация и порядок байтов не переносятся |
| SW.Blocks.GlobalDB «DB_Process» | ! требует проверки | DB_Process | `db.retain_standard` | стандартный DB без NON_RETAIN: в S7 он реманентный — объявлен RETAIN |

### `samples/lang/FB_ConveyorStl.xml`

Конструкций 39: автоматически 33, требуют проверки 6, не поддерживаются 0.

Блоки: FUNCTION_BLOCK «FB_ConveyorStl» → `FB_ConveyorStl`.

| Место | Статус | Блок | Правило | Причина |
|---:|---|---|---|---|
| SW.Blocks.FB «FB_ConveyorStl» | ! требует проверки | FB_ConveyorStl | `block.non_optimized` | стандартный (неоптимизированный) доступ S7: абсолютная адресация и порядок байтов не переносятся |
| сеть 2, строка 3 | ! требует проверки | FB_ConveyorStl | `s5.timebase` | SP T1 → F_S5Pulse (S7Compat): время — F_S7Now(), остаток пересчитывается при обращении к таймеру; фаза часового процесса CPU (точность ±1 единица шкалы) не моделируется |
| сеть 3, строка 3 | ! требует проверки | FB_ConveyorStl | `s5.timebase` | SD T2 → F_S5OnDelay (S7Compat): время — F_S7Now(), остаток пересчитывается при обращении к таймеру; фаза часового процесса CPU (точность ±1 единица шкалы) не моделируется |
| сеть 4, строка 3 | ! требует проверки | FB_ConveyorStl | `s5.timebase` | SF T3 → F_S5OffDelay (S7Compat): время — F_S7Now(), остаток пересчитывается при обращении к таймеру; фаза часового процесса CPU (точность ±1 единица шкалы) не моделируется |
| сеть 5, строка 3 | ! требует проверки | FB_ConveyorStl | `s5.timebase` | SE T4 → F_S5ExtPulse (S7Compat): время — F_S7Now(), остаток пересчитывается при обращении к таймеру; фаза часового процесса CPU (точность ±1 единица шкалы) не моделируется |
| сеть 5, строка 8 | ! требует проверки | FB_ConveyorStl | `s5.timebase` | SS T5 → F_S5RetOnDelay (S7Compat): время — F_S7Now(), остаток пересчитывается при обращении к таймеру; фаза часового процесса CPU (точность ±1 единица шкалы) не моделируется |

### `samples/lang/FB_PumpInterlockLad.xml`

Конструкций 52: автоматически 47, требуют проверки 5, не поддерживаются 0.

Блоки: FUNCTION_BLOCK «FB_PumpInterlockLad» → `FB_PumpInterlockLad`.

| Место | Статус | Блок | Правило | Причина |
|---:|---|---|---|---|
| сеть 5, UId 21 | ! требует проверки | FB_PumpInterlockLad | `lad.vocab_unverified` | элемент «Jump»: имя и пины в SimaticML не подтверждены открытым экспортом (docs/MAPPING_LADFBD.md, уровень L) |
| сеть 7, UId 25 | ! требует проверки | FB_PumpInterlockLad | `lad.eno_error` | ENO Add S7 = EN AND NOT переполнение: F_S7EnoAddInt из S7Compat (в CODESYS ENO = EN); результат при переполнении записывается с переносом, как у S7-300 [M] |
| сеть 9, UId 23 | ! требует проверки | FB_PumpInterlockLad | `lad.vocab_unverified` | элемент «Call»: имя и пины в SimaticML не подтверждены открытым экспортом (docs/MAPPING_LADFBD.md, уровень L) |
| сеть 9, UId 28 | ! требует проверки | FB_PumpInterlockLad | `lad.vocab_unverified` | элемент «Call»: имя и пины в SimaticML не подтверждены открытым экспортом (docs/MAPPING_LADFBD.md, уровень L) |
| сеть 9, UId 33 | ! требует проверки | FB_PumpInterlockLad | `lad.vocab_unverified` | элемент «Call»: имя и пины в SimaticML не подтверждены открытым экспортом (docs/MAPPING_LADFBD.md, уровень L) |

### `samples/lang/FB_StarterFbd.xml`

Конструкций 25: автоматически 24, требуют проверки 1, не поддерживаются 0.

Блоки: FUNCTION_BLOCK «FB_StarterFbd» → `FB_StarterFbd`.

| Место | Статус | Блок | Правило | Причина |
|---:|---|---|---|---|
| сеть 1, UId 28 | ! требует проверки | FB_StarterFbd | `fbd.vocab_unverified` | элемент «SR»: имя и пины в SimaticML не подтверждены открытым экспортом (docs/MAPPING_LADFBD.md, уровень L) |

### `samples/lang/FB_StarterLad.xml`

Конструкций 25: автоматически 24, требуют проверки 1, не поддерживаются 0.

Блоки: FUNCTION_BLOCK «FB_StarterLad» → `FB_StarterLad`.

| Место | Статус | Блок | Правило | Причина |
|---:|---|---|---|---|
| сеть 1, UId 32 | ! требует проверки | FB_StarterLad | `lad.vocab_unverified` | элемент «SR»: имя и пины в SimaticML не подтверждены открытым экспортом (docs/MAPPING_LADFBD.md, уровень L) |

### `samples/lang/FB_StarterScl.xml`

Конструкций 23: автоматически 23, требуют проверки 0, не поддерживаются 0.

Блоки: FUNCTION_BLOCK «FB_StarterScl» → `FB_StarterScl`.

Пометок нет.

### `samples/lang/FB_StarterStl.xml`

Конструкций 28: автоматически 27, требуют проверки 1, не поддерживаются 0.

Блоки: FUNCTION_BLOCK «FB_StarterStl» → `FB_StarterStl`.

| Место | Статус | Блок | Правило | Причина |
|---:|---|---|---|---|
| SW.Blocks.FB «FB_StarterStl» | ! требует проверки | FB_StarterStl | `block.non_optimized` | стандартный (неоптимизированный) доступ S7: абсолютная адресация и порядок байтов не переносятся |

### `samples/lang/FC_ClampPctLad.xml`

Конструкций 9: автоматически 9, требуют проверки 0, не поддерживаются 0.

Блоки: FUNCTION «FC_ClampPctLad» → `FC_ClampPctLad`.

Пометок нет.

### `samples/lang/UDT_Valve.xml`

Конструкций 4: автоматически 4, требуют проверки 0, не поддерживаются 0.

Блоки: TYPE «UDT_Valve» → `UDT_Valve`.

Пометок нет.
