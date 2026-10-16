// AUTO-GENERATED — не редактировать: s7conv gen-tests, сценарии scenarios/FB_AlarmDelay.csv
// Правка — в CSV (scenarios/README.md), затем python -m s7conv build-corpus.
// Назначение: тесты поведения сконвертированного FB_AlarmDelay по сценариям CSV (сценариев: 8, строк: 55):
//             один метод-тест на сценарий, строки — по порядку с моделируемым временем GVL_S7Clock.
//             Ожидаемые значения — из CSV (эталонные модели по описанию логики блока), не из
//             результата конвертации.
// Автор:      s7conv 0.1.0 (сгенерировано)
// Версия:     не указана
// Документ:   scenarios/README.md, docs/methodology.md, раздел «Проверка поведения»
FUNCTION_BLOCK FB_AlarmDelay_ScenarioTest EXTENDS coUnit.FB_TestSuite
VAR
    fbActivateAckClear : FB_AlarmDelay;  // свой экземпляр на сценарий
    xActivateAckClearDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbClearedBeforeAck : FB_AlarmDelay;  // свой экземпляр на сценарий
    xClearedBeforeAckDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbChatterSuppressed : FB_AlarmDelay;  // свой экземпляр на сценарий
    xChatterSuppressedDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbReturnDuringOffDelay : FB_AlarmDelay;  // свой экземпляр на сценарий
    xReturnDuringOffDelayDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbNewActivationAfterOffDelay : FB_AlarmDelay;  // свой экземпляр на сценарий
    xNewActivationAfterOffDelayDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbDisabled : FB_AlarmDelay;  // свой экземпляр на сценарий
    xDisabledDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbAckSameCallAsActivation : FB_AlarmDelay;  // свой экземпляр на сценарий
    xAckSameCallAsActivationDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbAckHeldDuringActivation : FB_AlarmDelay;  // свой экземпляр на сценарий
    xAckHeldDuringActivationDone : BOOL;  // сценарий выполнен (выполняется один раз)
END_VAR
