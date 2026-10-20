// Назначение: Блокировки насоса по уровню и давлению (LAD)
//             Блокировки насоса II подъёма по уровню в РЧВ и давлению в коллекторе (LAD).
//             1. xLowLevel := iLevel_cm < iLevelMin_cm.  2. xHighPress := iPressure_kPa > iPressureMax_kPa.
//             3. Если xLowLevel OR xHighPress — установить xAlarmLatch (S).
//             4. Если xAck AND NOT xLowLevel AND NOT xHighPress — сбросить xAlarmLatch (R).
//             5. Обслуживание: при xMaint прыжок вперёд к метке NoAuto (сети 6-7 не выполняются).
//             6. xPumpOn := xAutoReq AND NOT xAlarmLatch.
//             7. По фронту xPumpOn (P_TRIG, бит xRunEdge): iRunCount := iRunCount + 1 (ADD Int); xCountOk := ENO
//             сложения
//             (ENO = 0 при переполнении Int: 32767 + 1).
// Автор:      WTP2 (исходный блок S7); перевод в ST — s7conv 0.1.0
// Версия:     0.1 (исходный блок S7)
// Документ:   docs/CONVERSION_REPORT.md, docs/MAPPING.md
// Источник:   samples/lang/FB_PumpInterlockLad.xml, LAD, SW.Blocks.FB "FB_PumpInterlockLad", пространство имён
//             Interface/v5, FAMILY Drives
// Сгенерировано s7conv: пометки MIGRATION-CHECK и MIGRATION-TODO требуют ручного разбора.
FUNCTION_BLOCK FB_PumpInterlockLad
VAR_INPUT
    xAutoReq : BOOL;  // Запрос автоматики на работу
    iLevel_cm : INT;  // Уровень в РЧВ, см
    iLevelMin_cm : INT := 50;  // Минимальный уровень, см
    iPressure_kPa : INT;  // Давление в коллекторе, кПа
    iPressureMax_kPa : INT := 600;  // Максимальное давление, кПа
    xAck : BOOL;  // Квитирование аварии
    xMaint : BOOL;  // Режим обслуживания
END_VAR
VAR_OUTPUT
    xPumpOn : BOOL;  // Команда насосу
    xLowLevel : BOOL;  // Низкий уровень
    xHighPress : BOOL;  // Высокое давление
    xAlarm : BOOL;  // Авария (защёлка)
    iRunCount : INT;  // Число включений
    xCountOk : BOOL;  // ENO сложения: нет переполнения
    iSetpoint_pct : INT;  // Уставка производительности, %
    xChainOk : BOOL;  // ENO цепочки вызовов
    xRunMem : BOOL;  // Копия бита памяти фронта
END_VAR
VAR
    xAlarmLatch : BOOL;  // Защёлка аварии
    xRunEdge : BOOL;  // Бит памяти фронта xPumpOn
    iStage1 : INT;  // Уставка после первого ограничения
    iStage2 : INT;  // Уставка после второго ограничения
END_VAR
VAR_TEMP
    xNet5_1 : BOOL;  // сеть 5: условие прыжка к NoAuto (UId 21)
    xNet7_1 : BOOL;  // сеть 7: PBox (UId 21)
    xNet7_2 : BOOL;  // сеть 7: ENO Add (UId 25)
END_VAR
