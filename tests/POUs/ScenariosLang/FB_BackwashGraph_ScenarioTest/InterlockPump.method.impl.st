// AUTO-GENERATED — не редактировать: scenarios/lang/FB_BackwashGraph.csv, сценарий InterlockPump
coUnit.TEST('InterlockPump');
IF NOT xInterlockPumpDone THEN
    xInterlockPumpDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;

    // #1, t = 0 мс — первый вызов: начальный шаг Idle
    GVL_S7Clock.tSimNow := T#0MS;
    fbInterlockPump.OFF_SQ := FALSE;
    fbInterlockPump.INIT_SQ := FALSE;
    fbInterlockPump.ACK_EF := FALSE;
    fbInterlockPump.xStart := FALSE;
    fbInterlockPump.xLevelLow := FALSE;
    fbInterlockPump.xLevelHigh := FALSE;
    fbInterlockPump.xShortWash := FALSE;
    fbInterlockPump.xPumpOk := TRUE;
    fbInterlockPump.xValveFault := FALSE;
    fbInterlockPump();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbInterlockPump.ERR_FLT, Message := 'InterlockPump#1 ERR_FLT');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbInterlockPump.xReady, Message := 'InterlockPump#1 xReady');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbInterlockPump.xDrainValve,
                      Message := 'InterlockPump#1 xDrainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbInterlockPump.xBlower, Message := 'InterlockPump#1 xBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbInterlockPump.xAirValve, Message := 'InterlockPump#1 xAirValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbInterlockPump.xWashPump, Message := 'InterlockPump#1 xWashPump');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbInterlockPump.xInletValve,
                      Message := 'InterlockPump#1 xInletValve');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbInterlockPump.xWashActive,
                      Message := 'InterlockPump#1 xWashActive');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbInterlockPump.xValvesBusy,
                      Message := 'InterlockPump#1 xValvesBusy');
    AssertEquals_INT(Expected := 0, Actual := fbInterlockPump.iWashCount, Message := 'InterlockPump#1 iWashCount');

    // #2, t = 100 мс — T1 Start: Drain, промывка №1, слив открыт
    GVL_S7Clock.tSimNow := T#100MS;
    fbInterlockPump.xStart := TRUE;
    fbInterlockPump();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbInterlockPump.ERR_FLT, Message := 'InterlockPump#2 ERR_FLT');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbInterlockPump.xReady, Message := 'InterlockPump#2 xReady');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbInterlockPump.xDrainValve,
                      Message := 'InterlockPump#2 xDrainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbInterlockPump.xBlower, Message := 'InterlockPump#2 xBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbInterlockPump.xAirValve, Message := 'InterlockPump#2 xAirValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbInterlockPump.xWashPump, Message := 'InterlockPump#2 xWashPump');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbInterlockPump.xInletValve,
                      Message := 'InterlockPump#2 xInletValve');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbInterlockPump.xWashActive,
                      Message := 'InterlockPump#2 xWashActive');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbInterlockPump.xValvesBusy,
                      Message := 'InterlockPump#2 xValvesBusy');
    AssertEquals_INT(Expected := 1, Actual := fbInterlockPump.iWashCount, Message := 'InterlockPump#2 iWashCount');

    // #3, t = 200 мс — слив
    GVL_S7Clock.tSimNow := T#200MS;
    fbInterlockPump.xStart := FALSE;
    fbInterlockPump();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbInterlockPump.ERR_FLT, Message := 'InterlockPump#3 ERR_FLT');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbInterlockPump.xReady, Message := 'InterlockPump#3 xReady');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbInterlockPump.xDrainValve,
                      Message := 'InterlockPump#3 xDrainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbInterlockPump.xBlower, Message := 'InterlockPump#3 xBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbInterlockPump.xAirValve, Message := 'InterlockPump#3 xAirValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbInterlockPump.xWashPump, Message := 'InterlockPump#3 xWashPump');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbInterlockPump.xInletValve,
                      Message := 'InterlockPump#3 xInletValve');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbInterlockPump.xWashActive,
                      Message := 'InterlockPump#3 xWashActive');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbInterlockPump.xValvesBusy,
                      Message := 'InterlockPump#3 xValvesBusy');
    AssertEquals_INT(Expected := 1, Actual := fbInterlockPump.iWashCount, Message := 'InterlockPump#3 iWashCount');

    // #4, t = 1000 мс — Air и Rinse: насос промывки включён
    GVL_S7Clock.tSimNow := T#1000MS;
    fbInterlockPump.xLevelLow := TRUE;
    fbInterlockPump();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbInterlockPump.ERR_FLT, Message := 'InterlockPump#4 ERR_FLT');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbInterlockPump.xReady, Message := 'InterlockPump#4 xReady');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbInterlockPump.xDrainValve,
                      Message := 'InterlockPump#4 xDrainValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbInterlockPump.xBlower, Message := 'InterlockPump#4 xBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbInterlockPump.xAirValve, Message := 'InterlockPump#4 xAirValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbInterlockPump.xWashPump, Message := 'InterlockPump#4 xWashPump');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbInterlockPump.xInletValve,
                      Message := 'InterlockPump#4 xInletValve');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbInterlockPump.xWashActive,
                      Message := 'InterlockPump#4 xWashActive');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbInterlockPump.xValvesBusy,
                      Message := 'InterlockPump#4 xValvesBusy');
    AssertEquals_INT(Expected := 1, Actual := fbInterlockPump.iWashCount, Message := 'InterlockPump#4 iWashCount');

    // #5, t = 1100 мс — насос неисправен: блокировка не выполнена
    GVL_S7Clock.tSimNow := T#1100MS;
    fbInterlockPump.xLevelLow := FALSE;
    fbInterlockPump.xPumpOk := FALSE;
    fbInterlockPump();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbInterlockPump.ERR_FLT, Message := 'InterlockPump#5 ERR_FLT');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbInterlockPump.xReady, Message := 'InterlockPump#5 xReady');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbInterlockPump.xDrainValve,
                      Message := 'InterlockPump#5 xDrainValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbInterlockPump.xBlower, Message := 'InterlockPump#5 xBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbInterlockPump.xAirValve, Message := 'InterlockPump#5 xAirValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbInterlockPump.xWashPump, Message := 'InterlockPump#5 xWashPump');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbInterlockPump.xInletValve,
                      Message := 'InterlockPump#5 xInletValve');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbInterlockPump.xWashActive,
                      Message := 'InterlockPump#5 xWashActive');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbInterlockPump.xValvesBusy,
                      Message := 'InterlockPump#5 xValvesBusy');
    AssertEquals_INT(Expected := 1, Actual := fbInterlockPump.iWashCount, Message := 'InterlockPump#5 iWashCount');

    // #6, t = 1200 мс — насос исправен: снова включён
    GVL_S7Clock.tSimNow := T#1200MS;
    fbInterlockPump.xPumpOk := TRUE;
    fbInterlockPump();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbInterlockPump.ERR_FLT, Message := 'InterlockPump#6 ERR_FLT');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbInterlockPump.xReady, Message := 'InterlockPump#6 xReady');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbInterlockPump.xDrainValve,
                      Message := 'InterlockPump#6 xDrainValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbInterlockPump.xBlower, Message := 'InterlockPump#6 xBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbInterlockPump.xAirValve, Message := 'InterlockPump#6 xAirValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbInterlockPump.xWashPump, Message := 'InterlockPump#6 xWashPump');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbInterlockPump.xInletValve,
                      Message := 'InterlockPump#6 xInletValve');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbInterlockPump.xWashActive,
                      Message := 'InterlockPump#6 xWashActive');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbInterlockPump.xValvesBusy,
                      Message := 'InterlockPump#6 xValvesBusy');
    AssertEquals_INT(Expected := 1, Actual := fbInterlockPump.iWashCount, Message := 'InterlockPump#6 iWashCount');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
