// AUTO-GENERATED — не редактировать: scenarios/lang/FB_BackwashGraph.csv, сценарий ShortWash
coUnit.TEST('ShortWash');
IF NOT xShortWashDone THEN
    xShortWashDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;

    // #1, t = 0 мс — первый вызов: начальный шаг Idle
    GVL_S7Clock.tSimNow := T#0MS;
    fbShortWash.OFF_SQ := FALSE;
    fbShortWash.INIT_SQ := FALSE;
    fbShortWash.ACK_EF := FALSE;
    fbShortWash.xStart := FALSE;
    fbShortWash.xLevelLow := FALSE;
    fbShortWash.xLevelHigh := FALSE;
    fbShortWash.xShortWash := FALSE;
    fbShortWash.xPumpOk := TRUE;
    fbShortWash.xValveFault := FALSE;
    fbShortWash();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.ERR_FLT, Message := 'ShortWash#1 ERR_FLT');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbShortWash.xReady, Message := 'ShortWash#1 xReady');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.xDrainValve, Message := 'ShortWash#1 xDrainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.xBlower, Message := 'ShortWash#1 xBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.xAirValve, Message := 'ShortWash#1 xAirValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.xWashPump, Message := 'ShortWash#1 xWashPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.xInletValve, Message := 'ShortWash#1 xInletValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.xWashActive, Message := 'ShortWash#1 xWashActive');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.xValvesBusy, Message := 'ShortWash#1 xValvesBusy');
    AssertEquals_INT(Expected := 0, Actual := fbShortWash.iWashCount, Message := 'ShortWash#1 iWashCount');

    // #2, t = 100 мс — T1 Start: Drain, промывка №1, слив открыт
    GVL_S7Clock.tSimNow := T#100MS;
    fbShortWash.xStart := TRUE;
    fbShortWash();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.ERR_FLT, Message := 'ShortWash#2 ERR_FLT');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.xReady, Message := 'ShortWash#2 xReady');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbShortWash.xDrainValve, Message := 'ShortWash#2 xDrainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.xBlower, Message := 'ShortWash#2 xBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.xAirValve, Message := 'ShortWash#2 xAirValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.xWashPump, Message := 'ShortWash#2 xWashPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.xInletValve, Message := 'ShortWash#2 xInletValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbShortWash.xWashActive, Message := 'ShortWash#2 xWashActive');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbShortWash.xValvesBusy, Message := 'ShortWash#2 xValvesBusy');
    AssertEquals_INT(Expected := 1, Actual := fbShortWash.iWashCount, Message := 'ShortWash#2 iWashCount');

    // #3, t = 200 мс — слив
    GVL_S7Clock.tSimNow := T#200MS;
    fbShortWash.xStart := FALSE;
    fbShortWash();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.ERR_FLT, Message := 'ShortWash#3 ERR_FLT');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.xReady, Message := 'ShortWash#3 xReady');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbShortWash.xDrainValve, Message := 'ShortWash#3 xDrainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.xBlower, Message := 'ShortWash#3 xBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.xAirValve, Message := 'ShortWash#3 xAirValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.xWashPump, Message := 'ShortWash#3 xWashPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.xInletValve, Message := 'ShortWash#3 xInletValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbShortWash.xWashActive, Message := 'ShortWash#3 xWashActive');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbShortWash.xValvesBusy, Message := 'ShortWash#3 xValvesBusy');
    AssertEquals_INT(Expected := 1, Actual := fbShortWash.iWashCount, Message := 'ShortWash#3 iWashCount');

    // #4, t = 1000 мс — T3 ShortWash: QuickRinse
    GVL_S7Clock.tSimNow := T#1000MS;
    fbShortWash.xLevelLow := TRUE;
    fbShortWash.xShortWash := TRUE;
    fbShortWash();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.ERR_FLT, Message := 'ShortWash#4 ERR_FLT');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.xReady, Message := 'ShortWash#4 xReady');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.xDrainValve, Message := 'ShortWash#4 xDrainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.xBlower, Message := 'ShortWash#4 xBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.xAirValve, Message := 'ShortWash#4 xAirValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbShortWash.xWashPump, Message := 'ShortWash#4 xWashPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.xInletValve, Message := 'ShortWash#4 xInletValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbShortWash.xWashActive, Message := 'ShortWash#4 xWashActive');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.xValvesBusy, Message := 'ShortWash#4 xValvesBusy');
    AssertEquals_INT(Expected := 1, Actual := fbShortWash.iWashCount, Message := 'ShortWash#4 iWashCount');

    // #5, t = 1100 мс — быстрая отмывка
    GVL_S7Clock.tSimNow := T#1100MS;
    fbShortWash.xLevelLow := FALSE;
    fbShortWash();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.ERR_FLT, Message := 'ShortWash#5 ERR_FLT');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.xReady, Message := 'ShortWash#5 xReady');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.xDrainValve, Message := 'ShortWash#5 xDrainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.xBlower, Message := 'ShortWash#5 xBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.xAirValve, Message := 'ShortWash#5 xAirValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbShortWash.xWashPump, Message := 'ShortWash#5 xWashPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.xInletValve, Message := 'ShortWash#5 xInletValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbShortWash.xWashActive, Message := 'ShortWash#5 xWashActive');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.xValvesBusy, Message := 'ShortWash#5 xValvesBusy');
    AssertEquals_INT(Expected := 1, Actual := fbShortWash.iWashCount, Message := 'ShortWash#5 iWashCount');

    // #6, t = 2000 мс — T5 QuickDone: Refill
    GVL_S7Clock.tSimNow := T#2000MS;
    fbShortWash.xLevelHigh := TRUE;
    fbShortWash();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.ERR_FLT, Message := 'ShortWash#6 ERR_FLT');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.xReady, Message := 'ShortWash#6 xReady');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.xDrainValve, Message := 'ShortWash#6 xDrainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.xBlower, Message := 'ShortWash#6 xBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.xAirValve, Message := 'ShortWash#6 xAirValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.xWashPump, Message := 'ShortWash#6 xWashPump');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbShortWash.xInletValve, Message := 'ShortWash#6 xInletValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.xWashActive, Message := 'ShortWash#6 xWashActive');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbShortWash.xValvesBusy, Message := 'ShortWash#6 xValvesBusy');
    AssertEquals_INT(Expected := 1, Actual := fbShortWash.iWashCount, Message := 'ShortWash#6 iWashCount');

    // #7, t = 2100 мс — T6 Full: прыжок к Idle
    GVL_S7Clock.tSimNow := T#2100MS;
    fbShortWash();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.ERR_FLT, Message := 'ShortWash#7 ERR_FLT');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbShortWash.xReady, Message := 'ShortWash#7 xReady');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.xDrainValve, Message := 'ShortWash#7 xDrainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.xBlower, Message := 'ShortWash#7 xBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.xAirValve, Message := 'ShortWash#7 xAirValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.xWashPump, Message := 'ShortWash#7 xWashPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.xInletValve, Message := 'ShortWash#7 xInletValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.xWashActive, Message := 'ShortWash#7 xWashActive');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.xValvesBusy, Message := 'ShortWash#7 xValvesBusy');
    AssertEquals_INT(Expected := 1, Actual := fbShortWash.iWashCount, Message := 'ShortWash#7 iWashCount');

    // #8, t = 2200 мс — готов
    GVL_S7Clock.tSimNow := T#2200MS;
    fbShortWash.xLevelHigh := FALSE;
    fbShortWash.xShortWash := FALSE;
    fbShortWash();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.ERR_FLT, Message := 'ShortWash#8 ERR_FLT');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbShortWash.xReady, Message := 'ShortWash#8 xReady');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.xDrainValve, Message := 'ShortWash#8 xDrainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.xBlower, Message := 'ShortWash#8 xBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.xAirValve, Message := 'ShortWash#8 xAirValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.xWashPump, Message := 'ShortWash#8 xWashPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.xInletValve, Message := 'ShortWash#8 xInletValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.xWashActive, Message := 'ShortWash#8 xWashActive');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbShortWash.xValvesBusy, Message := 'ShortWash#8 xValvesBusy');
    AssertEquals_INT(Expected := 1, Actual := fbShortWash.iWashCount, Message := 'ShortWash#8 iWashCount');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
