// Назначение: Программа (OB) «Startup», сконвертирован из SCL
// Автор:      не указан (исходный блок S7); перевод в ST — s7conv 0.1.0
// Версия:     0.1 (исходный блок S7)
// Документ:   docs/CONVERSION_REPORT.md, docs/MAPPING.md
// Источник:   s7conv/tests/fixtures/main.scl, строки 34–41, ORGANIZATION_BLOCK "Startup"
// Сгенерировано s7conv: пометки MIGRATION-CHECK и MIGRATION-TODO требуют ручного разбора.
// MIGRATION-CHECK: OB100 (Startup) → однократное выполнение по флагу первого цикла в MainTask: флаг (не RETAIN)
//                  сбрасывается загрузкой, Reset warm/cold и перезапуском ПЛК, но не командой Stop → Start CODESYS
//                  (в S7 OB100 выполняется при каждом STOP → RUN); задачи с более высоким приоритетом могут
//                  выполниться раньше (стр. 34)
PROGRAM PRG_Startup
VAR
    xS7convStartupDone : BOOL; // флаг первого цикла (замена OB100)
END_VAR
