// Назначение: набор тестов CfUnit (coUnit 1.2.0.0) — характеризация SR и RS библиотеки Standard и проверка
//             перевода бистабильных элементов S7: S7 SR (сброс главнее) переводится в CODESYS RS, S7 RS
//             (установка главнее) — в CODESYS SR. Одноимённая замена, как в 1.0.0, меняла приоритет при
//             S = R = 1. Ожидаемые значения — по справке Standard (SR — set-dominant, RS — reset-dominant)
//             и справочнику LAD S7-300/400 (s7kop__b.pdf, §1.10–1.11).
//             Экземпляр набора объявляется в PRG_Tests.
// Автор:      kr0nsch
// Версия:     1.1.0
// Документ:   docs/MAPPING.md, раздел «Функциональные блоки инструкций»
FUNCTION_BLOCK FB_StandardFlipFlop_Test EXTENDS coUnit.FB_TestSuite
