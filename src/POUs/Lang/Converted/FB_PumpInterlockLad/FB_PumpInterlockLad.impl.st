// Сеть 1: Низкий уровень в РЧВ
xLowLevel := iLevel_cm < iLevelMin_cm;
// Сеть 2: Высокое давление в коллекторе
xHighPress := iPressure_kPa > iPressureMax_kPa;
// Сеть 3: Защёлка аварии: установка
IF xLowLevel OR xHighPress THEN
    xAlarmLatch := TRUE;
END_IF
// Сеть 4: Защёлка аварии: квитирование
IF xAck AND NOT xLowLevel AND NOT xHighPress THEN
    xAlarmLatch := FALSE;
END_IF
// Сеть 5: Обслуживание: прыжок к NoAuto
// MIGRATION-CHECK: элемент «Jump»: имя и пины в SimaticML не подтверждены открытым экспортом
//                  (docs/MAPPING_LADFBD.md, уровень L) (FB_PumpInterlockLad.xml, сеть 5, UId 21)
xNet5_1 := xMaint;
IF NOT xNet5_1 THEN
    // прыжок к NoAuto: сети 6–7 выполняются без прыжка
    // Сеть 6: Автоматический режим
    xPumpOn := xAutoReq AND NOT xAlarmLatch;
    // Сеть 7: Счётчик включений с ENO
    xNet7_1 := xPumpOn AND NOT xRunEdge;
    xRunEdge := xPumpOn;
    // MIGRATION-CHECK: ENO Add S7 = EN AND NOT переполнение: F_S7EnoAddInt из S7Compat (в CODESYS ENO = EN);
    //                  результат при переполнении записывается с переносом, как у S7-300 [M]
    //                  (FB_PumpInterlockLad.xml, сеть 7, UId 25)
    xNet7_2 := xNet7_1 AND F_S7EnoAddInt(iIn1 := iRunCount, iIn2 := 1);
    IF xNet7_1 THEN
        iRunCount := iRunCount + 1;
    END_IF
    xCountOk := xNet7_2;
END_IF
// Сеть 8: Метка NoAuto: обслуживание выключает насос
IF xMaint THEN
    xPumpOn := FALSE;
END_IF
// Сеть 9: Уставка: три вызова FC_ClampPctLad через EN/ENO
// MIGRATION-CHECK: элемент «Call»: имя и пины в SimaticML не подтверждены открытым экспортом
//                  (docs/MAPPING_LADFBD.md, уровень L) (FB_PumpInterlockLad.xml, сеть 9, UId 23)
IF xPumpOn THEN
    iStage1 := FC_ClampPctLad(iIn := iLevel_cm, iMin := 0, iMax := 100);
END_IF
// MIGRATION-CHECK: элемент «Call»: имя и пины в SimaticML не подтверждены открытым экспортом
//                  (docs/MAPPING_LADFBD.md, уровень L) (FB_PumpInterlockLad.xml, сеть 9, UId 28)
IF xPumpOn THEN
    iStage2 := FC_ClampPctLad(iIn := iStage1, iMin := 10, iMax := 90);
END_IF
// MIGRATION-CHECK: элемент «Call»: имя и пины в SimaticML не подтверждены открытым экспортом
//                  (docs/MAPPING_LADFBD.md, уровень L) (FB_PumpInterlockLad.xml, сеть 9, UId 33)
IF xPumpOn THEN
    iSetpoint_pct := FC_ClampPctLad(iIn := iStage2, iMin := 20, iMax := 80);
END_IF
xChainOk := xPumpOn;
// Сеть 10: Насос выключен: уставка 0
IF NOT xPumpOn THEN
    iSetpoint_pct := 0;
END_IF
// Сеть 11: Авария
xAlarm := xAlarmLatch;
// Сеть 12: Бит памяти фронта в другой сети
xRunMem := xRunEdge;
