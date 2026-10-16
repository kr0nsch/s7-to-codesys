// AUTO-GENERATED — не редактировать: s7conv gen-tests, сценарии scenarios/FB_PumpAlternation.csv
// Правка — в CSV (scenarios/README.md), затем python -m s7conv build-corpus.
// Назначение: тесты поведения сконвертированного FB_PumpAlternation по сценариям CSV (сценариев: 6, строк: 31):
//             один метод-тест на сценарий, строки — по порядку с моделируемым временем GVL_S7Clock.
//             Ожидаемые значения — из CSV (эталонные модели по описанию логики блока), не из
//             результата конвертации.
// Автор:      s7conv 0.1.0 (сгенерировано)
// Версия:     не указана
// Документ:   scenarios/README.md, docs/methodology.md, раздел «Проверка поведения»
FUNCTION_BLOCK FB_PumpAlternation_ScenarioTest EXTENDS coUnit.FB_TestSuite
VAR
    fbRotateOnStop : FB_PumpAlternation;  // свой экземпляр на сценарий
    xRotateOnStopDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbStandbyTakesOver : FB_PumpAlternation;  // свой экземпляр на сценарий
    xStandbyTakesOverDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbForcedAlternate : FB_PumpAlternation;  // свой экземпляр на сценарий
    xForcedAlternateDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbRotateOnStopDisabled : FB_PumpAlternation;  // свой экземпляр на сценарий
    xRotateOnStopDisabledDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbNoPumpsAvailable : FB_PumpAlternation;  // свой экземпляр на сценарий
    xNoPumpsAvailableDone : BOOL;  // сценарий выполнен (выполняется один раз)
    fbDemandClamped : FB_PumpAlternation;  // свой экземпляр на сценарий
    xDemandClampedDone : BOOL;  // сценарий выполнен (выполняется один раз)
END_VAR
