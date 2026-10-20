// AUTO-GENERATED — не редактировать: s7conv gen-tests, сценарии scenarios/lang/FB_ConveyorStl.csv
// Правка — в CSV (scenarios/README.md), затем python -m s7conv build-corpus.
// Назначение: тесты поведения сконвертированного FB_ConveyorStl по сценариям CSV (сценариев: 7, строк: 58):
//             один метод-тест на сценарий, строки — по порядку с моделируемым временем GVL_S7Clock.
//             Ожидаемые значения — из CSV (эталонные модели по описанию логики блока), не из
//             результата конвертации.
// Автор:      s7conv 0.1.0 (сгенерировано)
// Версия:     не указана
// Документ:   scenarios/README.md, docs/methodology.md, раздел «Проверка поведения»
FUNCTION_BLOCK FB_ConveyorStl_ScenarioTest EXTENDS coUnit.FB_TestSuite
VAR
    fbStartSequence : FB_ConveyorStl;  // свой экземпляр на сценарий
    xStartSequenceDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbStopRunOut : FB_ConveyorStl;  // свой экземпляр на сценарий
    xStopRunOutDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbJamWithoutProducts : FB_ConveyorStl;  // свой экземпляр на сценарий
    xJamWithoutProductsDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbProductsKeepFlow : FB_ConveyorStl;  // свой экземпляр на сценарий
    xProductsKeepFlowDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbCountResetIsLevel : FB_ConveyorStl;  // свой экземпляр на сценарий
    xCountResetIsLevelDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbHornCutShort : FB_ConveyorStl;  // свой экземпляр на сценарий
    xHornCutShortDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbAckRestartsFlowWatch : FB_ConveyorStl;  // свой экземпляр на сценарий
    xAckRestartsFlowWatchDone : BOOL;  // сценарий выполнен (выполняется один раз)
END_VAR
