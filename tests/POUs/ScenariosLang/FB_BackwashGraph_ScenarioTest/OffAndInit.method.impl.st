// AUTO-GENERATED — не редактировать: scenarios/lang/FB_BackwashGraph.csv, сценарий OffAndInit
coUnit.TEST('OffAndInit');
IF NOT xOffAndInitDone THEN
    xOffAndInitDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;

    // #1, t = 0 мс — первый вызов: начальный шаг Idle
    GVL_S7Clock.tSimNow := T#0MS;
    fbOffAndInit.OFF_SQ := FALSE;
    fbOffAndInit.INIT_SQ := FALSE;
    fbOffAndInit.ACK_EF := FALSE;
    fbOffAndInit.xStart := FALSE;
    fbOffAndInit.xLevelLow := FALSE;
    fbOffAndInit.xLevelHigh := FALSE;
    fbOffAndInit.xShortWash := FALSE;
    fbOffAndInit.xPumpOk := TRUE;
    fbOffAndInit.xValveFault := FALSE;
    fbOffAndInit();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbOffAndInit.ERR_FLT, Message := 'OffAndInit#1 ERR_FLT');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbOffAndInit.xReady, Message := 'OffAndInit#1 xReady');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbOffAndInit.xDrainValve, Message := 'OffAndInit#1 xDrainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbOffAndInit.xBlower, Message := 'OffAndInit#1 xBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbOffAndInit.xAirValve, Message := 'OffAndInit#1 xAirValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbOffAndInit.xWashPump, Message := 'OffAndInit#1 xWashPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbOffAndInit.xInletValve, Message := 'OffAndInit#1 xInletValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbOffAndInit.xWashActive, Message := 'OffAndInit#1 xWashActive');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbOffAndInit.xValvesBusy, Message := 'OffAndInit#1 xValvesBusy');
    AssertEquals_INT(Expected := 0, Actual := fbOffAndInit.iWashCount, Message := 'OffAndInit#1 iWashCount');

    // #2, t = 100 мс — T1 Start: Drain, промывка №1, слив открыт
    GVL_S7Clock.tSimNow := T#100MS;
    fbOffAndInit.xStart := TRUE;
    fbOffAndInit();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbOffAndInit.ERR_FLT, Message := 'OffAndInit#2 ERR_FLT');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbOffAndInit.xReady, Message := 'OffAndInit#2 xReady');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbOffAndInit.xDrainValve, Message := 'OffAndInit#2 xDrainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbOffAndInit.xBlower, Message := 'OffAndInit#2 xBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbOffAndInit.xAirValve, Message := 'OffAndInit#2 xAirValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbOffAndInit.xWashPump, Message := 'OffAndInit#2 xWashPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbOffAndInit.xInletValve, Message := 'OffAndInit#2 xInletValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbOffAndInit.xWashActive, Message := 'OffAndInit#2 xWashActive');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbOffAndInit.xValvesBusy, Message := 'OffAndInit#2 xValvesBusy');
    AssertEquals_INT(Expected := 1, Actual := fbOffAndInit.iWashCount, Message := 'OffAndInit#2 iWashCount');

    // #3, t = 200 мс — слив
    GVL_S7Clock.tSimNow := T#200MS;
    fbOffAndInit.xStart := FALSE;
    fbOffAndInit();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbOffAndInit.ERR_FLT, Message := 'OffAndInit#3 ERR_FLT');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbOffAndInit.xReady, Message := 'OffAndInit#3 xReady');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbOffAndInit.xDrainValve, Message := 'OffAndInit#3 xDrainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbOffAndInit.xBlower, Message := 'OffAndInit#3 xBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbOffAndInit.xAirValve, Message := 'OffAndInit#3 xAirValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbOffAndInit.xWashPump, Message := 'OffAndInit#3 xWashPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbOffAndInit.xInletValve, Message := 'OffAndInit#3 xInletValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbOffAndInit.xWashActive, Message := 'OffAndInit#3 xWashActive');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbOffAndInit.xValvesBusy, Message := 'OffAndInit#3 xValvesBusy');
    AssertEquals_INT(Expected := 1, Actual := fbOffAndInit.iWashCount, Message := 'OffAndInit#3 iWashCount');

    // #4, t = 300 мс — OFF_SQ: шаг Drain выключен, слив закрыт; промывка идёт (S держится)
    GVL_S7Clock.tSimNow := T#300MS;
    fbOffAndInit.OFF_SQ := TRUE;
    fbOffAndInit();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbOffAndInit.ERR_FLT, Message := 'OffAndInit#4 ERR_FLT');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbOffAndInit.xReady, Message := 'OffAndInit#4 xReady');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbOffAndInit.xDrainValve, Message := 'OffAndInit#4 xDrainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbOffAndInit.xBlower, Message := 'OffAndInit#4 xBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbOffAndInit.xAirValve, Message := 'OffAndInit#4 xAirValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbOffAndInit.xWashPump, Message := 'OffAndInit#4 xWashPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbOffAndInit.xInletValve, Message := 'OffAndInit#4 xInletValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbOffAndInit.xWashActive, Message := 'OffAndInit#4 xWashActive');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbOffAndInit.xValvesBusy, Message := 'OffAndInit#4 xValvesBusy');
    AssertEquals_INT(Expected := 1, Actual := fbOffAndInit.iWashCount, Message := 'OffAndInit#4 iWashCount');

    // #5, t = 400 мс — пуск без активных шагов: ничего
    GVL_S7Clock.tSimNow := T#400MS;
    fbOffAndInit.OFF_SQ := FALSE;
    fbOffAndInit.xStart := TRUE;
    fbOffAndInit();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbOffAndInit.ERR_FLT, Message := 'OffAndInit#5 ERR_FLT');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbOffAndInit.xReady, Message := 'OffAndInit#5 xReady');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbOffAndInit.xDrainValve, Message := 'OffAndInit#5 xDrainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbOffAndInit.xBlower, Message := 'OffAndInit#5 xBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbOffAndInit.xAirValve, Message := 'OffAndInit#5 xAirValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbOffAndInit.xWashPump, Message := 'OffAndInit#5 xWashPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbOffAndInit.xInletValve, Message := 'OffAndInit#5 xInletValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbOffAndInit.xWashActive, Message := 'OffAndInit#5 xWashActive');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbOffAndInit.xValvesBusy, Message := 'OffAndInit#5 xValvesBusy');
    AssertEquals_INT(Expected := 1, Actual := fbOffAndInit.iWashCount, Message := 'OffAndInit#5 iWashCount');

    // #6, t = 500 мс — INIT_SQ: Idle
    GVL_S7Clock.tSimNow := T#500MS;
    fbOffAndInit.INIT_SQ := TRUE;
    fbOffAndInit.xStart := FALSE;
    fbOffAndInit();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbOffAndInit.ERR_FLT, Message := 'OffAndInit#6 ERR_FLT');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbOffAndInit.xReady, Message := 'OffAndInit#6 xReady');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbOffAndInit.xDrainValve, Message := 'OffAndInit#6 xDrainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbOffAndInit.xBlower, Message := 'OffAndInit#6 xBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbOffAndInit.xAirValve, Message := 'OffAndInit#6 xAirValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbOffAndInit.xWashPump, Message := 'OffAndInit#6 xWashPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbOffAndInit.xInletValve, Message := 'OffAndInit#6 xInletValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbOffAndInit.xWashActive, Message := 'OffAndInit#6 xWashActive');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbOffAndInit.xValvesBusy, Message := 'OffAndInit#6 xValvesBusy');
    AssertEquals_INT(Expected := 1, Actual := fbOffAndInit.iWashCount, Message := 'OffAndInit#6 iWashCount');

    // #7, t = 600 мс — пуск: Drain, промывка №2
    GVL_S7Clock.tSimNow := T#600MS;
    fbOffAndInit.INIT_SQ := FALSE;
    fbOffAndInit.xStart := TRUE;
    fbOffAndInit();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbOffAndInit.ERR_FLT, Message := 'OffAndInit#7 ERR_FLT');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbOffAndInit.xReady, Message := 'OffAndInit#7 xReady');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbOffAndInit.xDrainValve, Message := 'OffAndInit#7 xDrainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbOffAndInit.xBlower, Message := 'OffAndInit#7 xBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbOffAndInit.xAirValve, Message := 'OffAndInit#7 xAirValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbOffAndInit.xWashPump, Message := 'OffAndInit#7 xWashPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbOffAndInit.xInletValve, Message := 'OffAndInit#7 xInletValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbOffAndInit.xWashActive, Message := 'OffAndInit#7 xWashActive');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbOffAndInit.xValvesBusy, Message := 'OffAndInit#7 xValvesBusy');
    AssertEquals_INT(Expected := 2, Actual := fbOffAndInit.iWashCount, Message := 'OffAndInit#7 iWashCount');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
