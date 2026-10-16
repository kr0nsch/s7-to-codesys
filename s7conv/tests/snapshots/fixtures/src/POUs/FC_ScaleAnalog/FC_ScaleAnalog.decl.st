// Назначение: Scale raw analog value 0..27648
// Автор:      не указан (исходный блок S7); перевод в ST — s7conv 0.1.0
// Версия:     0.1 (исходный блок S7)
// Документ:   docs/CONVERSION_REPORT.md, docs/MAPPING.md
// Источник:   s7conv/tests/fixtures/analog.scl, строки 2–29, FUNCTION "FC_ScaleAnalog"
// Сгенерировано s7conv: пометки MIGRATION-CHECK и MIGRATION-TODO требуют ручного разбора.
// ---- комментарий в начале исходного файла SCL ----
// Фикстура s7conv: масштабирование аналогового входа и глобальный DB уставок.
FUNCTION FC_ScaleAnalog : REAL
VAR_INPUT
    raw : INT;  // сырое значение канала
    low : REAL;
    high : REAL;
END_VAR
VAR_OUTPUT
    valid : BOOL;
END_VAR
VAR
    norm : REAL;
END_VAR
VAR CONSTANT
    RAW_MAX : INT := 27648;
END_VAR
