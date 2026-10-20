// AUTO-GENERATED — не редактировать: s7conv gen-tests, сценарии scenarios/lang/FB_Starter.csv
// Правка — в CSV (scenarios/README.md), затем python -m s7conv build-corpus.
// Назначение: тесты поведения сконвертированного FB_StarterStl по сценариям CSV (сценариев: 9, строк: 47):
//             один метод-тест на сценарий, строки — по порядку с моделируемым временем GVL_S7Clock.
//             Ожидаемые значения — из CSV (эталонные модели по описанию логики блока), не из
//             результата конвертации.
// Автор:      s7conv 0.1.0 (сгенерировано)
// Версия:     не указана
// Документ:   scenarios/README.md, docs/methodology.md, раздел «Проверка поведения»
FUNCTION_BLOCK FB_StarterStl_ScenarioTest EXTENDS coUnit.FB_TestSuite
VAR
    fbStartStop : FB_StarterStl;  // свой экземпляр на сценарий
    xStartStopDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbStartAndStopTogether : FB_StarterStl;  // свой экземпляр на сценарий
    xStartAndStopTogetherDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbInterlockBlocksStart : FB_StarterStl;  // свой экземпляр на сценарий
    xInterlockBlocksStartDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbInterlockDropStops : FB_StarterStl;  // свой экземпляр на сценарий
    xInterlockDropStopsDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbFeedbackOk : FB_StarterStl;  // свой экземпляр на сценарий
    xFeedbackOkDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbFeedbackTimeout : FB_StarterStl;  // свой экземпляр на сценарий
    xFeedbackTimeoutDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbFaultResetAndBlock : FB_StarterStl;  // свой экземпляр на сценарий
    xFaultResetAndBlockDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbStartCounter : FB_StarterStl;  // свой экземпляр на сценарий
    xStartCounterDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbResetWhileRunning : FB_StarterStl;  // свой экземпляр на сценарий
    xResetWhileRunningDone : BOOL;  // сценарий выполнен (выполняется один раз)
END_VAR
