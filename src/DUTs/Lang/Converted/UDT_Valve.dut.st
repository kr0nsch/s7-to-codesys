// Назначение: Задвижка
//             Состояние задвижки для HMI и STL
// Автор:      не указан (исходный блок S7); перевод в ST — s7conv 0.1.0
// Версия:     0.1 (исходный блок S7)
// Документ:   docs/CONVERSION_REPORT.md, docs/MAPPING.md
// Источник:   samples/lang/UDT_Valve.xml, UDT, SW.Types.PlcStruct "UDT_Valve", пространство имён Interface/v5
// Сгенерировано s7conv: пометки MIGRATION-CHECK и MIGRATION-TODO требуют ручного разбора.
TYPE UDT_Valve :
STRUCT
    xOpen : BOOL;  // Открыта
    xClosed : BOOL;  // Закрыта
    iPos_pct : INT;  // Положение, %
END_STRUCT
END_TYPE
