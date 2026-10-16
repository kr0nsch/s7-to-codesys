// Назначение: набор тестов CfUnit (coUnit 1.2.0.0) для F_S7Now — источника времени таймеров S7Compat:
//             моделируемые часы при xSimulation = TRUE; при xSimulation = FALSE — время ПЛК, которое
//             идёт так же, как ET таймера CODESYS Standard (тест на несколько циклов).
//             Экземпляр набора объявляется в PRG_Tests.
// Автор:      <ИМЯ ФАМИЛИЯ>
// Версия:     0.1.0
// Документ:   docs/methodology.md, раздел «Проверка поведения: время в тестах»
FUNCTION_BLOCK FB_F_S7Now_Test EXTENDS coUnit.FB_TestSuite
VAR
    // AdvancesLikeStandardTimer: состояние между циклами (тест идёт несколько циклов)
    fbRtReference : TON;            // эталон времени — таймер CODESYS Standard
    xRtStarted : BOOL;              // момент начала зафиксирован
    xRtDone : BOOL;                 // тест завершён
    tRtStart : TIME;                // F_S7Now() в начале теста
    tRtElapsed : TIME;              // прирост F_S7Now()
    tRtDiff : TIME;                 // |прирост F_S7Now() - ET эталона|
END_VAR
VAR CONSTANT
    T_RT_REF_PT : TIME := T#10S;    // PT эталона: больше длительности теста, ET не насыщается
    T_RT_DURATION : TIME := T#300MS;  // длительность теста по эталону
    T_RT_TOL : TIME := T#5MS;       // допуск: F_S7Now и TON читают часы в разные моменты вызова
END_VAR
