// Назначение: Тип (UDT) «UDT_MotorCmd», сконвертирован из SCL
// Автор:      не указан (исходный блок S7); перевод в ST — s7conv 0.1.0
// Версия:     0.1 (исходный блок S7)
// Документ:   docs/CONVERSION_REPORT.md, docs/MAPPING.md
// Источник:   s7conv/tests/fixtures/motor.scl, строки 3–12, TYPE "UDT_MotorCmd"
// Сгенерировано s7conv: пометки MIGRATION-CHECK и MIGRATION-TODO требуют ручного разбора.
// ---- комментарий в начале исходного файла SCL ----
// Фикстура s7conv: двигатель с пуском по фронту, задержкой контроля обратной связи и режимами.
// Написано с нуля для тестов конвертера, формат — внешний источник TIA Portal.
TYPE UDT_MotorCmd :
STRUCT
    start : BOOL;  // команда «пуск» (импульс)
    stop : BOOL;  // команда «стоп» (импульс)
    mode : INT := 1;  // 0 — выведен, 1 — авто, 2 — ручной
    name : STRING(16);
END_STRUCT
END_TYPE
