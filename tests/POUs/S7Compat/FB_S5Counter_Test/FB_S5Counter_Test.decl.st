// Назначение: набор тестов CfUnit (coUnit 1.2.0.0) для счётчиков S5 слоя совместимости S7Compat
//             (F_S5CountUp, F_S5CountDown, F_S5CounterSet, F_S5CounterReset, F_S5CounterEnable, F_S5CounterQ,
//             F_S5CounterBin, F_S5CounterBcd): счёт по фронту, границы 0 и 999, установка из BCD по фронту,
//             сброс по уровню, FR. Ожидаемые значения — по справочнику STL S7-300/400 (AWL_e.pdf, гл. 4).
//             Экземпляр набора объявляется в PRG_Tests.
// Автор:      kr0nsch
// Версия:     1.2.0
// Документ:   docs/MAPPING_STL.md, правило s5.counter
FUNCTION_BLOCK FB_S5Counter_Test EXTENDS coUnit.FB_TestSuite
