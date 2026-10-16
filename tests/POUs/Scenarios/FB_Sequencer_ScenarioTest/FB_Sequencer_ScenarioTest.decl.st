// AUTO-GENERATED — не редактировать: s7conv gen-tests, сценарии scenarios/FB_Sequencer.csv
// Правка — в CSV (scenarios/README.md), затем python -m s7conv build-corpus.
// Назначение: тесты поведения сконвертированного FB_Sequencer по сценариям CSV (сценариев: 6, строк: 42):
//             один метод-тест на сценарий, строки — по порядку с моделируемым временем GVL_S7Clock.
//             Ожидаемые значения — из CSV (эталонные модели по описанию логики блока), не из
//             результата конвертации.
// Автор:      s7conv 0.1.0 (сгенерировано)
// Версия:     не указана
// Документ:   scenarios/README.md, docs/methodology.md, раздел «Проверка поведения»
FUNCTION_BLOCK FB_Sequencer_ScenarioTest EXTENDS coUnit.FB_TestSuite
VAR
    fbFullCycle : FB_Sequencer;  // свой экземпляр на сценарий
    xFullCycleDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbDrainTimeout : FB_Sequencer;  // свой экземпляр на сценарий
    xDrainTimeoutDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbAbortByStop : FB_Sequencer;  // свой экземпляр на сценарий
    xAbortByStopDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbPermissiveMissing : FB_Sequencer;  // свой экземпляр на сценарий
    xPermissiveMissingDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbDrainTimeoutBoundary : FB_Sequencer;  // свой экземпляр на сценарий
    xDrainTimeoutBoundaryDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbRefillTimeoutBoundary : FB_Sequencer;  // свой экземпляр на сценарий
    xRefillTimeoutBoundaryDone : BOOL;  // сценарий выполнен (выполняется один раз)
END_VAR
