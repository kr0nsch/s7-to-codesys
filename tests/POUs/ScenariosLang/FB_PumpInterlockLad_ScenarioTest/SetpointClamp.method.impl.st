// AUTO-GENERATED — не редактировать: scenarios/lang/FB_PumpInterlockLad.csv, сценарий SetpointClamp
coUnit.TEST('SetpointClamp');
IF NOT xSetpointClampDone THEN
    xSetpointClampDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;

    // #1, t = 0 мс — 55 → 55 → 55 → 55
    GVL_S7Clock.tSimNow := T#0MS;
    fbSetpointClamp.xAutoReq := TRUE;
    fbSetpointClamp.iLevel_cm := 55;
    fbSetpointClamp.iLevelMin_cm := 50;
    fbSetpointClamp.iPressure_kPa := 400;
    fbSetpointClamp.iPressureMax_kPa := 600;
    fbSetpointClamp.xAck := FALSE;
    fbSetpointClamp.xMaint := FALSE;
    fbSetpointClamp();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbSetpointClamp.xPumpOn, Message := 'SetpointClamp#1 xPumpOn');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSetpointClamp.xLowLevel, Message := 'SetpointClamp#1 xLowLevel');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSetpointClamp.xHighPress, Message := 'SetpointClamp#1 xHighPress');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSetpointClamp.xAlarm, Message := 'SetpointClamp#1 xAlarm');
    AssertEquals_INT(Expected := 1, Actual := fbSetpointClamp.iRunCount, Message := 'SetpointClamp#1 iRunCount');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbSetpointClamp.xCountOk, Message := 'SetpointClamp#1 xCountOk');
    AssertEquals_INT(Expected := 55,
                     Actual := fbSetpointClamp.iSetpoint_pct,
                     Message := 'SetpointClamp#1 iSetpoint_pct');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbSetpointClamp.xChainOk, Message := 'SetpointClamp#1 xChainOk');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbSetpointClamp.xRunMem, Message := 'SetpointClamp#1 xRunMem');

    // #2, t = 100 мс — 95 → 95 → 90 → 80
    GVL_S7Clock.tSimNow := T#100MS;
    fbSetpointClamp.iLevel_cm := 95;
    fbSetpointClamp();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbSetpointClamp.xPumpOn, Message := 'SetpointClamp#2 xPumpOn');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSetpointClamp.xLowLevel, Message := 'SetpointClamp#2 xLowLevel');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSetpointClamp.xHighPress, Message := 'SetpointClamp#2 xHighPress');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSetpointClamp.xAlarm, Message := 'SetpointClamp#2 xAlarm');
    AssertEquals_INT(Expected := 1, Actual := fbSetpointClamp.iRunCount, Message := 'SetpointClamp#2 iRunCount');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSetpointClamp.xCountOk, Message := 'SetpointClamp#2 xCountOk');
    AssertEquals_INT(Expected := 80,
                     Actual := fbSetpointClamp.iSetpoint_pct,
                     Message := 'SetpointClamp#2 iSetpoint_pct');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbSetpointClamp.xChainOk, Message := 'SetpointClamp#2 xChainOk');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbSetpointClamp.xRunMem, Message := 'SetpointClamp#2 xRunMem');

    // #3, t = 200 мс — 15 → 15 → 15 → 20
    GVL_S7Clock.tSimNow := T#200MS;
    fbSetpointClamp.iLevel_cm := 15;
    fbSetpointClamp.iLevelMin_cm := 10;
    fbSetpointClamp();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbSetpointClamp.xPumpOn, Message := 'SetpointClamp#3 xPumpOn');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSetpointClamp.xLowLevel, Message := 'SetpointClamp#3 xLowLevel');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSetpointClamp.xHighPress, Message := 'SetpointClamp#3 xHighPress');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSetpointClamp.xAlarm, Message := 'SetpointClamp#3 xAlarm');
    AssertEquals_INT(Expected := 1, Actual := fbSetpointClamp.iRunCount, Message := 'SetpointClamp#3 iRunCount');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSetpointClamp.xCountOk, Message := 'SetpointClamp#3 xCountOk');
    AssertEquals_INT(Expected := 20,
                     Actual := fbSetpointClamp.iSetpoint_pct,
                     Message := 'SetpointClamp#3 iSetpoint_pct');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbSetpointClamp.xChainOk, Message := 'SetpointClamp#3 xChainOk');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbSetpointClamp.xRunMem, Message := 'SetpointClamp#3 xRunMem');

    // #4, t = 300 мс — 5 → 5 → 10 → 20
    GVL_S7Clock.tSimNow := T#300MS;
    fbSetpointClamp.iLevel_cm := 5;
    fbSetpointClamp.iLevelMin_cm := 0;
    fbSetpointClamp();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbSetpointClamp.xPumpOn, Message := 'SetpointClamp#4 xPumpOn');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSetpointClamp.xLowLevel, Message := 'SetpointClamp#4 xLowLevel');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSetpointClamp.xHighPress, Message := 'SetpointClamp#4 xHighPress');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSetpointClamp.xAlarm, Message := 'SetpointClamp#4 xAlarm');
    AssertEquals_INT(Expected := 1, Actual := fbSetpointClamp.iRunCount, Message := 'SetpointClamp#4 iRunCount');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSetpointClamp.xCountOk, Message := 'SetpointClamp#4 xCountOk');
    AssertEquals_INT(Expected := 20,
                     Actual := fbSetpointClamp.iSetpoint_pct,
                     Message := 'SetpointClamp#4 iSetpoint_pct');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbSetpointClamp.xChainOk, Message := 'SetpointClamp#4 xChainOk');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbSetpointClamp.xRunMem, Message := 'SetpointClamp#4 xRunMem');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
