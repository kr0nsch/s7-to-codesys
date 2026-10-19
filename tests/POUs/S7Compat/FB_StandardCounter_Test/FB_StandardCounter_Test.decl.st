// Назначение: набор тестов CfUnit (coUnit 1.2.0.0) — характеризация CTU, CTD и CTUD библиотеки Standard,
//             на которых построены модели интерпретатора stsim (s7conv/sim/stsim.py, builtin_counter):
//             счёт по фронту, RESET и LOAD по уровню, Q/QU/QD, нижняя граница CTD, приоритет RESET над LOAD
//             и одновременные фронты CU и CD у CTUD (справка Standard этого не описывает).
//             Экземпляр набора объявляется в PRG_Tests.
// Автор:      kr0nsch
// Версия:     1.1.0
// Документ:   docs/MAPPING.md, раздел «Функциональные блоки инструкций»; docs/EQUIVALENCE.md
FUNCTION_BLOCK FB_StandardCounter_Test EXTENDS coUnit.FB_TestSuite
