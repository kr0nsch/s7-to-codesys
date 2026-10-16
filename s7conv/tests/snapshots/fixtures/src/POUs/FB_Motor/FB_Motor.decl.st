// Назначение: Motor with feedback supervision
//             Пуск по фронту команды, контроль обратной связи через FeedbackTime.
// Автор:      Engineer (исходный блок S7); перевод в ST — s7conv 0.1.0
// Версия:     1.2 (исходный блок S7)
// Документ:   docs/CONVERSION_REPORT.md, docs/MAPPING.md
// Источник:   s7conv/tests/fixtures/motor.scl, строки 14–101, FUNCTION_BLOCK "FB_Motor", FAMILY Drives
// Сгенерировано s7conv: пометки MIGRATION-CHECK и MIGRATION-TODO требуют ручного разбора.
// MIGRATION-CHECK: VAR RETAIN в ФБ: в CODESYS при RETAIN-переменной в retain-памяти хранится весь экземпляр ФБ, в
//                  S7 — только эти переменные (сверить с источником) (стр. 46)
FUNCTION_BLOCK FB_Motor
VAR_INPUT
    cmd : UDT_MotorCmd;
    feedback : BOOL;  // контактор включён
    feedbackTime : TIME := T#3S;
END_VAR
VAR_OUTPUT
    run : BOOL;
    fault : BOOL;
    runTime : TIME;
END_VAR
VAR_IN_OUT
    ack : BOOL;
END_VAR
VAR
    startEdge : R_TRIG;
    fbTimer : TON;
    starts : DINT;
    stat : ST_FB_Motor_stat;
END_VAR
VAR RETAIN
    operatingHours : REAL;
END_VAR
VAR_TEMP
    i : INT;
END_VAR
VAR CONSTANT
    MAX_STARTS : DINT := 1000;
END_VAR
