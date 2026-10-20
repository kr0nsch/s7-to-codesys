// AUTO-GENERATED — не редактировать: scenarios/lang/FB_PumpInterlockLad.csv, сценарий AutoRunAndCount
coUnit.TEST('AutoRunAndCount');
IF NOT xAutoRunAndCountDone THEN
    xAutoRunAndCountDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;

    // #1, t = 0 мс — покой: уставка 0
    GVL_S7Clock.tSimNow := T#0MS;
    fbAutoRunAndCount.xAutoReq := FALSE;
    fbAutoRunAndCount.iLevel_cm := 120;
    fbAutoRunAndCount.iLevelMin_cm := 50;
    fbAutoRunAndCount.iPressure_kPa := 400;
    fbAutoRunAndCount.iPressureMax_kPa := 600;
    fbAutoRunAndCount.xAck := FALSE;
    fbAutoRunAndCount.xMaint := FALSE;
    fbAutoRunAndCount();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAutoRunAndCount.xPumpOn, Message := 'AutoRunAndCount#1 xPumpOn');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbAutoRunAndCount.xLowLevel,
                      Message := 'AutoRunAndCount#1 xLowLevel');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbAutoRunAndCount.xHighPress,
                      Message := 'AutoRunAndCount#1 xHighPress');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAutoRunAndCount.xAlarm, Message := 'AutoRunAndCount#1 xAlarm');
    AssertEquals_INT(Expected := 0, Actual := fbAutoRunAndCount.iRunCount, Message := 'AutoRunAndCount#1 iRunCount');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAutoRunAndCount.xCountOk, Message := 'AutoRunAndCount#1 xCountOk');
    AssertEquals_INT(Expected := 0,
                     Actual := fbAutoRunAndCount.iSetpoint_pct,
                     Message := 'AutoRunAndCount#1 iSetpoint_pct');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAutoRunAndCount.xChainOk, Message := 'AutoRunAndCount#1 xChainOk');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAutoRunAndCount.xRunMem, Message := 'AutoRunAndCount#1 xRunMem');

    // #2, t = 100 мс — включение №1: ENO = 1, уставка 120 → 100 → 90 → 80
    GVL_S7Clock.tSimNow := T#100MS;
    fbAutoRunAndCount.xAutoReq := TRUE;
    fbAutoRunAndCount();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbAutoRunAndCount.xPumpOn, Message := 'AutoRunAndCount#2 xPumpOn');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbAutoRunAndCount.xLowLevel,
                      Message := 'AutoRunAndCount#2 xLowLevel');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbAutoRunAndCount.xHighPress,
                      Message := 'AutoRunAndCount#2 xHighPress');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAutoRunAndCount.xAlarm, Message := 'AutoRunAndCount#2 xAlarm');
    AssertEquals_INT(Expected := 1, Actual := fbAutoRunAndCount.iRunCount, Message := 'AutoRunAndCount#2 iRunCount');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbAutoRunAndCount.xCountOk, Message := 'AutoRunAndCount#2 xCountOk');
    AssertEquals_INT(Expected := 80,
                     Actual := fbAutoRunAndCount.iSetpoint_pct,
                     Message := 'AutoRunAndCount#2 iSetpoint_pct');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbAutoRunAndCount.xChainOk, Message := 'AutoRunAndCount#2 xChainOk');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbAutoRunAndCount.xRunMem, Message := 'AutoRunAndCount#2 xRunMem');

    // #3, t = 200 мс — работает: фронта нет, ENO = 0
    GVL_S7Clock.tSimNow := T#200MS;
    fbAutoRunAndCount();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbAutoRunAndCount.xPumpOn, Message := 'AutoRunAndCount#3 xPumpOn');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbAutoRunAndCount.xLowLevel,
                      Message := 'AutoRunAndCount#3 xLowLevel');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbAutoRunAndCount.xHighPress,
                      Message := 'AutoRunAndCount#3 xHighPress');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAutoRunAndCount.xAlarm, Message := 'AutoRunAndCount#3 xAlarm');
    AssertEquals_INT(Expected := 1, Actual := fbAutoRunAndCount.iRunCount, Message := 'AutoRunAndCount#3 iRunCount');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAutoRunAndCount.xCountOk, Message := 'AutoRunAndCount#3 xCountOk');
    AssertEquals_INT(Expected := 80,
                     Actual := fbAutoRunAndCount.iSetpoint_pct,
                     Message := 'AutoRunAndCount#3 iSetpoint_pct');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbAutoRunAndCount.xChainOk, Message := 'AutoRunAndCount#3 xChainOk');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbAutoRunAndCount.xRunMem, Message := 'AutoRunAndCount#3 xRunMem');

    // #4, t = 300 мс — запрос снят: насос выключен, уставка 0 (MOVE)
    GVL_S7Clock.tSimNow := T#300MS;
    fbAutoRunAndCount.xAutoReq := FALSE;
    fbAutoRunAndCount();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAutoRunAndCount.xPumpOn, Message := 'AutoRunAndCount#4 xPumpOn');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbAutoRunAndCount.xLowLevel,
                      Message := 'AutoRunAndCount#4 xLowLevel');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbAutoRunAndCount.xHighPress,
                      Message := 'AutoRunAndCount#4 xHighPress');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAutoRunAndCount.xAlarm, Message := 'AutoRunAndCount#4 xAlarm');
    AssertEquals_INT(Expected := 1, Actual := fbAutoRunAndCount.iRunCount, Message := 'AutoRunAndCount#4 iRunCount');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAutoRunAndCount.xCountOk, Message := 'AutoRunAndCount#4 xCountOk');
    AssertEquals_INT(Expected := 0,
                     Actual := fbAutoRunAndCount.iSetpoint_pct,
                     Message := 'AutoRunAndCount#4 iSetpoint_pct');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAutoRunAndCount.xChainOk, Message := 'AutoRunAndCount#4 xChainOk');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAutoRunAndCount.xRunMem, Message := 'AutoRunAndCount#4 xRunMem');

    // #5, t = 400 мс — включение №2
    GVL_S7Clock.tSimNow := T#400MS;
    fbAutoRunAndCount.xAutoReq := TRUE;
    fbAutoRunAndCount();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbAutoRunAndCount.xPumpOn, Message := 'AutoRunAndCount#5 xPumpOn');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbAutoRunAndCount.xLowLevel,
                      Message := 'AutoRunAndCount#5 xLowLevel');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbAutoRunAndCount.xHighPress,
                      Message := 'AutoRunAndCount#5 xHighPress');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAutoRunAndCount.xAlarm, Message := 'AutoRunAndCount#5 xAlarm');
    AssertEquals_INT(Expected := 2, Actual := fbAutoRunAndCount.iRunCount, Message := 'AutoRunAndCount#5 iRunCount');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbAutoRunAndCount.xCountOk, Message := 'AutoRunAndCount#5 xCountOk');
    AssertEquals_INT(Expected := 80,
                     Actual := fbAutoRunAndCount.iSetpoint_pct,
                     Message := 'AutoRunAndCount#5 iSetpoint_pct');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbAutoRunAndCount.xChainOk, Message := 'AutoRunAndCount#5 xChainOk');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbAutoRunAndCount.xRunMem, Message := 'AutoRunAndCount#5 xRunMem');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
