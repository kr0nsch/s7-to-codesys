// Назначение: Функциональный блок «FB_Level», сконвертирован из SCL
// Автор:      не указан (исходный блок S7); перевод в ST — s7conv 0.1.0
// Версия:     0.1 (исходный блок S7)
// Документ:   docs/CONVERSION_REPORT.md, docs/MAPPING.md
// Источник:   s7conv/tests/fixtures/analog.scl, строки 50–70, FUNCTION_BLOCK "FB_Level"
// Сгенерировано s7conv: пометки MIGRATION-CHECK и MIGRATION-TODO требуют ручного разбора.
FUNCTION_BLOCK FB_Level
VAR_OUTPUT
    level : REAL;
    levelPercent : INT;
END_VAR
VAR
    sensorOk : BOOL;
END_VAR
