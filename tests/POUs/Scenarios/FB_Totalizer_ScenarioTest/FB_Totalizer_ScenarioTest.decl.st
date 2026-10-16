// AUTO-GENERATED — не редактировать: s7conv gen-tests, сценарии scenarios/FB_Totalizer.csv
// Правка — в CSV (scenarios/README.md), затем python -m s7conv build-corpus.
// Назначение: тесты поведения сконвертированного FB_Totalizer по сценариям CSV (сценариев: 6, строк: 36):
//             один метод-тест на сценарий, строки — по порядку с моделируемым временем GVL_S7Clock.
//             Ожидаемые значения — из CSV (эталонные модели по описанию логики блока), не из
//             результата конвертации.
// Автор:      s7conv 0.1.0 (сгенерировано)
// Версия:     не указана
// Документ:   scenarios/README.md, docs/methodology.md, раздел «Проверка поведения»
FUNCTION_BLOCK FB_Totalizer_ScenarioTest EXTENDS coUnit.FB_TestSuite
VAR
    fbIntegrationAndPulses : FB_Totalizer;  // свой экземпляр на сценарий
    xIntegrationAndPulsesDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbCutoffAndEnable : FB_Totalizer;  // свой экземпляр на сценарий
    xCutoffAndEnableDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbResetLevel : FB_Totalizer;  // свой экземпляр на сценарий
    xResetLevelDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbVariableCycleTime : FB_Totalizer;  // свой экземпляр на сценарий
    xVariableCycleTimeDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbLargeStepPulsesCatchUp : FB_Totalizer;  // свой экземпляр на сценарий
    xLargeStepPulsesCatchUpDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbPulseVolumeZero : FB_Totalizer;  // свой экземпляр на сценарий
    xPulseVolumeZeroDone : BOOL;  // сценарий выполнен (выполняется один раз)
END_VAR
