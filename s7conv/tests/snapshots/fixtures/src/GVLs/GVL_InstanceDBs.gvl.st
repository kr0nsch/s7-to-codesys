// Назначение: экземпляры функциональных блоков и типизированные DB S7 (экземплярные DB → переменные GVL)
// Автор:      s7conv 0.1.0 (сгенерировано)
// Версия:     не указана
// Документ:   docs/MAPPING.md, раздел «DB»
{attribute 'qualified_only'}
VAR_GLOBAL
    Delay_DB : TON; // s7conv/tests/fixtures/main.scl:56
    Level_DB : FB_Level; // s7conv/tests/fixtures/main.scl:66
    Motor1_DB : FB_Motor; // s7conv/tests/fixtures/motor.scl:103
    // MIGRATION-CHECK: экземплярный DB FB_Legacy_DB выведен по вызову (исходника DB в корпусе нет)
    FB_Legacy_DB : FB_Legacy;
END_VAR
