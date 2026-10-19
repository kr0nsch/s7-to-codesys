// Назначение: набор тестов CfUnit (coUnit 1.2.0.0) для функций ENO арифметики S7 (F_S7Eno<Оп><Тип>):
//             на границах диапазона INT и DINT, при переполнении в обе стороны и без переполнения.
//             Ожидаемые значения — по правилу S7 «ENO = EN AND NOT переполнение» (справочник LAD
//             S7-300/400, прил. C.1), проверка HAND_CHECKS «ENO при ADD_I 32767 + 1».
//             Экземпляр набора объявляется в PRG_Tests.
// Автор:      kr0nsch
// Версия:     1.1.0
// Документ:   docs/MAPPING_LADFBD.md, правило lad.eno_error
FUNCTION_BLOCK FB_F_S7Eno_Test EXTENDS coUnit.FB_TestSuite
