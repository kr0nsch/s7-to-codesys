// Назначение: структура поля «stat» блока «FB_Motor» (анонимный Struct в SCL)
// Автор:      s7conv 0.1.0 (сгенерировано)
// Версия:     не указана
// Документ:   docs/MAPPING.md, раздел «Типы»
// Источник:   s7conv/tests/fixtures/motor.scl, FUNCTION_BLOCK "FB_Motor"
TYPE ST_FB_Motor_stat :
STRUCT
    lastMode : INT;
    history : ARRAY[0..3] OF BOOL;
END_STRUCT
END_TYPE
