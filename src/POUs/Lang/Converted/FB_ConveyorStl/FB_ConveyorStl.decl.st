// Назначение: Конвейер выдачи реагента (STL, таймеры S5)
//             Ленточный конвейер выдачи реагента (STL S7-300): таймеры и счётчик S5.
//             1. Запрос работы xReq: S по xStart, затем R по xStop OR xJam (сброс главнее; xJam — прошлого вызова).
//             2. Сирена: SP T1 1 с по фронту xReq — xHorn = T1; снятие запроса обрывает сирену.
//             3. Задержка пуска: SD T2 2 с, RLO = xReq.
//             4. Выбег: SF T3 3 с, RLO = T2 — xMotor = T3 (двигатель работает, пока T2 = 1, и 3 с после).
//             5. Контроль потока: SE T4 4 с по каждому фронту xSensor — xFlowOk = T4. Взвод контроля: SS T5 5 с по
//             фронту
//             xMotor, сброс T5 (R) при xMotor = 0. Затор: T5 AND NOT T4 → S xJam. Квитирование xAck: FR T4 (при
//             удерживаемом xSensor контроль запускается снова), R xJam.
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
