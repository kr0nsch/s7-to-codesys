// AUTO-GENERATED — не редактировать: scenarios/lang/FB_BackwashGraph.csv, сценарий AckSwitches
coUnit.TEST('AckSwitches');
IF NOT xAckSwitchesDone THEN
    xAckSwitchesDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;

    // #1, t = 0 мс — первый вызов: начальный шаг Idle
    GVL_S7Clock.tSimNow := T#0MS;
    fbAckSwitches.OFF_SQ := FALSE;
    fbAckSwitches.INIT_SQ := FALSE;
    fbAckSwitches.ACK_EF := FALSE;
    fbAckSwitches.xStart := FALSE;
    fbAckSwitches.xLevelLow := FALSE;
    fbAckSwitches.xLevelHigh := FALSE;
    fbAckSwitches.xShortWash := FALSE;
    fbAckSwitches.xPumpOk := TRUE;
    fbAckSwitches.xValveFault := FALSE;
    fbAckSwitches();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAckSwitches.ERR_FLT, Message := 'AckSwitches#1 ERR_FLT');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbAckSwitches.xReady, Message := 'AckSwitches#1 xReady');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAckSwitches.xDrainValve, Message := 'AckSwitches#1 xDrainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAckSwitches.xBlower, Message := 'AckSwitches#1 xBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAckSwitches.xAirValve, Message := 'AckSwitches#1 xAirValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAckSwitches.xWashPump, Message := 'AckSwitches#1 xWashPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAckSwitches.xInletValve, Message := 'AckSwitches#1 xInletValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAckSwitches.xWashActive, Message := 'AckSwitches#1 xWashActive');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAckSwitches.xValvesBusy, Message := 'AckSwitches#1 xValvesBusy');
    AssertEquals_INT(Expected := 0, Actual := fbAckSwitches.iWashCount, Message := 'AckSwitches#1 iWashCount');

    // #2, t = 100 мс — T1 Start: Drain, промывка №1, слив открыт
    GVL_S7Clock.tSimNow := T#100MS;
    fbAckSwitches.xStart := TRUE;
    fbAckSwitches();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAckSwitches.ERR_FLT, Message := 'AckSwitches#2 ERR_FLT');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAckSwitches.xReady, Message := 'AckSwitches#2 xReady');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbAckSwitches.xDrainValve, Message := 'AckSwitches#2 xDrainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAckSwitches.xBlower, Message := 'AckSwitches#2 xBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAckSwitches.xAirValve, Message := 'AckSwitches#2 xAirValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAckSwitches.xWashPump, Message := 'AckSwitches#2 xWashPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAckSwitches.xInletValve, Message := 'AckSwitches#2 xInletValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbAckSwitches.xWashActive, Message := 'AckSwitches#2 xWashActive');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbAckSwitches.xValvesBusy, Message := 'AckSwitches#2 xValvesBusy');
    AssertEquals_INT(Expected := 1, Actual := fbAckSwitches.iWashCount, Message := 'AckSwitches#2 iWashCount');

    // #3, t = 200 мс — слив
    GVL_S7Clock.tSimNow := T#200MS;
    fbAckSwitches.xStart := FALSE;
    fbAckSwitches();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAckSwitches.ERR_FLT, Message := 'AckSwitches#3 ERR_FLT');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAckSwitches.xReady, Message := 'AckSwitches#3 xReady');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbAckSwitches.xDrainValve, Message := 'AckSwitches#3 xDrainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAckSwitches.xBlower, Message := 'AckSwitches#3 xBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAckSwitches.xAirValve, Message := 'AckSwitches#3 xAirValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAckSwitches.xWashPump, Message := 'AckSwitches#3 xWashPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAckSwitches.xInletValve, Message := 'AckSwitches#3 xInletValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbAckSwitches.xWashActive, Message := 'AckSwitches#3 xWashActive');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbAckSwitches.xValvesBusy, Message := 'AckSwitches#3 xValvesBusy');
    AssertEquals_INT(Expected := 1, Actual := fbAckSwitches.iWashCount, Message := 'AckSwitches#3 iWashCount');

    // #4, t = 500 мс — ошибка контроля
    GVL_S7Clock.tSimNow := T#500MS;
    fbAckSwitches.xShortWash := TRUE;
    fbAckSwitches.xValveFault := TRUE;
    fbAckSwitches();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbAckSwitches.ERR_FLT, Message := 'AckSwitches#4 ERR_FLT');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAckSwitches.xReady, Message := 'AckSwitches#4 xReady');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbAckSwitches.xDrainValve, Message := 'AckSwitches#4 xDrainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAckSwitches.xBlower, Message := 'AckSwitches#4 xBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAckSwitches.xAirValve, Message := 'AckSwitches#4 xAirValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAckSwitches.xWashPump, Message := 'AckSwitches#4 xWashPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAckSwitches.xInletValve, Message := 'AckSwitches#4 xInletValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbAckSwitches.xWashActive, Message := 'AckSwitches#4 xWashActive');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbAckSwitches.xValvesBusy, Message := 'AckSwitches#4 xValvesBusy');
    AssertEquals_INT(Expected := 1, Actual := fbAckSwitches.iWashCount, Message := 'AckSwitches#4 iWashCount');

    // #5, t = 600 мс — квитирование и уровень: T3 ShortWash в том же вызове
    GVL_S7Clock.tSimNow := T#600MS;
    fbAckSwitches.ACK_EF := TRUE;
    fbAckSwitches.xLevelLow := TRUE;
    fbAckSwitches();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAckSwitches.ERR_FLT, Message := 'AckSwitches#5 ERR_FLT');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAckSwitches.xReady, Message := 'AckSwitches#5 xReady');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAckSwitches.xDrainValve, Message := 'AckSwitches#5 xDrainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAckSwitches.xBlower, Message := 'AckSwitches#5 xBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAckSwitches.xAirValve, Message := 'AckSwitches#5 xAirValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbAckSwitches.xWashPump, Message := 'AckSwitches#5 xWashPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAckSwitches.xInletValve, Message := 'AckSwitches#5 xInletValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbAckSwitches.xWashActive, Message := 'AckSwitches#5 xWashActive');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAckSwitches.xValvesBusy, Message := 'AckSwitches#5 xValvesBusy');
    AssertEquals_INT(Expected := 1, Actual := fbAckSwitches.iWashCount, Message := 'AckSwitches#5 iWashCount');

    // #6, t = 700 мс — QuickRinse: контроль Drain больше не действует
    GVL_S7Clock.tSimNow := T#700MS;
    fbAckSwitches.ACK_EF := FALSE;
    fbAckSwitches.xLevelLow := FALSE;
    fbAckSwitches();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAckSwitches.ERR_FLT, Message := 'AckSwitches#6 ERR_FLT');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAckSwitches.xReady, Message := 'AckSwitches#6 xReady');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAckSwitches.xDrainValve, Message := 'AckSwitches#6 xDrainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAckSwitches.xBlower, Message := 'AckSwitches#6 xBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAckSwitches.xAirValve, Message := 'AckSwitches#6 xAirValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbAckSwitches.xWashPump, Message := 'AckSwitches#6 xWashPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAckSwitches.xInletValve, Message := 'AckSwitches#6 xInletValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbAckSwitches.xWashActive, Message := 'AckSwitches#6 xWashActive');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAckSwitches.xValvesBusy, Message := 'AckSwitches#6 xValvesBusy');
    AssertEquals_INT(Expected := 1, Actual := fbAckSwitches.iWashCount, Message := 'AckSwitches#6 iWashCount');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
