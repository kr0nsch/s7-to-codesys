// AUTO-GENERATED — не редактировать: s7conv gen-tests, сценарии scenarios/lang/FB_BackwashGraph.csv
// Правка — в CSV (scenarios/README.md), затем python -m s7conv build-corpus.
// Назначение: тесты поведения сконвертированного FB_BackwashGraph по сценариям CSV (сценариев: 6, строк: 46):
//             один метод-тест на сценарий, строки — по порядку с моделируемым временем GVL_S7Clock.
//             Ожидаемые значения — из CSV (эталонные модели по описанию логики блока), не из
//             результата конвертации.
// Автор:      s7conv 0.1.0 (сгенерировано)
// Версия:     не указана
// Документ:   scenarios/README.md, docs/methodology.md, раздел «Проверка поведения»
FUNCTION_BLOCK FB_BackwashGraph_ScenarioTest EXTENDS coUnit.FB_TestSuite
VAR
    fbLongWash : FB_BackwashGraph;  // свой экземпляр на сценарий
    xLongWashDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbShortWash : FB_BackwashGraph;  // свой экземпляр на сценарий
    xShortWashDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbSupervision : FB_BackwashGraph;  // свой экземпляр на сценарий
    xSupervisionDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbAckSwitches : FB_BackwashGraph;  // свой экземпляр на сценарий
    xAckSwitchesDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbInterlockPump : FB_BackwashGraph;  // свой экземпляр на сценарий
    xInterlockPumpDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbOffAndInit : FB_BackwashGraph;  // свой экземпляр на сценарий
    xOffAndInitDone : BOOL;  // сценарий выполнен (выполняется один раз)
END_VAR
