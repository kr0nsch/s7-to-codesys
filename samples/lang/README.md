# Корпус всех языков S7 (`samples/lang/`)

Блоки той же вымышленной водопроводной станции, что и корпус SCL (`samples/scl/`), но в формате
SimaticML — XML экспорта TIA Portal Openness — и на языках LAD, FBD, STL и SCL. Это вход конвертера и
материал для проверки поведения: сценарии `scenarios/lang/` посчитаны моделями по описанию логики ниже,
а не по результату конвертации.

> **Честно о происхождении.** TIA Portal в окружении проекта нет, поэтому XML не экспортирован из TIA, а
> собран скриптом `build_xml.py` из описания блоков `blocks.py`. Форма документа повторяет открытые
> экспорты TIA (см. `EXTERNAL.json`), а фрагменты `Sections`, `FlgNet`, `StatementList` и `StructuredText`
> валидны по XSD V21 своей версии — это проверяет `s7conv/tests/test_lang_external.py`. Имена элементов
> LAD/FBD и их пинов XSD не проверяет: для элементов, которых нет в открытых экспортах (SR/RS с
> операндом, FBD-блоки A/O, вызовы, прыжки), форма взята из руководства и помечена уровнем L в
> [MAPPING_LADFBD.md](../../docs/MAPPING_LADFBD.md). Импорт этих файлов в TIA Portal не проверялся.

## Как собирается

```bat
python samples/lang/build_xml.py           # записать samples/lang/*.xml
python samples/lang/build_xml.py --check   # сравнить с файлами (CI), код 1 — устарело
```

XML — артефакт в git: руками не правится. UId элементов назначаются по порядку создания с 21 (как в
экспортах TIA), провода — после элементов; пространства имён — по версии TIA (`--tia V21`). Перевод
корпуса в ST — `python -m s7conv build-corpus` (папка `src/*/Lang/Converted/`, отчёт
[CONVERSION_REPORT_LANG.md](../../docs/CONVERSION_REPORT_LANG.md)).

## Блоки

| Файл | Блок | Язык | Сценарии | Что проверяет |
|---|---|---|---|---|
| `FB_StarterLad.xml` | FB 101 | LAD | `FB_Starter.csv` | SR с битом-операндом при S = R1 = 1, TON обратной связи, самоподхват аварии, P-фронт (PBox) счётчика пусков, ADD |
| `FB_StarterFbd.xml` | FB 102 | FBD | `FB_Starter.csv` | то же на блоках A/O с отрицанием входа |
| `FB_StarterStl.xml` | FB 103 | STL (стандартный доступ, S7-300) | `FB_Starter.csv` | `A/AN/O/ON`, скобки, `S/R`, `=`, `CALL` TON, `FP`, `JCN` с меткой, `L/T`, `+I` |
| `FB_StarterScl.xml` | FB 104 | SCL в SimaticML | `FB_Starter.csv` | сеть SCL из токенов XML; тот же ST, что из `.scl` |
| `FB_PumpInterlockLad.xml` | FB 110 | LAD | `FB_PumpInterlockLad.csv` | S/R, сравнения, MOVE, прыжок вперёд к метке, PBox с битом, который читается в другой сети, ADD с ENO, цепочка трёх вызовов EN → ENO → EN |
| `FC_ClampPctLad.xml` | FC 111 | LAD | — (через FB_PumpInterlockLad) | функция с возвратом `Ret_Val`, MOVE под условием |
| `DB_Process.xml` | DB 20 | DB, стандартный доступ | — | члены со смещениями `Offset`, реманентный член, член типа UDT |
| `UDT_Valve.xml` | UDT | тип данных PLC | — | структура для DB_Process |

## Логика блоков (нормативное описание)

### FB_Starter* — пускатель насоса (один блок на четырёх языках)

Интерфейс общий: входы `xStart`, `xStop` (TRUE — нажата), `xInterlock` (по умолчанию TRUE), `xFeedback`,
`tFeedbackTime` (по умолчанию T#2S), `xReset`; выходы `xRun`, `xFault`, `iStarts` (Int); статика `xRunMem`,
`xEdgeMem`, `tonFeedback` (TON_TIME).

1. Пуск/стоп — SR с битом-операндом `xRunMem`: S = `xStart AND xInterlock`; R1 = `xStop OR NOT xInterlock
   OR xFault`. SR S7: сначала S, затем R1 — при S = R1 = 1 (Пуск и Стоп одновременно) бит сброшен.
   `xRun := xRunMem`.
2. Контроль обратной связи: TON `tonFeedback` (IN = `xRun AND NOT xFeedback`, PT = `tFeedbackTime`).
3. Авария с самоподхватом: `xFault := (tonFeedback.Q OR xFault) AND NOT xReset`.
4. Счётчик пусков: по фронту `xRun` (бит памяти `xEdgeMem`) `iStarts := iStarts + 1`.

Сети выполняются по порядку 1–4; `xFault` в сети 1 — значение прошлого вызова.

### FB_PumpInterlockLad — блокировки насоса по уровню и давлению

1. `xLowLevel := iLevel_cm < iLevelMin_cm`. 2. `xHighPress := iPressure_kPa > iPressureMax_kPa`.
3. Если `xLowLevel OR xHighPress` — установить `xAlarmLatch` (S).
4. Если `xAck AND NOT xLowLevel AND NOT xHighPress` — сбросить `xAlarmLatch` (R).
5. Обслуживание: при `xMaint` прыжок вперёд к метке `NoAuto` — сети 6–7 не выполняются.
6. `xPumpOn := xAutoReq AND NOT xAlarmLatch`.
7. По фронту `xPumpOn` (PBox, бит `xRunEdge`): `iRunCount := iRunCount + 1` (ADD Int); `xCountOk` — ENO
   сложения (ENO = 0 при переполнении Int и при EN = 0).
8. Метка `NoAuto`: при `xMaint` сбросить `xPumpOn` (R).
9. При `xPumpOn` — три вызова `FC_ClampPctLad` через EN → ENO: `iStage1 := clamp(iLevel_cm, 0, 100)`,
   `iStage2 := clamp(iStage1, 10, 90)`, `iSetpoint_pct := clamp(iStage2, 20, 80)`; `xChainOk` — ENO третьего
   вызова.
10. При `NOT xPumpOn`: `iSetpoint_pct := 0` (MOVE).
11. `xAlarm := xAlarmLatch`. 12. `xRunMem := xRunEdge` — бит памяти фронта читается в другой сети.

`FC_ClampPctLad`: результат — `iIn`, ограниченный сверху `iMax`, затем снизу `iMin` (оба сравнения — с
исходным `iIn`); ENO блок не пишет, поэтому ENO = EN.

## Внешние образцы (`EXTERNAL.json`)

Приёмка разборщика на чужих экспортах: файлы скачиваются тестами в `.cache/lang/` с проверкой SHA-256, в
git не кладутся; без сети тест пропускается с сообщением.

| Образец | Лицензия | Версия TIA | Что внутри | Ожидаемый итог |
|---|---|---|---|---|
| bulaofen0036-coder/TIA_Portal_Openness_MCP, `lad-cookbook` | MIT | V21 | LAD: контакты, катушки, O, Not, PBox, TON, сравнения, Move, Add…Mod, Convert | без `RawBlock` и `MIGRATION-TODO` |
| asier-vega-gutierrez/Smart_Factory, `src/ProgramBlocks` | Apache-2.0 | V18 (`StatementList/v4`) | STL: A, =, FP, FN, CALL NORM_X/SCALE_X; глобальные DB | без `RawBlock` и `MIGRATION-TODO`; теги таблиц тегов (не скачиваются) — `sym.unknown` |

Схемы XSD V15.1–V21 — копии в dotnetprojects/DotNetSiemensPLCToolBoxLibrary (© Siemens AG, в git не
кладутся); используется V21 по коммиту `bbe5bec` с SHA-256 каждого файла.
