// Назначение: Глобальный DB «DB_Settings», сконвертирован из SCL
// Автор:      не указан (исходный блок S7); перевод в ST — s7conv 0.1.0
// Версия:     0.1 (исходный блок S7)
// Документ:   docs/CONVERSION_REPORT.md, docs/MAPPING.md
// Источник:   s7conv/tests/fixtures/analog.scl, строки 31–48, DATA_BLOCK "DB_Settings"
// Сгенерировано s7conv: пометки MIGRATION-CHECK и MIGRATION-TODO требуют ручного разбора.
{attribute 'qualified_only'}
VAR_GLOBAL
    levelLow : REAL := 0.0;
    levelHigh : REAL := 95.5;
    pumpDelay : TIME := T#5s;
    // MIGRATION-CHECK: S5Time → TIME: в S7 S5TIME — BCD с шагом 10 мс…10 с, диапазон до 2h46m30s (стр. 38)
    oldDelay : TIME := T#2s;
    label : STRING(254);
END_VAR
VAR_GLOBAL RETAIN
    totalVolume : LREAL;
    counterRaw : INT;
END_VAR
