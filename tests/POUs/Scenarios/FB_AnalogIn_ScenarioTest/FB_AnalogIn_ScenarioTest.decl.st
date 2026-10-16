// AUTO-GENERATED — не редактировать: s7conv gen-tests, сценарии scenarios/FB_AnalogIn.csv
// Правка — в CSV (scenarios/README.md), затем python -m s7conv build-corpus.
// Назначение: тесты поведения сконвертированного FB_AnalogIn по сценариям CSV (сценариев: 6, строк: 47):
//             один метод-тест на сценарий, строки — по порядку с моделируемым временем GVL_S7Clock.
//             Ожидаемые значения — из CSV (эталонные модели по описанию логики блока), не из
//             результата конвертации.
// Автор:      s7conv 0.1.0 (сгенерировано)
// Версия:     не указана
// Документ:   scenarios/README.md, docs/methodology.md, раздел «Проверка поведения»
FUNCTION_BLOCK FB_AnalogIn_ScenarioTest EXTENDS coUnit.FB_TestSuite
VAR
    fbScalingPoints : FB_AnalogIn;  // свой экземпляр на сценарий
    xScalingPointsDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbHighLimitsHysteresis : FB_AnalogIn;  // свой экземпляр на сценарий
    xHighLimitsHysteresisDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbLowLimitsHysteresis : FB_AnalogIn;  // свой экземпляр на сценарий
    xLowLimitsHysteresisDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbChannelDiagnostics : FB_AnalogIn;  // свой экземпляр на сценарий
    xChannelDiagnosticsDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbSimulation : FB_AnalogIn;  // свой экземпляр на сценарий
    xSimulationDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbCustomRanges : FB_AnalogIn;  // свой экземпляр на сценарий
    xCustomRangesDone : BOOL;  // сценарий выполнен (выполняется один раз)
END_VAR
