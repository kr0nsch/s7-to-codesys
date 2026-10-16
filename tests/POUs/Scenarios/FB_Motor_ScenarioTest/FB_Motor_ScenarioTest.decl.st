// AUTO-GENERATED — не редактировать: s7conv gen-tests, сценарии scenarios/FB_Motor.csv
// Правка — в CSV (scenarios/README.md), затем python -m s7conv build-corpus.
// Назначение: тесты поведения сконвертированного FB_Motor по сценариям CSV (сценариев: 7, строк: 52):
//             один метод-тест на сценарий, строки — по порядку с моделируемым временем GVL_S7Clock.
//             Ожидаемые значения — из CSV (эталонные модели по описанию логики блока), не из
//             результата конвертации.
// Автор:      s7conv 0.1.0 (сгенерировано)
// Версия:     не указана
// Документ:   scenarios/README.md, docs/methodology.md, раздел «Проверка поведения»
FUNCTION_BLOCK FB_Motor_ScenarioTest EXTENDS coUnit.FB_TestSuite
VAR
    fbAutoStartOk : FB_Motor;  // свой экземпляр на сценарий
    xAutoStartOkDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbNoFeedbackTimeout : FB_Motor;  // свой экземпляр на сценарий
    xNoFeedbackTimeoutDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbFeedbackLost : FB_Motor;  // свой экземпляр на сценарий
    xFeedbackLostDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbUnexpectedFeedback : FB_Motor;  // свой экземпляр на сценарий
    xUnexpectedFeedbackDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbThermalTripManual : FB_Motor;  // свой экземпляр на сценарий
    xThermalTripManualDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbBumplessAutoToManual : FB_Motor;  // свой экземпляр на сценарий
    xBumplessAutoToManualDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbCustomFeedbackTime : FB_Motor;  // свой экземпляр на сценарий
    xCustomFeedbackTimeDone : BOOL;  // сценарий выполнен (выполняется один раз)
END_VAR
