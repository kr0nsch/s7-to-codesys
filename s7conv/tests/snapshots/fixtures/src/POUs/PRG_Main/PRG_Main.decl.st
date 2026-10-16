// Назначение: Main Program Sweep (Cycle)
// Автор:      не указан (исходный блок S7); перевод в ST — s7conv 0.1.0
// Версия:     0.1 (исходный блок S7)
// Документ:   docs/CONVERSION_REPORT.md, docs/MAPPING.md
// Источник:   s7conv/tests/fixtures/main.scl, строки 2–23, ORGANIZATION_BLOCK "Main"
// Сгенерировано s7conv: пометки MIGRATION-CHECK и MIGRATION-TODO требуют ручного разбора.
// ---- комментарий в начале исходного файла SCL ----
// Фикстура s7conv: организационные блоки и одиночный экземпляр IEC-таймера.
PROGRAM PRG_Main
VAR_TEMP
    cmdTmp : UDT_MotorCmd;
END_VAR
