// Назначение: глобальные теги S7 без адреса и символы, не найденные в корпусе
// Автор:      s7conv 0.1.0 (сгенерировано)
// Версия:     не указана
// Документ:   docs/MAPPING.md, раздел «Теги»
{attribute 'qualified_only'}
VAR_GLOBAL
    // MIGRATION-CHECK: символ "Alarm_Lamp" не найден — тип BOOL выведен по использованию
    //                  (s7conv/tests/fixtures/analog.scl:69)
    Alarm_Lamp : BOOL;
END_VAR
