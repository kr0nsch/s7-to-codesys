// AUTO-GENERATED — не редактировать: scenarios/lang/FB_BackwashGraph.csv, сценарий LongWash
coUnit.TEST('LongWash');
IF NOT xLongWashDone THEN
    xLongWashDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;

    // #1, t = 0 мс — первый вызов: начальный шаг Idle
    GVL_S7Clock.tSimNow := T#0MS;
    fbLongWash.OFF_SQ := FALSE;
    fbLongWash.INIT_SQ := FALSE;
    fbLongWash.ACK_EF := FALSE;
    fbLongWash.xStart := FALSE;
    fbLongWash.xLevelLow := FALSE;
    fbLongWash.xLevelHigh := FALSE;
    fbLongWash.xShortWash := FALSE;
    fbLongWash.xPumpOk := TRUE;
    fbLongWash.xValveFault := FALSE;
    fbLongWash();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.ERR_FLT, Message := 'LongWash#1 ERR_FLT');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbLongWash.xReady, Message := 'LongWash#1 xReady');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.xDrainValve, Message := 'LongWash#1 xDrainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.xBlower, Message := 'LongWash#1 xBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.xAirValve, Message := 'LongWash#1 xAirValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.xWashPump, Message := 'LongWash#1 xWashPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.xInletValve, Message := 'LongWash#1 xInletValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.xWashActive, Message := 'LongWash#1 xWashActive');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.xValvesBusy, Message := 'LongWash#1 xValvesBusy');
    AssertEquals_INT(Expected := 0, Actual := fbLongWash.iWashCount, Message := 'LongWash#1 iWashCount');

    // #2, t = 100 мс — T1 Start: Drain, промывка №1, слив открыт
    GVL_S7Clock.tSimNow := T#100MS;
    fbLongWash.xStart := TRUE;
    fbLongWash();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.ERR_FLT, Message := 'LongWash#2 ERR_FLT');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.xReady, Message := 'LongWash#2 xReady');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbLongWash.xDrainValve, Message := 'LongWash#2 xDrainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.xBlower, Message := 'LongWash#2 xBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.xAirValve, Message := 'LongWash#2 xAirValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.xWashPump, Message := 'LongWash#2 xWashPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.xInletValve, Message := 'LongWash#2 xInletValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbLongWash.xWashActive, Message := 'LongWash#2 xWashActive');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbLongWash.xValvesBusy, Message := 'LongWash#2 xValvesBusy');
    AssertEquals_INT(Expected := 1, Actual := fbLongWash.iWashCount, Message := 'LongWash#2 iWashCount');

    // #3, t = 200 мс — слив
    GVL_S7Clock.tSimNow := T#200MS;
    fbLongWash.xStart := FALSE;
    fbLongWash();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.ERR_FLT, Message := 'LongWash#3 ERR_FLT');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.xReady, Message := 'LongWash#3 xReady');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbLongWash.xDrainValve, Message := 'LongWash#3 xDrainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.xBlower, Message := 'LongWash#3 xBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.xAirValve, Message := 'LongWash#3 xAirValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.xWashPump, Message := 'LongWash#3 xWashPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.xInletValve, Message := 'LongWash#3 xInletValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbLongWash.xWashActive, Message := 'LongWash#3 xWashActive');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbLongWash.xValvesBusy, Message := 'LongWash#3 xValvesBusy');
    AssertEquals_INT(Expected := 1, Actual := fbLongWash.iWashCount, Message := 'LongWash#3 iWashCount');

    // #4, t = 1000 мс — T2 LongWash: параллельно Air и Rinse
    GVL_S7Clock.tSimNow := T#1000MS;
    fbLongWash.xLevelLow := TRUE;
    fbLongWash();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.ERR_FLT, Message := 'LongWash#4 ERR_FLT');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.xReady, Message := 'LongWash#4 xReady');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.xDrainValve, Message := 'LongWash#4 xDrainValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbLongWash.xBlower, Message := 'LongWash#4 xBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.xAirValve, Message := 'LongWash#4 xAirValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbLongWash.xWashPump, Message := 'LongWash#4 xWashPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.xInletValve, Message := 'LongWash#4 xInletValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbLongWash.xWashActive, Message := 'LongWash#4 xWashActive');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.xValvesBusy, Message := 'LongWash#4 xValvesBusy');
    AssertEquals_INT(Expected := 1, Actual := fbLongWash.iWashCount, Message := 'LongWash#4 iWashCount');

    // #5, t = 1100 мс — воздуходувка и насос; задвижка воздуха ещё закрыта
    GVL_S7Clock.tSimNow := T#1100MS;
    fbLongWash.xLevelLow := FALSE;
    fbLongWash();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.ERR_FLT, Message := 'LongWash#5 ERR_FLT');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.xReady, Message := 'LongWash#5 xReady');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.xDrainValve, Message := 'LongWash#5 xDrainValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbLongWash.xBlower, Message := 'LongWash#5 xBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.xAirValve, Message := 'LongWash#5 xAirValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbLongWash.xWashPump, Message := 'LongWash#5 xWashPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.xInletValve, Message := 'LongWash#5 xInletValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbLongWash.xWashActive, Message := 'LongWash#5 xWashActive');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.xValvesBusy, Message := 'LongWash#5 xValvesBusy');
    AssertEquals_INT(Expected := 1, Actual := fbLongWash.iWashCount, Message := 'LongWash#5 iWashCount');

    // #6, t = 3000 мс, на пороге таймера — 2 с продувки: задвижка воздуха открыта (D)
    GVL_S7Clock.tSimNow := T#3000MS;
    fbLongWash();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.ERR_FLT, Message := 'LongWash#6 ERR_FLT');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.xReady, Message := 'LongWash#6 xReady');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.xDrainValve, Message := 'LongWash#6 xDrainValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbLongWash.xBlower, Message := 'LongWash#6 xBlower');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbLongWash.xAirValve, Message := 'LongWash#6 xAirValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbLongWash.xWashPump, Message := 'LongWash#6 xWashPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.xInletValve, Message := 'LongWash#6 xInletValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbLongWash.xWashActive, Message := 'LongWash#6 xWashActive');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.xValvesBusy, Message := 'LongWash#6 xValvesBusy');
    AssertEquals_INT(Expected := 1, Actual := fbLongWash.iWashCount, Message := 'LongWash#6 iWashCount');

    // #7, t = 10700 мс — 9,7 с: синхронизация ещё не прошла
    GVL_S7Clock.tSimNow := T#10700MS;
    fbLongWash();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.ERR_FLT, Message := 'LongWash#7 ERR_FLT');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.xReady, Message := 'LongWash#7 xReady');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.xDrainValve, Message := 'LongWash#7 xDrainValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbLongWash.xBlower, Message := 'LongWash#7 xBlower');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbLongWash.xAirValve, Message := 'LongWash#7 xAirValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbLongWash.xWashPump, Message := 'LongWash#7 xWashPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.xInletValve, Message := 'LongWash#7 xInletValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbLongWash.xWashActive, Message := 'LongWash#7 xWashActive');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.xValvesBusy, Message := 'LongWash#7 xValvesBusy');
    AssertEquals_INT(Expected := 1, Actual := fbLongWash.iWashCount, Message := 'LongWash#7 iWashCount');

    // #8, t = 11000 мс, на пороге таймера — 10 с: T4 AirDone — Refill, подача открыта
    GVL_S7Clock.tSimNow := T#11000MS;
    fbLongWash();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.ERR_FLT, Message := 'LongWash#8 ERR_FLT');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.xReady, Message := 'LongWash#8 xReady');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.xDrainValve, Message := 'LongWash#8 xDrainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.xBlower, Message := 'LongWash#8 xBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.xAirValve, Message := 'LongWash#8 xAirValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.xWashPump, Message := 'LongWash#8 xWashPump');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbLongWash.xInletValve, Message := 'LongWash#8 xInletValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.xWashActive, Message := 'LongWash#8 xWashActive');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbLongWash.xValvesBusy, Message := 'LongWash#8 xValvesBusy');
    AssertEquals_INT(Expected := 1, Actual := fbLongWash.iWashCount, Message := 'LongWash#8 iWashCount');

    // #9, t = 11500 мс — T6 Full: прыжок к Idle
    GVL_S7Clock.tSimNow := T#11500MS;
    fbLongWash.xLevelHigh := TRUE;
    fbLongWash();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.ERR_FLT, Message := 'LongWash#9 ERR_FLT');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbLongWash.xReady, Message := 'LongWash#9 xReady');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.xDrainValve, Message := 'LongWash#9 xDrainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.xBlower, Message := 'LongWash#9 xBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.xAirValve, Message := 'LongWash#9 xAirValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.xWashPump, Message := 'LongWash#9 xWashPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.xInletValve, Message := 'LongWash#9 xInletValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.xWashActive, Message := 'LongWash#9 xWashActive');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.xValvesBusy, Message := 'LongWash#9 xValvesBusy');
    AssertEquals_INT(Expected := 1, Actual := fbLongWash.iWashCount, Message := 'LongWash#9 iWashCount');

    // #10, t = 11600 мс — готов к новой промывке
    GVL_S7Clock.tSimNow := T#11600MS;
    fbLongWash.xLevelHigh := FALSE;
    fbLongWash();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.ERR_FLT, Message := 'LongWash#10 ERR_FLT');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbLongWash.xReady, Message := 'LongWash#10 xReady');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.xDrainValve, Message := 'LongWash#10 xDrainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.xBlower, Message := 'LongWash#10 xBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.xAirValve, Message := 'LongWash#10 xAirValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.xWashPump, Message := 'LongWash#10 xWashPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.xInletValve, Message := 'LongWash#10 xInletValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.xWashActive, Message := 'LongWash#10 xWashActive');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbLongWash.xValvesBusy, Message := 'LongWash#10 xValvesBusy');
    AssertEquals_INT(Expected := 1, Actual := fbLongWash.iWashCount, Message := 'LongWash#10 iWashCount');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
