// Назначение: набор тестов CfUnit (coUnit 1.2.0.0) для таймеров S5 слоя совместимости S7Compat (F_S5Pulse,
//             F_S5ExtPulse, F_S5OnDelay, F_S5RetOnDelay, F_S5OffDelay, F_S5Enable, F_S5Reset, F_S5Q, F_S5Bin,
//             F_S5Bcd, F_S5TimeWord): пуск по фронту, останов по RLO, перезапуск, FR, сброс по уровню,
//             остаток в единицах шкалы и BCD со шкалой, выбор шкалы, чтение до пуска в том же цикле.
//             Ожидаемые значения — по справочникам STL и LAD S7-300/400 (AWL_e.pdf гл. 12, s7kop гл. 13) и
//             записям L13–L16 docs/ASSUMPTIONS.md, а не по результату реализации. Моделируемое время —
//             GVL_S7Clock (тест включает и выключает его сам). Экземпляр набора объявляется в PRG_Tests.
// Автор:      kr0nsch
// Версия:     1.2.0
// Документ:   docs/MAPPING_STL.md, правила s5.timebase и s5.timer; docs/EQUIVALENCE.md
FUNCTION_BLOCK FB_S5Timer_Test EXTENDS coUnit.FB_TestSuite
