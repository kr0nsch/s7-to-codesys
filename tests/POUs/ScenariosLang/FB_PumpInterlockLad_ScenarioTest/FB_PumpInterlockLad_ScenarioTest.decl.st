// AUTO-GENERATED — не редактировать: s7conv gen-tests, сценарии scenarios/lang/FB_PumpInterlockLad.csv
// Правка — в CSV (scenarios/README.md), затем python -m s7conv build-corpus.
// Назначение: тесты поведения сконвертированного FB_PumpInterlockLad по сценариям CSV (сценариев: 5, строк: 25):
//             один метод-тест на сценарий, строки — по порядку с моделируемым временем GVL_S7Clock.
//             Ожидаемые значения — из CSV (эталонные модели по описанию логики блока), не из
//             результата конвертации.
// Автор:      s7conv 0.1.0 (сгенерировано)
// Версия:     не указана
// Документ:   scenarios/README.md, docs/methodology.md, раздел «Проверка поведения»
FUNCTION_BLOCK FB_PumpInterlockLad_ScenarioTest EXTENDS coUnit.FB_TestSuite
VAR
    fbAutoRunAndCount : FB_PumpInterlockLad;  // свой экземпляр на сценарий
    xAutoRunAndCountDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbLowLevelTripAndAck : FB_PumpInterlockLad;  // свой экземпляр на сценарий
    xLowLevelTripAndAckDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbHighPressure : FB_PumpInterlockLad;  // свой экземпляр на сценарий
    xHighPressureDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbMaintenanceJump : FB_PumpInterlockLad;  // свой экземпляр на сценарий
    xMaintenanceJumpDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbSetpointClamp : FB_PumpInterlockLad;  // свой экземпляр на сценарий
    xSetpointClampDone : BOOL;  // сценарий выполнен (выполняется один раз)
END_VAR
