// AUTO-GENERATED — не редактировать: scenarios/lang/FB_PumpInterlockLad.csv, сценарий MaintenanceJump
coUnit.TEST('MaintenanceJump');
IF NOT xMaintenanceJumpDone THEN
    xMaintenanceJumpDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;

    // #1, t = 0 мс — включение №1, xCountOk = 1
    GVL_S7Clock.tSimNow := T#0MS;
    fbMaintenanceJump.xAutoReq := TRUE;
    fbMaintenanceJump.iLevel_cm := 120;
    fbMaintenanceJump.iLevelMin_cm := 50;
    fbMaintenanceJump.iPressure_kPa := 400;
    fbMaintenanceJump.iPressureMax_kPa := 600;
    fbMaintenanceJump.xAck := FALSE;
    fbMaintenanceJump.xMaint := FALSE;
    fbMaintenanceJump();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbMaintenanceJump.xPumpOn, Message := 'MaintenanceJump#1 xPumpOn');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbMaintenanceJump.xLowLevel,
                      Message := 'MaintenanceJump#1 xLowLevel');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbMaintenanceJump.xHighPress,
                      Message := 'MaintenanceJump#1 xHighPress');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbMaintenanceJump.xAlarm, Message := 'MaintenanceJump#1 xAlarm');
    AssertEquals_INT(Expected := 1, Actual := fbMaintenanceJump.iRunCount, Message := 'MaintenanceJump#1 iRunCount');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbMaintenanceJump.xCountOk, Message := 'MaintenanceJump#1 xCountOk');
    AssertEquals_INT(Expected := 80,
                     Actual := fbMaintenanceJump.iSetpoint_pct,
                     Message := 'MaintenanceJump#1 iSetpoint_pct');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbMaintenanceJump.xChainOk, Message := 'MaintenanceJump#1 xChainOk');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbMaintenanceJump.xRunMem, Message := 'MaintenanceJump#1 xRunMem');

    // #2, t = 100 мс — обслуживание: насос выключен; xCountOk и xRunMem сохраняют значения
    GVL_S7Clock.tSimNow := T#100MS;
    fbMaintenanceJump.xMaint := TRUE;
    fbMaintenanceJump();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbMaintenanceJump.xPumpOn, Message := 'MaintenanceJump#2 xPumpOn');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbMaintenanceJump.xLowLevel,
                      Message := 'MaintenanceJump#2 xLowLevel');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbMaintenanceJump.xHighPress,
                      Message := 'MaintenanceJump#2 xHighPress');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbMaintenanceJump.xAlarm, Message := 'MaintenanceJump#2 xAlarm');
    AssertEquals_INT(Expected := 1, Actual := fbMaintenanceJump.iRunCount, Message := 'MaintenanceJump#2 iRunCount');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbMaintenanceJump.xCountOk, Message := 'MaintenanceJump#2 xCountOk');
    AssertEquals_INT(Expected := 0,
                     Actual := fbMaintenanceJump.iSetpoint_pct,
                     Message := 'MaintenanceJump#2 iSetpoint_pct');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbMaintenanceJump.xChainOk, Message := 'MaintenanceJump#2 xChainOk');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbMaintenanceJump.xRunMem, Message := 'MaintenanceJump#2 xRunMem');

    // #3, t = 200 мс — обслуживание держится
    GVL_S7Clock.tSimNow := T#200MS;
    fbMaintenanceJump();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbMaintenanceJump.xPumpOn, Message := 'MaintenanceJump#3 xPumpOn');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbMaintenanceJump.xLowLevel,
                      Message := 'MaintenanceJump#3 xLowLevel');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbMaintenanceJump.xHighPress,
                      Message := 'MaintenanceJump#3 xHighPress');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbMaintenanceJump.xAlarm, Message := 'MaintenanceJump#3 xAlarm');
    AssertEquals_INT(Expected := 1, Actual := fbMaintenanceJump.iRunCount, Message := 'MaintenanceJump#3 iRunCount');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbMaintenanceJump.xCountOk, Message := 'MaintenanceJump#3 xCountOk');
    AssertEquals_INT(Expected := 0,
                     Actual := fbMaintenanceJump.iSetpoint_pct,
                     Message := 'MaintenanceJump#3 iSetpoint_pct');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbMaintenanceJump.xChainOk, Message := 'MaintenanceJump#3 xChainOk');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbMaintenanceJump.xRunMem, Message := 'MaintenanceJump#3 xRunMem');

    // #4, t = 300 мс — выход из обслуживания: насос включён, фронта нет — бит памяти остался 1
    GVL_S7Clock.tSimNow := T#300MS;
    fbMaintenanceJump.xMaint := FALSE;
    fbMaintenanceJump();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbMaintenanceJump.xPumpOn, Message := 'MaintenanceJump#4 xPumpOn');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbMaintenanceJump.xLowLevel,
                      Message := 'MaintenanceJump#4 xLowLevel');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbMaintenanceJump.xHighPress,
                      Message := 'MaintenanceJump#4 xHighPress');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbMaintenanceJump.xAlarm, Message := 'MaintenanceJump#4 xAlarm');
    AssertEquals_INT(Expected := 1, Actual := fbMaintenanceJump.iRunCount, Message := 'MaintenanceJump#4 iRunCount');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbMaintenanceJump.xCountOk, Message := 'MaintenanceJump#4 xCountOk');
    AssertEquals_INT(Expected := 80,
                     Actual := fbMaintenanceJump.iSetpoint_pct,
                     Message := 'MaintenanceJump#4 iSetpoint_pct');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbMaintenanceJump.xChainOk, Message := 'MaintenanceJump#4 xChainOk');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbMaintenanceJump.xRunMem, Message := 'MaintenanceJump#4 xRunMem');

    // #5, t = 400 мс — запрос снят
    GVL_S7Clock.tSimNow := T#400MS;
    fbMaintenanceJump.xAutoReq := FALSE;
    fbMaintenanceJump();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbMaintenanceJump.xPumpOn, Message := 'MaintenanceJump#5 xPumpOn');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbMaintenanceJump.xLowLevel,
                      Message := 'MaintenanceJump#5 xLowLevel');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbMaintenanceJump.xHighPress,
                      Message := 'MaintenanceJump#5 xHighPress');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbMaintenanceJump.xAlarm, Message := 'MaintenanceJump#5 xAlarm');
    AssertEquals_INT(Expected := 1, Actual := fbMaintenanceJump.iRunCount, Message := 'MaintenanceJump#5 iRunCount');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbMaintenanceJump.xCountOk, Message := 'MaintenanceJump#5 xCountOk');
    AssertEquals_INT(Expected := 0,
                     Actual := fbMaintenanceJump.iSetpoint_pct,
                     Message := 'MaintenanceJump#5 iSetpoint_pct');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbMaintenanceJump.xChainOk, Message := 'MaintenanceJump#5 xChainOk');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbMaintenanceJump.xRunMem, Message := 'MaintenanceJump#5 xRunMem');

    // #6, t = 500 мс — включение №2
    GVL_S7Clock.tSimNow := T#500MS;
    fbMaintenanceJump.xAutoReq := TRUE;
    fbMaintenanceJump();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbMaintenanceJump.xPumpOn, Message := 'MaintenanceJump#6 xPumpOn');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbMaintenanceJump.xLowLevel,
                      Message := 'MaintenanceJump#6 xLowLevel');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbMaintenanceJump.xHighPress,
                      Message := 'MaintenanceJump#6 xHighPress');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbMaintenanceJump.xAlarm, Message := 'MaintenanceJump#6 xAlarm');
    AssertEquals_INT(Expected := 2, Actual := fbMaintenanceJump.iRunCount, Message := 'MaintenanceJump#6 iRunCount');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbMaintenanceJump.xCountOk, Message := 'MaintenanceJump#6 xCountOk');
    AssertEquals_INT(Expected := 80,
                     Actual := fbMaintenanceJump.iSetpoint_pct,
                     Message := 'MaintenanceJump#6 iSetpoint_pct');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbMaintenanceJump.xChainOk, Message := 'MaintenanceJump#6 xChainOk');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbMaintenanceJump.xRunMem, Message := 'MaintenanceJump#6 xRunMem');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
