// Назначение: многоцикловый набор CfUnit (coUnit 1.2.0.0) без времени для FB_BackwashGraph — промывки
//             фильтра, переведённой из S7-GRAPH. Один и тот же набор проходят оба варианта: ST-двойник
//             (src/POUs/Lang/Converted, этот проект) и SFC с ФБ-обёрткой (plcopen/Lang/Converted, проект
//             tools_project/cds_plcopen.py test). SFC переключается в конце цикла, двойник — в том же вызове,
//             поэтому каждый шаг теста — CYCLES вызовов с одинаковыми входами, затем проверки установившегося
//             состояния. Пути с временем (продувка 10 с, D задвижки воздуха) проверяют сценарии ST-двойника.
//             Ожидаемые значения — по описанию блока (samples/lang/README.md), а не по результату перевода.
//             Экземпляр набора объявляется в PRG_Tests.
// Автор:      kr0nsch
// Версия:     1.2.0
// Документ:   docs/MAPPING_GRAPH.md; docs/EQUIVALENCE.md
FUNCTION_BLOCK FB_BackwashGraph_SeqTest EXTENDS coUnit.FB_TestSuite
VAR CONSTANT
    CYCLES : INT := 3;  // вызовов на шаг теста: хватает SFC (переключение в конце цикла) и двойнику
END_VAR
