// Назначение: Технологические данные (стандартный доступ)
//             Неоптимизированный DB: STL S7-300 адресует члены по смещению (Offset)
// Автор:      WTP2 (исходный блок S7); перевод в ST — s7conv 0.1.0
// Версия:     0.1 (исходный блок S7)
// Документ:   docs/CONVERSION_REPORT.md, docs/MAPPING.md
// Источник:   samples/lang/DB_Process.xml, DB, SW.Blocks.GlobalDB "DB_Process", пространство имён Interface/v5,
//             FAMILY Plant
// Сгенерировано s7conv: пометки MIGRATION-CHECK и MIGRATION-TODO требуют ручного разбора.
// MIGRATION-CHECK: стандартный (неоптимизированный) доступ S7: абсолютная адресация и порядок байтов не переносятся
//                  (DB_Process.xml, SW.Blocks.GlobalDB «DB_Process»)
// MIGRATION-CHECK: стандартный DB без NON_RETAIN: в S7 он реманентный — объявлен RETAIN (DB_Process.xml,
//                  SW.Blocks.GlobalDB «DB_Process»)
{attribute 'qualified_only'}
VAR_GLOBAL
END_VAR
VAR_GLOBAL RETAIN
    xPumpRun : BOOL;  // Насос в работе
    iLevel_cm : INT;  // Уровень, см
    rFlow_m3h : REAL;  // Расход, м3/ч
    wStatus : WORD;  // Слово состояния
    stValve : UDT_Valve;  // Задвижка напорная
    iBatch : INT := 1;  // Номер партии
END_VAR
