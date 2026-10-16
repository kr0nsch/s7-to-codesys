// Назначение: набор тестов CfUnit (coUnit 1.2.0.0) для FB_S7Tp слоя совместимости S7Compat:
//             импульс по фронту IN длительностью PT, порог PT, ET после импульса и при IN = FALSE,
//             фронты во время импульса, совпадение со Standard.TP в реальном времени.
//             Ожидаемые значения — по семантике МЭК 61131-3 и S7 (описание в объявлении блока), а
//             не по результату реализации. Моделируемое время — GVL_S7Clock (тест включает и
//             выключает его сам). Экземпляр набора объявляется в PRG_Tests.
// Автор:      <ИМЯ ФАМИЛИЯ>
// Версия:     0.1.0
// Документ:   docs/methodology.md, раздел «Проверка поведения: время в тестах»
FUNCTION_BLOCK FB_S7Tp_Test EXTENDS coUnit.FB_TestSuite
VAR
    // MatchesStandardInRealTime: состояние между циклами (тест идёт несколько циклов)
    fbRtCompat : FB_S7Tp;              // проверяемый таймер S7Compat
    fbRtStandard : TP;               // эталон — таймер CODESYS Standard
    xRtStarted : BOOL;              // момент начала зафиксирован
    xRtDone : BOOL;                 // тест завершён
    xRtIn : BOOL;                   // общий вход IN
    xRtSawQ : BOOL;                 // Standard Q хотя бы раз был TRUE
    tRtStart : TIME;                // время начала теста (F_S7Now() = TIME())
    tRtElapsed : TIME;              // прошло с начала теста
    tRtEtDiff : TIME;               // |ET S7Compat - ET Standard|
    tRtEtToPt : TIME;               // PT - ET Standard (близость к порогу)
    iRtMismatches : INT;            // циклов с расхождением
END_VAR
VAR CONSTANT
    T_RT_PT : TIME := T#200MS;      // PT обоих таймеров
    T_RT_DURATION : TIME := T#700MS;  // длительность теста
    T_RT_TOL : TIME := T#5MS;       // допуск ET: таймеры читают TIME() в разные моменты цикла
END_VAR
