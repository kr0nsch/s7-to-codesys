// Назначение: Конвейер выдачи реагента (STL, таймеры S5)
//             Ленточный конвейер выдачи реагента (STL S7-300); таймеры T1–T5 и счётчик C1 S5 — глобальные.
//             1. Запрос xReq: S по xStart, затем R по xStop OR xJam (сброс главнее; xJam — прошлого вызова).
//             2. Сирена: SP T1 1 с по фронту xReq, xHorn = T1; снятие запроса обрывает. 3. SD T2 2 с, RLO = xReq.
//             4. Выбег: SF T3 3 с, RLO = T2, xMotor = T3. 5. Поток: SE T4 4 с по фронту xSensor, xFlowOk = T4;
//             взвод SS T5 5 с по фронту xMotor, R T5 при xMotor = 0; затор T5 AND NOT T4 → S xJam; xAck: FR T4
//             (при удерживаемом xSensor контроль запускается снова), R xJam.
//             6. iDelayLeft := L T2 (остаток задержки, единицы 10 мс), wRunOutBcd := LC T3 (BCD со шкалой).
//             7. Счётчик C1: CU по xSensor, R по xCountReset (по уровню); iCount := L C1, wCountBcd := LC C1.
// Автор:      WTP2 (исходный блок S7); перевод в ST — s7conv 0.1.0
// Версия:     0.1 (исходный блок S7)
// Документ:   docs/CONVERSION_REPORT.md, docs/MAPPING.md
// Источник:   samples/lang/FB_ConveyorStl.xml, STL, SW.Blocks.FB "FB_ConveyorStl", пространство имён Interface/v5,
//             FAMILY Dosing
// Сгенерировано s7conv: пометки MIGRATION-CHECK и MIGRATION-TODO требуют ручного разбора.
// MIGRATION-CHECK: стандартный (неоптимизированный) доступ S7: абсолютная адресация и порядок байтов не переносятся
//                  (FB_ConveyorStl.xml, SW.Blocks.FB «FB_ConveyorStl»)
FUNCTION_BLOCK FB_ConveyorStl
VAR_INPUT
    xStart : BOOL;  // Пуск ленты
    xStop : BOOL;  // Стоп ленты
    xSensor : BOOL;  // Датчик изделия на выходе ленты
    xAck : BOOL;  // Квитирование аварии
    xCountReset : BOOL;  // Сброс счётчика изделий
END_VAR
VAR_OUTPUT
    xHorn : BOOL;  // Сирена перед пуском
    xMotor : BOOL;  // Двигатель ленты
    xFlowOk : BOOL;  // Поток изделий в норме (идёт T4)
    xJam : BOOL;  // Авария: затор
    iDelayLeft : INT;  // Остаток задержки пуска, единицы 10 мс
    wRunOutBcd : WORD;  // Остаток выбега, BCD со шкалой
    iCount : INT;  // Изделий
    wCountBcd : WORD;  // Изделий, BCD
END_VAR
VAR
    xReq : BOOL;  // Запрос работы
END_VAR
