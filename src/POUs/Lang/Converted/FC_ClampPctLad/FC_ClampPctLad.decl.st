// Назначение: Ограничение значения пределами (LAD)
//             Результат: iIn, ограниченный снизу iMin и сверху iMax (сначала верхний предел, затем нижний). ENO не
//             пишется: ENO = EN.
// Автор:      WTP2 (исходный блок S7); перевод в ST — s7conv 0.1.0
// Версия:     0.1 (исходный блок S7)
// Документ:   docs/CONVERSION_REPORT.md, docs/MAPPING.md
// Источник:   samples/lang/FC_ClampPctLad.xml, LAD, SW.Blocks.FC "FC_ClampPctLad", пространство имён Interface/v5,
//             FAMILY Utils
// Сгенерировано s7conv: пометки MIGRATION-CHECK и MIGRATION-TODO требуют ручного разбора.
FUNCTION FC_ClampPctLad : INT
VAR_INPUT
    iIn : INT;  // Значение
    iMin : INT;  // Нижний предел
    iMax : INT;  // Верхний предел
END_VAR
