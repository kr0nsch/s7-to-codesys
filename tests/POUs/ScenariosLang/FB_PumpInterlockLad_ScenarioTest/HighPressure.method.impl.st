// AUTO-GENERATED — не редактировать: scenarios/lang/FB_PumpInterlockLad.csv, сценарий HighPressure
coUnit.TEST('HighPressure');
IF NOT xHighPressureDone THEN
    xHighPressureDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;

    // #1, t = 0 мс — включение №1
    GVL_S7Clock.tSimNow := T#0MS;
    fbHighPressure.xAutoReq := TRUE;
    fbHighPressure.iLevel_cm := 120;
    fbHighPressure.iLevelMin_cm := 50;
    fbHighPressure.iPressure_kPa := 400;
    fbHighPressure.iPressureMax_kPa := 600;
    fbHighPressure.xAck := FALSE;
    fbHighPressure.xMaint := FALSE;
    fbHighPressure();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbHighPressure.xPumpOn, Message := 'HighPressure#1 xPumpOn');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbHighPressure.xLowLevel, Message := 'HighPressure#1 xLowLevel');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbHighPressure.xHighPress, Message := 'HighPressure#1 xHighPress');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbHighPressure.xAlarm, Message := 'HighPressure#1 xAlarm');
    AssertEquals_INT(Expected := 1, Actual := fbHighPressure.iRunCount, Message := 'HighPressure#1 iRunCount');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbHighPressure.xCountOk, Message := 'HighPressure#1 xCountOk');
    AssertEquals_INT(Expected := 80, Actual := fbHighPressure.iSetpoint_pct, Message := 'HighPressure#1 iSetpoint_pct');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbHighPressure.xChainOk, Message := 'HighPressure#1 xChainOk');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbHighPressure.xRunMem, Message := 'HighPressure#1 xRunMem');

    // #2, t = 100 мс — 650 > 600: авария, насос выключен
    GVL_S7Clock.tSimNow := T#100MS;
    fbHighPressure.iPressure_kPa := 650;
    fbHighPressure();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbHighPressure.xPumpOn, Message := 'HighPressure#2 xPumpOn');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbHighPressure.xLowLevel, Message := 'HighPressure#2 xLowLevel');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbHighPressure.xHighPress, Message := 'HighPressure#2 xHighPress');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbHighPressure.xAlarm, Message := 'HighPressure#2 xAlarm');
    AssertEquals_INT(Expected := 1, Actual := fbHighPressure.iRunCount, Message := 'HighPressure#2 iRunCount');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbHighPressure.xCountOk, Message := 'HighPressure#2 xCountOk');
    AssertEquals_INT(Expected := 0, Actual := fbHighPressure.iSetpoint_pct, Message := 'HighPressure#2 iSetpoint_pct');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbHighPressure.xChainOk, Message := 'HighPressure#2 xChainOk');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbHighPressure.xRunMem, Message := 'HighPressure#2 xRunMem');

    // #3, t = 200 мс — 600 не больше 600: квитирование снимает, включение №2
    GVL_S7Clock.tSimNow := T#200MS;
    fbHighPressure.iPressure_kPa := 600;
    fbHighPressure.xAck := TRUE;
    fbHighPressure();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbHighPressure.xPumpOn, Message := 'HighPressure#3 xPumpOn');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbHighPressure.xLowLevel, Message := 'HighPressure#3 xLowLevel');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbHighPressure.xHighPress, Message := 'HighPressure#3 xHighPress');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbHighPressure.xAlarm, Message := 'HighPressure#3 xAlarm');
    AssertEquals_INT(Expected := 2, Actual := fbHighPressure.iRunCount, Message := 'HighPressure#3 iRunCount');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbHighPressure.xCountOk, Message := 'HighPressure#3 xCountOk');
    AssertEquals_INT(Expected := 80, Actual := fbHighPressure.iSetpoint_pct, Message := 'HighPressure#3 iSetpoint_pct');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbHighPressure.xChainOk, Message := 'HighPressure#3 xChainOk');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbHighPressure.xRunMem, Message := 'HighPressure#3 xRunMem');

    // #4, t = 300 мс — работает
    GVL_S7Clock.tSimNow := T#300MS;
    fbHighPressure.xAck := FALSE;
    fbHighPressure();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbHighPressure.xPumpOn, Message := 'HighPressure#4 xPumpOn');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbHighPressure.xLowLevel, Message := 'HighPressure#4 xLowLevel');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbHighPressure.xHighPress, Message := 'HighPressure#4 xHighPress');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbHighPressure.xAlarm, Message := 'HighPressure#4 xAlarm');
    AssertEquals_INT(Expected := 2, Actual := fbHighPressure.iRunCount, Message := 'HighPressure#4 iRunCount');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbHighPressure.xCountOk, Message := 'HighPressure#4 xCountOk');
    AssertEquals_INT(Expected := 80, Actual := fbHighPressure.iSetpoint_pct, Message := 'HighPressure#4 iSetpoint_pct');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbHighPressure.xChainOk, Message := 'HighPressure#4 xChainOk');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbHighPressure.xRunMem, Message := 'HighPressure#4 xRunMem');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
