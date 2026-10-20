# Отчёт о тестировании

Результаты юнит-тестов CfUnit (coUnit 1.2.0.0) в CODESYS Control Win V3 и проверок без CODESYS.
Запись «проверено в CODESYS» появляется только после реального прогона.

<!-- cds:test-report:begin (раздел обновляет `python tools/codesys/cds.py report`) -->
## Последний прогон в CODESYS

Проверено в CODESYS 3.5.17.30 / CODESYS Control Win V3 (пользовательский процесс) — 2026-10-20 04:04:26. Итог: **все тесты пройдены**.

| Параметр | Значение |
|---|---|
| Дата прогона | 2026-10-20 04:04:26 |
| Коммит | 1a2db65 |
| CODESYS | 3.5.17.30 (профиль `CODESYS V3.5 SP17 Patch 3`) |
| Устройство в проекте | CODESYS Control Win V3 (4096 / 0000 0001 / 3.5.17.30) |
| Рантайм | CODESYS Control Win V3 (пользовательский процесс) |
| Фреймворк тестов | coUnit (CfUnit) 1.2.0.0 |
| Сборка | ошибок 0, предупреждений 0 |
| Способ запуска | `python tools/codesys/cds.py test` |

| Набор | Тестов | Пройдено | Упало | Пропущено | Итог |
|---|---|---|---|---|---|
| `PRG_Tests.fbF_NormXTest` | 8 | 8 | 0 | 0 | пройдено |
| `PRG_Tests.fbF_S7EnoTest` | 4 | 4 | 0 | 0 | пройдено |
| `PRG_Tests.fbF_S7NowTest` | 2 | 2 | 0 | 0 | пройдено |
| `PRG_Tests.fbF_ScaleXTest` | 8 | 8 | 0 | 0 | пройдено |
| `PRG_Tests.fbS7FTrigTest` | 3 | 3 | 0 | 0 | пройдено |
| `PRG_Tests.fbS7TofTest` | 4 | 4 | 0 | 0 | пройдено |
| `PRG_Tests.fbS7TonTest` | 7 | 7 | 0 | 0 | пройдено |
| `PRG_Tests.fbS7TpTest` | 3 | 3 | 0 | 0 | пройдено |
| `PRG_Tests.fbStandardCounterTest` | 4 | 4 | 0 | 0 | пройдено |
| `PRG_Tests.fbStandardFlipFlopTest` | 5 | 5 | 0 | 0 | пройдено |
| `PRG_Tests.fbPumpInterlockLad_ScenarioTest` | 5 | 5 | 0 | 0 | пройдено |
| `PRG_Tests.fbStarterFbd_ScenarioTest` | 9 | 9 | 0 | 0 | пройдено |
| `PRG_Tests.fbStarterLad_ScenarioTest` | 9 | 9 | 0 | 0 | пройдено |
| `PRG_Tests.fbStarterScl_ScenarioTest` | 9 | 9 | 0 | 0 | пройдено |
| `PRG_Tests.fbStarterStl_ScenarioTest` | 9 | 9 | 0 | 0 | пройдено |
| `PRG_Tests.fbAlarmDelay_ScenarioTest` | 8 | 8 | 0 | 0 | пройдено |
| `PRG_Tests.fbAnalogIn_ScenarioTest` | 6 | 6 | 0 | 0 | пройдено |
| `PRG_Tests.fbMotor_ScenarioTest` | 7 | 7 | 0 | 0 | пройдено |
| `PRG_Tests.fbPumpAlternation_ScenarioTest` | 6 | 6 | 0 | 0 | пройдено |
| `PRG_Tests.fbSequencer_ScenarioTest` | 6 | 6 | 0 | 0 | пройдено |
| `PRG_Tests.fbTotalizer_ScenarioTest` | 6 | 6 | 0 | 0 | пройдено |
| **Всего** | 128 | 128 | 0 | 0 | **пройдено** |

### Результаты тестов

| Набор | Тест | Итог |
|---|---|---|
| `PRG_Tests.fbF_NormXTest` | `MidRangeGivesHalf` | пройден |
| `PRG_Tests.fbF_NormXTest` | `AtMinGivesZero` | пройден |
| `PRG_Tests.fbF_NormXTest` | `AtMaxGivesOne` | пройден |
| `PRG_Tests.fbF_NormXTest` | `BelowMinExtrapolates` | пройден |
| `PRG_Tests.fbF_NormXTest` | `AboveMaxExtrapolates` | пройден |
| `PRG_Tests.fbF_NormXTest` | `OffsetRange` | пройден |
| `PRG_Tests.fbF_NormXTest` | `EqualBoundsGivesZero` | пройден |
| `PRG_Tests.fbF_NormXTest` | `ReversedBoundsKeepsFormula` | пройден |
| `PRG_Tests.fbF_S7EnoTest` | `AddIntOverflow` | пройден |
| `PRG_Tests.fbF_S7EnoTest` | `SubIntUnderflow` | пройден |
| `PRG_Tests.fbF_S7EnoTest` | `MulIntOverflow` | пройден |
| `PRG_Tests.fbF_S7EnoTest` | `DintLimits` | пройден |
| `PRG_Tests.fbF_S7NowTest` | `SimulationReturnsSimClock` | пройден |
| `PRG_Tests.fbF_S7NowTest` | `AdvancesLikeStandardTimer` | пройден |
| `PRG_Tests.fbF_ScaleXTest` | `HalfGivesMidRange` | пройден |
| `PRG_Tests.fbF_ScaleXTest` | `ZeroGivesMin` | пройден |
| `PRG_Tests.fbF_ScaleXTest` | `OneGivesMax` | пройден |
| `PRG_Tests.fbF_ScaleXTest` | `AboveOneExtrapolates` | пройден |
| `PRG_Tests.fbF_ScaleXTest` | `BelowZeroExtrapolates` | пройден |
| `PRG_Tests.fbF_ScaleXTest` | `NegativeLowBound` | пройден |
| `PRG_Tests.fbF_ScaleXTest` | `EqualBoundsGivesMin` | пройден |
| `PRG_Tests.fbF_ScaleXTest` | `ReversedBoundsKeepsFormula` | пройден |
| `PRG_Tests.fbS7FTrigTest` | `NoEdgeOnFirstCallWithClkFalse` | пройден |
| `PRG_Tests.fbS7FTrigTest` | `FallingEdgeOnce` | пройден |
| `PRG_Tests.fbS7FTrigTest` | `StandardFTrigMatchesS7` | пройден |
| `PRG_Tests.fbS7TofTest` | `HoldsThenDrops` | пройден |
| `PRG_Tests.fbS7TofTest` | `ReturnBeforeTimeout` | пройден |
| `PRG_Tests.fbS7TofTest` | `NoOutputBeforeFirstTrue` | пройден |
| `PRG_Tests.fbS7TofTest` | `MatchesStandardInRealTime` | пройден |
| `PRG_Tests.fbS7TonTest` | `CountsFromRisingEdge` | пройден |
| `PRG_Tests.fbS7TonTest` | `FirstCallWithInTrueStarts` | пройден |
| `PRG_Tests.fbS7TonTest` | `ResetWhenInFalse` | пройден |
| `PRG_Tests.fbS7TonTest` | `ZeroPtSwitchesImmediately` | пройден |
| `PRG_Tests.fbS7TonTest` | `SurvivesTimeWraparound` | пройден |
| `PRG_Tests.fbS7TonTest` | `KeepsQWhileInHeldAcrossWrap` | пройден |
| `PRG_Tests.fbS7TonTest` | `MatchesStandardInRealTime` | пройден |
| `PRG_Tests.fbS7TpTest` | `PulseOnRisingEdge` | пройден |
| `PRG_Tests.fbS7TpTest` | `RetriggerIgnored` | пройден |
| `PRG_Tests.fbS7TpTest` | `MatchesStandardInRealTime` | пройден |
| `PRG_Tests.fbStandardCounterTest` | `CtuCountsRisingEdges` | пройден |
| `PRG_Tests.fbStandardCounterTest` | `CtdStopsAtZero` | пройден |
| `PRG_Tests.fbStandardCounterTest` | `CtudResetBeatsLoad` | пройден |
| `PRG_Tests.fbStandardCounterTest` | `CtudBothEdgesSameCall` | пройден |
| `PRG_Tests.fbStandardFlipFlopTest` | `SrSetDominant` | пройден |
| `PRG_Tests.fbStandardFlipFlopTest` | `RsResetDominant` | пройден |
| `PRG_Tests.fbStandardFlipFlopTest` | `RsSetHeldReappliesAfterReset` | пройден |
| `PRG_Tests.fbStandardFlipFlopTest` | `S7SrResetDominantViaRs` | пройден |
| `PRG_Tests.fbStandardFlipFlopTest` | `S7RsSetDominantViaSr` | пройден |
| `PRG_Tests.fbPumpInterlockLad_ScenarioTest` | `AutoRunAndCount` | пройден |
| `PRG_Tests.fbPumpInterlockLad_ScenarioTest` | `LowLevelTripAndAck` | пройден |
| `PRG_Tests.fbPumpInterlockLad_ScenarioTest` | `HighPressure` | пройден |
| `PRG_Tests.fbPumpInterlockLad_ScenarioTest` | `MaintenanceJump` | пройден |
| `PRG_Tests.fbPumpInterlockLad_ScenarioTest` | `SetpointClamp` | пройден |
| `PRG_Tests.fbStarterFbd_ScenarioTest` | `StartStop` | пройден |
| `PRG_Tests.fbStarterFbd_ScenarioTest` | `StartAndStopTogether` | пройден |
| `PRG_Tests.fbStarterFbd_ScenarioTest` | `InterlockBlocksStart` | пройден |
| `PRG_Tests.fbStarterFbd_ScenarioTest` | `InterlockDropStops` | пройден |
| `PRG_Tests.fbStarterFbd_ScenarioTest` | `FeedbackOk` | пройден |
| `PRG_Tests.fbStarterFbd_ScenarioTest` | `FeedbackTimeout` | пройден |
| `PRG_Tests.fbStarterFbd_ScenarioTest` | `FaultResetAndBlock` | пройден |
| `PRG_Tests.fbStarterFbd_ScenarioTest` | `StartCounter` | пройден |
| `PRG_Tests.fbStarterFbd_ScenarioTest` | `ResetWhileRunning` | пройден |
| `PRG_Tests.fbStarterLad_ScenarioTest` | `StartStop` | пройден |
| `PRG_Tests.fbStarterLad_ScenarioTest` | `StartAndStopTogether` | пройден |
| `PRG_Tests.fbStarterLad_ScenarioTest` | `InterlockBlocksStart` | пройден |
| `PRG_Tests.fbStarterLad_ScenarioTest` | `InterlockDropStops` | пройден |
| `PRG_Tests.fbStarterLad_ScenarioTest` | `FeedbackOk` | пройден |
| `PRG_Tests.fbStarterLad_ScenarioTest` | `FeedbackTimeout` | пройден |
| `PRG_Tests.fbStarterLad_ScenarioTest` | `FaultResetAndBlock` | пройден |
| `PRG_Tests.fbStarterLad_ScenarioTest` | `StartCounter` | пройден |
| `PRG_Tests.fbStarterLad_ScenarioTest` | `ResetWhileRunning` | пройден |
| `PRG_Tests.fbStarterScl_ScenarioTest` | `StartStop` | пройден |
| `PRG_Tests.fbStarterScl_ScenarioTest` | `StartAndStopTogether` | пройден |
| `PRG_Tests.fbStarterScl_ScenarioTest` | `InterlockBlocksStart` | пройден |
| `PRG_Tests.fbStarterScl_ScenarioTest` | `InterlockDropStops` | пройден |
| `PRG_Tests.fbStarterScl_ScenarioTest` | `FeedbackOk` | пройден |
| `PRG_Tests.fbStarterScl_ScenarioTest` | `FeedbackTimeout` | пройден |
| `PRG_Tests.fbStarterScl_ScenarioTest` | `FaultResetAndBlock` | пройден |
| `PRG_Tests.fbStarterScl_ScenarioTest` | `StartCounter` | пройден |
| `PRG_Tests.fbStarterScl_ScenarioTest` | `ResetWhileRunning` | пройден |
| `PRG_Tests.fbStarterStl_ScenarioTest` | `StartStop` | пройден |
| `PRG_Tests.fbStarterStl_ScenarioTest` | `StartAndStopTogether` | пройден |
| `PRG_Tests.fbStarterStl_ScenarioTest` | `InterlockBlocksStart` | пройден |
| `PRG_Tests.fbStarterStl_ScenarioTest` | `InterlockDropStops` | пройден |
| `PRG_Tests.fbStarterStl_ScenarioTest` | `FeedbackOk` | пройден |
| `PRG_Tests.fbStarterStl_ScenarioTest` | `FeedbackTimeout` | пройден |
| `PRG_Tests.fbStarterStl_ScenarioTest` | `FaultResetAndBlock` | пройден |
| `PRG_Tests.fbStarterStl_ScenarioTest` | `StartCounter` | пройден |
| `PRG_Tests.fbStarterStl_ScenarioTest` | `ResetWhileRunning` | пройден |
| `PRG_Tests.fbAlarmDelay_ScenarioTest` | `ActivateAckClear` | пройден |
| `PRG_Tests.fbAlarmDelay_ScenarioTest` | `ClearedBeforeAck` | пройден |
| `PRG_Tests.fbAlarmDelay_ScenarioTest` | `ChatterSuppressed` | пройден |
| `PRG_Tests.fbAlarmDelay_ScenarioTest` | `ReturnDuringOffDelay` | пройден |
| `PRG_Tests.fbAlarmDelay_ScenarioTest` | `NewActivationAfterOffDelay` | пройден |
| `PRG_Tests.fbAlarmDelay_ScenarioTest` | `Disabled` | пройден |
| `PRG_Tests.fbAlarmDelay_ScenarioTest` | `AckSameCallAsActivation` | пройден |
| `PRG_Tests.fbAlarmDelay_ScenarioTest` | `AckHeldDuringActivation` | пройден |
| `PRG_Tests.fbAnalogIn_ScenarioTest` | `ScalingPoints` | пройден |
| `PRG_Tests.fbAnalogIn_ScenarioTest` | `HighLimitsHysteresis` | пройден |
| `PRG_Tests.fbAnalogIn_ScenarioTest` | `LowLimitsHysteresis` | пройден |
| `PRG_Tests.fbAnalogIn_ScenarioTest` | `ChannelDiagnostics` | пройден |
| `PRG_Tests.fbAnalogIn_ScenarioTest` | `Simulation` | пройден |
| `PRG_Tests.fbAnalogIn_ScenarioTest` | `CustomRanges` | пройден |
| `PRG_Tests.fbMotor_ScenarioTest` | `AutoStartOk` | пройден |
| `PRG_Tests.fbMotor_ScenarioTest` | `NoFeedbackTimeout` | пройден |
| `PRG_Tests.fbMotor_ScenarioTest` | `FeedbackLost` | пройден |
| `PRG_Tests.fbMotor_ScenarioTest` | `UnexpectedFeedback` | пройден |
| `PRG_Tests.fbMotor_ScenarioTest` | `ThermalTripManual` | пройден |
| `PRG_Tests.fbMotor_ScenarioTest` | `BumplessAutoToManual` | пройден |
| `PRG_Tests.fbMotor_ScenarioTest` | `CustomFeedbackTime` | пройден |
| `PRG_Tests.fbPumpAlternation_ScenarioTest` | `RotateOnStop` | пройден |
| `PRG_Tests.fbPumpAlternation_ScenarioTest` | `StandbyTakesOver` | пройден |
| `PRG_Tests.fbPumpAlternation_ScenarioTest` | `ForcedAlternate` | пройден |
| `PRG_Tests.fbPumpAlternation_ScenarioTest` | `RotateOnStopDisabled` | пройден |
| `PRG_Tests.fbPumpAlternation_ScenarioTest` | `NoPumpsAvailable` | пройден |
| `PRG_Tests.fbPumpAlternation_ScenarioTest` | `DemandClamped` | пройден |
| `PRG_Tests.fbSequencer_ScenarioTest` | `FullCycle` | пройден |
| `PRG_Tests.fbSequencer_ScenarioTest` | `DrainTimeout` | пройден |
| `PRG_Tests.fbSequencer_ScenarioTest` | `AbortByStop` | пройден |
| `PRG_Tests.fbSequencer_ScenarioTest` | `PermissiveMissing` | пройден |
| `PRG_Tests.fbSequencer_ScenarioTest` | `DrainTimeoutBoundary` | пройден |
| `PRG_Tests.fbSequencer_ScenarioTest` | `RefillTimeoutBoundary` | пройден |
| `PRG_Tests.fbTotalizer_ScenarioTest` | `IntegrationAndPulses` | пройден |
| `PRG_Tests.fbTotalizer_ScenarioTest` | `CutoffAndEnable` | пройден |
| `PRG_Tests.fbTotalizer_ScenarioTest` | `ResetLevel` | пройден |
| `PRG_Tests.fbTotalizer_ScenarioTest` | `VariableCycleTime` | пройден |
| `PRG_Tests.fbTotalizer_ScenarioTest` | `LargeStepPulsesCatchUp` | пройден |
| `PRG_Tests.fbTotalizer_ScenarioTest` | `PulseVolumeZero` | пройден |

### Упавшие тесты

_Нет._

Машиночитаемые результаты: `build/test-results.json`, `build/junit.xml` (не в git).
<!-- cds:test-report:end -->

## Прогон выпуска 1.1.0 (2026-10-20)

Все команды — на коммите `1a2db65` в чистом клоне репозитория (каталог `s7-to-codesys`, `build/` с нуля).
CODESYS 3.5.17.30, CODESYS Control Win V3 в пользовательском процессе, coUnit 1.2.0.0; Astra.IDE 1.7.2.2.
Итоги взяты из файлов прогона в `build/` (в git не хранятся).

| Команда `python tools/codesys/cds.py …` | Среда и устройство | Итог |
|---|---|---|
| `build` | CODESYS 3.5.17.30, Control Win V3 (4096 / `0000 0001` / 3.5.17.30) | импорт: создано 63 объекта; ошибок 0, предупреждений 0 |
| `check --tests` | CODESYS 3.5.17.30, пул без устройства | объектов 76 (`src/` и `tests/`, оба корпуса), ошибок 0, предупреждений 0 |
| `test --clean` | CODESYS 3.5.17.30, Control Win V3 | импорт: создано 217 объектов; сборка 0/0; 21 набор, 128 тестов: пройдено 128, упало 0 (раздел «Последний прогон в CODESYS» выше) |
| `check` с `CODESYS_EXE` = Astra.IDE, `CDS_DEVICE_*` = 4096 / `109B 0008` / 11.7.2.60 | Astra.IDE 1.7.2.2 (профиль `Astra.IDE_V1.7.2.2`), REGUL R500 | объектов 54 (`src/`), ошибок 0, предупреждений 0 |
| `check` с `CDS_DEVICE_*` = 4096 / `1628 0083` / 3.5.17.35 | CODESYS 3.5.17.30 с таргет-файлами ОВЕН, ПЛК210; библиотека устройства OwenStorage 3.5.17.33 | объектов 54 (`src/`), ошибок 0, предупреждений 0 |

Что нового по сравнению с 1.0.0:

- Наборы корпуса всех языков `FB_StarterLad/Fbd/Stl/Scl_ScenarioTest` (по 9 сценариев — один и тот же
  `FB_Starter.csv`) и `FB_PumpInterlockLad_ScenarioTest` (5) — 41 тест; все пройдены.
- Рукописные наборы S7Compat: `FB_StandardFlipFlop_Test` (5: SR/RS Standard по уровню, перевод S7 SR → RS и
  S7 RS → SR при `S = R = 1`), `FB_StandardCounter_Test` (4: CTU/CTD/CTUD, одновременные фронты CU и CD),
  `FB_F_S7Eno_Test` (4: ENO сложения, вычитания и умножения INT/DINT на границах).
- Под R500 и ПЛК210 — компиляция всех объектов `src/`; загрузка на ПЛК и прогон тестов coUnit на этих
  устройствах не выполнялись.

Отдельно проверена копия репозитория для своего проекта (README, «Как использовать в своём проекте», шаг 7):
учебный набор SCL вместо обоих демокорпусов — `check --tests` 34 объекта 0/0, `test` 11 наборов и 55 тестов
пройдены, `build` — ошибка «Не задано ни одной задачи» (в учебном наборе нет OB, ожидаемо); один блок
SimaticML вместо корпуса всех языков — `check --tests` 64 объекта 0/0.

## Повторный прогон перед выпуском (2026-10-19)

Перед выпуском 1.0.0 повторены две команды — тот же CODESYS 3.5.17.30, CODESYS Control Win V3 и coUnit
1.2.0.0. Итоги взяты из файлов прогона в `build/` (в git не хранятся).

| Команда `python tools/codesys/cds.py …` | Что проверяет | Итог |
|---|---|---|
| `check --tests` (14:39) | компиляция всех объектов `src/` (40) и `tests/` (14) в пуле проекта без устройства, в том числе объектов без задачи и без вызовов | объектов 54, ошибок 0, предупреждений 0 (`build/check.log`, `build/check.json`) |
| `test --clean` (14:43) | тестовый проект с нуля, загрузка в Control Win, прогон coUnit | импорт: создано 138 объектов, обновлено 0; сборка — 0 ошибок, 0 предупреждений; 13 наборов, 74 теста: пройдено 74, упало 0 (раздел «Последний прогон в CODESYS» выше) |

В `build/test-results.json` команда записана как `python tools/codesys/cds.py test`: это поле `cds.py` пишет
без ключей. Что проект собран с нуля, видно по итогу импорта. Тот же прогон снят в GIF README.

## Сборка и прогон в CODESYS (2026-10-16)

CODESYS 3.5.17.30 (32 бит, сборка ОВЕН), CODESYS Control Win V3 в пользовательском процессе, coUnit 1.2.0.0,
Standard 3.5.17.0. Все команды — `python tools/codesys/cds.py ...`; результаты ниже — их фактический вывод.

| Команда | Что проверяет | Итог |
|---|---|---|
| `build` | рабочий проект: `src/` (сконвертированный корпус и S7Compat), задачи `MainTask` 10 мс (`PRG_Startup`, `PRG_Main`) и `Task_OB30` 100 мс (`PRG_Cyclic_interrupt`) из `config.json` | ошибок 0, предупреждений 0 |
| `library` | «Проверить все объекты пула» — 39 объектов `src/` (все, кроме `PRG_Main`, который компилирует `build`). Нужна потому, что сборка приложения компилирует только объекты, достижимые из задач, а `PRG_Diagnostic_error_interrupt` (OB82) задачи не имеет | ошибок 0, предупреждений 0 |
| `build --tests` | тестовый проект: `src/` и `tests/`, coUnit | ошибок 0, предупреждений 0 |
| `test` | загрузка в Control Win, `TestTask` 10 мс, опрос coUnit | 13 наборов, 74 теста: пройдено 74, упало 0, пропущено 0; все наборы завершились за 1,2 с |
| `roundtrip` | импорт в чистый проект → экспорт → сравнение с `src/` и `tests/`; повторный импорт после открытия с диска | 242 файла совпадают побайтно; 0 изменений |

Что значит «0 предупреждений» — [STATIC_ANALYSIS.md](STATIC_ANALYSIS.md), раздел «Компилятор CODESYS»: зонд
показал, что неявная смена знака даёт предупреждение C0195, а неявное сужение (DINT → INT, REAL → INT) в
3.5.17 — ошибку C0032, так что пропустить такие преобразования молча сборка не может.

**Первая сборка — 89 ошибок** (`Неизвестный тип: 'R_TRIG'`, `'TON'`, `'CTU'`, `Идентификатор 'CONCAT' не
задан`): в `tools/codesys/config.json` шаблона нет ссылки на библиотеку Standard. Добавлен плейсхолдер
`Standard` в `library.libraries` (ключ `standard`; так рекомендует `tools/README.md` для библиотек, которые
разрешает профиль) — он подключается к рабочему и тестовому проектам и к проверке пула. Ошибок в
сконвертированном коде сборка не нашла.

### Повторная проверка с чистого `build/`

Независимый повтор того же дня: каталог `build/` удалён, команды выполнены заново в том же порядке —
`build` (импорт 47 объектов), `library` (39 объектов), `build --tests` (импорт 138 объектов), `test`,
`roundtrip`. Итоги совпали с таблицей выше: 0 ошибок и 0 предупреждений во всех трёх компиляциях, 13 наборов
и 74 теста — все пройдены, все наборы завершились за 1,2 с, roundtrip — 242 файла побайтно, повторный
импорт — 0 изменений. Плейсхолдер `#Standard` в собранном тестовом проекте разрешён в
`Standard, 3.5.17.0 (System)` («Разрешено профилем библиотеки» — `effective_resolution` и `resolution_info`
ссылки, прочитанные скриптом CODESYS); это та версия, на которой проверен `F_TRIG`.

Зонды повтора — в копии репозитория во временном каталоге (в репозиторий не входят):

| Что сделано в копии | Результат CODESYS 3.5.17.30 | Что подтверждает |
|---|---|---|
| в `PRG_Diagnostic_error_interrupt` (OB82, без задачи) добавлена строка `DB_Plant.diagCount := T#1S;` | `build` этой ошибки не видит; `library` — `Error C0032` с файлом и строкой раскладки (`PRG_Diagnostic_error_interrupt.impl.st:7`) | без проверки пула объект без задачи не компилируется; `build` + `library` вместе покрывают весь `src/` |
| новая программа, вызванная из `PRG_Main`: `wY := iX;` (INT → WORD), `iX := diZ;` (DINT → INT), неиспользуемая `iUnused` | `Warning C0195`, `Error C0032`; о неиспользуемой переменной сообщения нет | выводы раздела «Компилятор CODESYS» в STATIC_ANALYSIS.md; `cds.py` показывает предупреждения, а не только ошибки |
| программа-обработчик пишет стартовую информацию в `PRG_Diagnostic_error_interrupt.Channel := 3;` (тогда — `VAR` программы) | `Error C0037` «'Channel' не является входом 'PRG_Diagnostic_error_interrupt'» — в `VAR` программы извне записать нельзя | конвертер исправлен: у событийного OB стартовая информация остаётся `VAR_INPUT` (пометка `ob.start_info`), см. ниже |
| после исправления: `PRG_Diagnostic_error_interrupt(IO_State := 16#0001, Channel := 3, MultiError := FALSE);` из программы-обработчика | `build`: 0 ошибок, 0 предупреждений | обработчик события передаёт стартовую информацию OB82, не трогая сгенерированный код (MANUAL_STEPS.md, 4.1) |
| GVL с `VAR_GLOBAL PERSISTENT RETAIN` (как даёт `s7conv --retain persistent`), объекта Persistent Variables в приложении нет | `Warning C0244` «Приложение не содержит VAR_PERSISTENT-списка для ввода экземпляра пути для переменной GVL_PersistProbe.diProbe» | текст пометки `db.persistent` и MAPPING.md уточнены; корпус собирается с `RETAIN`, поэтому в его сборке этого предупреждения нет |
| ожидания изменены в других строках, чем в первом эксперименте: `FB_AlarmDelay/ActivateAckClear#4 active` (строка `boundary` ровно на `onDelay`) и `FB_Motor/AutoStartOk#3 status.startCount`; тесты пересобраны `s7conv build-corpus` | `test`: пройдено 72, упало 2 — ровно эти тесты с сообщениями `ActivateAckClear#4 active` и `AutoStartOk#3 status.startCount` | проверки сценариев не пустые, включая строку на пороге таймера |

**Исправление по итогам повтора.** Конвертер объявлял стартовую информацию всех OB как `VAR`, и у
OB82 её нельзя было передать без правки сгенерированного кода (C0037 выше). Теперь у событийных OB она
остаётся `VAR_INPUT` (`s7conv/emitter.py`, тест `test_event_ob_start_info_stays_input`); у циклических OB и
OB100 — по-прежнему `VAR` (их вызывает задача, а `Initial_Call` эмулируется в самой программе). Корпус
пересобран `s7conv build-corpus` — изменилось только объявление `PRG_Diagnostic_error_interrupt` и текст
пометки в отчёте конвертации; число конструкций и статусы прежние (942 / 26 / 30). После этого `build`,
`library`, `build --tests`, `test` и `roundtrip` выполнены заново — итоги те же (раздел «Последний прогон»).

### Лимиты coUnit и время цикла

| Что | Значение | Вывод |
|---|---|---|
| проверок в наборе, максимум | 470 (`FB_AnalogIn_ScenarioTest`); лимит coUnit 1.2.0.0 — 1000 (`MaxNumberOfAssertsForEachTestSuite`) | наборы делить не нужно; генератор теперь отказывается выпускать набор с проверками больше 900 или тестами больше 100 (`s7conv/testgen.py`, `_check_counit_limits`): библиотека свои лимиты не проверяет |
| тестов в наборе, максимум | 8; лимит — 100 | — |
| длительность цикла `TestTask` (зонд, см. ниже) | максимум за 149 циклов — 3 мс, первый цикл — 3 мс (`TIME()`, разрешение 1 мс); все 39 сценариев (1895 проверок) выполняются в одном цикле | в цикл 10 мс укладывается с запасом; исключений в рантайме нет (все наборы завершились, результаты прочитаны); сторожевой таймер задачи `cds.py` не включает |

**Контрольные эксперименты** (в копии репозитория во временном каталоге — в репозиторий не входят):

- *отрицательный контроль*: в копии изменены ожидания в последних строках CSV двух самых больших наборов
  (`FB_AnalogIn/CustomRanges#6 statusWord`, `FB_Sequencer/RefillTimeoutBoundary#8 stepText`), тесты
  пересобраны `s7conv build-corpus`. CODESYS показал ровно эти два падения с этими сообщениями — последние
  проверки самых больших наборов выполняются и доходят до отчёта;
- *зонд времени цикла*: в `PRG_Tests` копии замерялось время `coUnit.RUN()` по `TIME()`, итог выводился
  сообщением намеренно падающего теста: `first=T#3ms max=T#3ms cycles=149`.

Сообщение о падении coUnit содержит только текст `Message` (без Expected/Actual) — поэтому у каждой
проверки сценария уникальное сообщение `Сценарий#строка путь`.

## Разбор результатов первого прогона

До прогона были открыты три вопроса (раздел «Что ожидать при первом прогоне» прежней версии отчёта).

| Вопрос | Результат в CODESYS | Решение |
|---|---|---|
| Даёт ли `F_TRIG` CODESYS Standard ложный спад на первом вызове с `CLK = FALSE` (S4, K18) | **нет**: строка 1 сценария `FB_PumpAlternation/RotateOnStop` прошла (`leadPump` = 1); добавлен прямой тест `FB_S7FTrig_Test.StandardFTrigMatchesS7` (Standard.F_TRIG и `FB_S7FTrig` на одних входах, начиная с первого вызова) — прошёл | семантика `F_TRIG` Standard 3.5.17.0 совпадает с S7; корпус остаётся со Standard `F_TRIG`, `--f-trig s7compat` не нужен. Пометка `fb.f_trig` остаётся `MIGRATION-CHECK`, но её текст называет проверенную версию и тест, который нужно повторить на другой версии Standard (MAPPING.md) |
| Совпадают ли таймеры S7Compat со Standard в реальном времени (K19) | `MatchesStandardInRealTime` (TON, TOF, TP) и `AdvancesLikeStandardTimer` прошли: ET расходится не больше 5 мс, Q — только на пороге PT | подтверждено в той части, которую сравнивают тесты; поведение при смене PT во время отсчёта по-прежнему не сравнивалось |
| Вызывает ли раннер coUnit тесты каждый цикл до `TEST_FINISHED()` (C10) | тесты на несколько циклов завершились (~700 мс), сценарии выполнились один раз | подтверждено |

Расхождений сконвертированного кода с эталонными моделями нет: все 39 сценариев прошли с первого прогона;
ни модели, ни ожидания не менялись, и по итогам сценариев не менялся конвертер (его единственное
исправление на этом этапе — стартовая информация событийных OB, найдено зондом, раздел «Повторная
проверка с чистого `build/`»).

## stsim и CODESYS

Интерпретатор ST в тестах конвертера (`s7conv/tests/stsim.py`) — модель CODESYS. Сравнение по каждому тесту
(coUnit отдаёт итог по тесту; число проверок по тесту через `read_value` не читается):

| Что | stsim (pytest) | CODESYS Control Win | Совпадает |
|---|---|---|---|
| 39 сценариев, F_TRIG с семантикой S7 | 39 из 39 пройдены (1895 проверок, каждая ровно один раз) | 39 из 39 пройдены | да, по каждому сценарию |
| гипотеза «ложный спад F_TRIG на первом вызове» (`F_TRIG_IEC_M_FALSE`) | падают `RotateOnStop` и `StandardFTrigMatchesS7` | оба проходят | CODESYS ведёт себя как модель с семантикой S7 (`F_TRIG_S7`, по умолчанию в stsim); гипотеза отвергнута |
| 7 рукописных наборов S7Compat (35 тестов) | пройдены; тесты в реальном времени — с моделью таймеров Standard по МЭК | пройдены с настоящими TON/TOF/TP Standard | да |

Вывод: на всём корпусе сценариев stsim и CODESYS дают одинаковый итог; единственная неопределённость
модели (начальное состояние F_TRIG) закрыта прогоном. stsim остаётся предварительной проверкой в CI, где
CODESYS нет; окончательный результат — прогон в Control Win.

## Наборы тестов

13 наборов, 74 теста, 2026 проверок. Все наборы объявлены в `tests/POUs/PRG_Tests` (генерируется
`s7conv build-corpus` вместе с тестами сценариев; рукописные наборы находятся по `EXTENDS
coUnit.FB_TestSuite`). Итог — последний прогон в CODESYS (раздел выше).

| Набор | Папка | Тестов | Проверок | Что проверяет | Итог |
|---|---|---:|---:|---|---|
| `FB_F_NormX_Test` | `tests/POUs/S7Compat` | 8 | 8 | `F_NormX` по формуле Siemens NORM_X: середина, границы, вне диапазона, обратный и вырожденный диапазон | пройдено |
| `FB_F_ScaleX_Test` | `tests/POUs/S7Compat` | 8 | 8 | `F_ScaleX` по формуле SCALE_X | пройдено |
| `FB_S7Ton_Test` | `tests/POUs/S7Compat` | 7 | 48 | `FB_S7Ton`: отсчёт с фронта и с первого вызова, Q ровно на PT, насыщение ET, сброс, PT = 0, переход TIME через 2³² мс, Q при IN = TRUE дольше 2³² мс (`KeepsQWhileInHeldAcrossWrap`, добавлен ревью); `MatchesStandardInRealTime` — совпадение со Standard.TON в реальном времени (~700 мс) | пройдено |
| `FB_S7Tof_Test` | `tests/POUs/S7Compat` | 4 | 28 | `FB_S7Tof`: отсчёт со спада, порог PT, возврат IN раньше PT, выход до первого TRUE; совпадение со Standard.TOF | пройдено |
| `FB_S7Tp_Test` | `tests/POUs/S7Compat` | 3 | 24 | `FB_S7Tp`: импульс по фронту, порог PT, ET после импульса, фронты во время импульса; совпадение со Standard.TP | пройдено |
| `FB_S7FTrig_Test` | `tests/POUs/S7Compat` | 3 | 13 | `FB_S7FTrig`: нет спада на первом вызове с CLK = FALSE, спад ровно на одном вызове; `StandardFTrigMatchesS7` — Standard.F_TRIG на тех же входах (характеризация платформы) | пройдено |
| `FB_F_S7Now_Test` | `tests/POUs/S7Compat` | 2 | 2 | `F_S7Now`: моделируемые часы; в реальном времени идёт как ET Standard.TON (~300 мс) | пройдено |
| `FB_AlarmDelay_ScenarioTest` | `tests/POUs/Scenarios` | 8 | 275 | `scenarios/FB_AlarmDelay.csv`: задержки появления и снятия, квитирование по фронту, состояния, вывод из работы | пройдено |
| `FB_AnalogIn_ScenarioTest` | `tests/POUs/Scenarios` | 6 | 470 | `scenarios/FB_AnalogIn.csv`: NORM_X/SCALE_X, зоны перегрузки, неисправность канала, гистерезис уставок, имитация, слово состояния | пройдено |
| `FB_Motor_ScenarioTest` | `tests/POUs/Scenarios` | 7 | 364 | `scenarios/FB_Motor.csv`: авто/ручной, контроль обратной связи (TON), коды аварий, сброс, счётчик пусков | пройдено |
| `FB_PumpAlternation_ScenarioTest` | `tests/POUs/Scenarios` | 6 | 186 | `scenarios/FB_PumpAlternation.csv`: смена ведущего (R_TRIG, F_TRIG), подхват резервным, нехватка | пройдено |
| `FB_Sequencer_ScenarioTest` | `tests/POUs/Scenarios` | 6 | 420 | `scenarios/FB_Sequencer.csv`: шаги CASE, переходы по времени (ET таймера) и уровням, аварии по времени, `STRING` | пройдено |
| `FB_Totalizer_ScenarioTest` | `tests/POUs/Scenarios` | 6 | 180 | `scenarios/FB_Totalizer.csv`: интегрирование LREAL, отсечка, сброс, импульсы | пройдено |

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
| `FB_S7FTrig_Test` при той же гипотезе | падает только `StandardFTrigMatchesS7` (`Standard F_TRIG, first call CLK=FALSE: no edge`); при семантике S7 проходит |
| 7 рукописных наборов S7Compat, 100 циклов по 10 мс (тесты в реальном времени — с моделью Standard по МЭК) | все проходят и завершаются |
| мутации логики: `FB_Motor`, `FB_AlarmDelay` (счёт и квитирование уровнем), `FB_AnalogIn` (гистерезис), порог `FB_S7Ton` (`>=` → `>`) | каждая роняет тесты |
| `FB_S7Ton` 0.1.0 (разность «сейчас − старт») против нового теста `KeepsQWhileInHeldAcrossWrap` | тест падал (`after wrap Q: Expected True, Actual False`) — ошибка найдена ревью; `FB_S7Ton` 0.2.0 проходит |

## Упавшие тесты

Нет: в последнем прогоне (и в первом, до добавления `StandardFTrigMatchesS7`, — 73 из 73) упавших тестов
нет. Падения в контрольном эксперименте вызваны намеренно и описаны выше.

## Проверки без CODESYS

| Проверка | Итог | Примечание |
|---|---|---|
| `ruff check`, `ruff format --check`, `mypy` | пройдено, 2026-10-19, локально | mypy strict: 63 файла |
| `pytest` | пройдено, 2026-10-19, локально | 1030 тестов, пропущенных нет; тесты шаблона — все, без `--deselect` (STATIC_ANALYSIS.md, «Тесты шаблона»), включая интеграционные с настоящими `plc` и iec_checker |
| `python -m s7conv build-corpus --check` | пройдено, 2026-10-16, локально | `src/*/Converted`, отчёт, задачи в `config.json`, тесты сценариев воспроизводятся побайтно |
| `python -m s7conv gen-tests scenarios --out tests --check` | пройдено, 2026-10-16, локально | 6 наборов, 39 тестов, 1895 проверок |
| `tools/assemble.py --tests` | пройдено, 2026-10-16, локально | 54 объекта `src/` и `tests/` |
| `tools/check/st_lint.py --strict` | пройдено, 2026-10-16, локально | 242 файла, 0 замечаний |
| iec_checker 0.4 (`run_iec_checker.py --tests`) | пройдено, 2026-10-16, локально | `ParserError` 0, необоснованных 0, обоснованных 962, артефактов сборки 163 — [STATIC_ANALYSIS.md](STATIC_ANALYSIS.md) |
| RuSTy 1.0.6 (`run_rusty.py`) | пройдено, 2026-10-16, локально | 51 файл (3 исключены, причины — STATIC_ANALYSIS.md), 0 ошибок; весь `src/` и `tests/` (у `GVL_Markers` без `AT`) — в pytest |
