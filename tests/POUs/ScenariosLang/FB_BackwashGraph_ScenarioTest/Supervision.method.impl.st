// AUTO-GENERATED — не редактировать: scenarios/lang/FB_BackwashGraph.csv, сценарий Supervision
coUnit.TEST('Supervision');
IF NOT xSupervisionDone THEN
    xSupervisionDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;

    // #1, t = 0 мс — первый вызов: начальный шаг Idle
    GVL_S7Clock.tSimNow := T#0MS;
    fbSupervision.OFF_SQ := FALSE;
    fbSupervision.INIT_SQ := FALSE;
    fbSupervision.ACK_EF := FALSE;
    fbSupervision.xStart := FALSE;
    fbSupervision.xLevelLow := FALSE;
    fbSupervision.xLevelHigh := FALSE;
    fbSupervision.xShortWash := FALSE;
    fbSupervision.xPumpOk := TRUE;
    fbSupervision.xValveFault := FALSE;
    fbSupervision();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSupervision.ERR_FLT, Message := 'Supervision#1 ERR_FLT');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbSupervision.xReady, Message := 'Supervision#1 xReady');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSupervision.xDrainValve, Message := 'Supervision#1 xDrainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSupervision.xBlower, Message := 'Supervision#1 xBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSupervision.xAirValve, Message := 'Supervision#1 xAirValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSupervision.xWashPump, Message := 'Supervision#1 xWashPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSupervision.xInletValve, Message := 'Supervision#1 xInletValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSupervision.xWashActive, Message := 'Supervision#1 xWashActive');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSupervision.xValvesBusy, Message := 'Supervision#1 xValvesBusy');
    AssertEquals_INT(Expected := 0, Actual := fbSupervision.iWashCount, Message := 'Supervision#1 iWashCount');

    // #2, t = 100 мс — T1 Start: Drain, промывка №1, слив открыт
    GVL_S7Clock.tSimNow := T#100MS;
    fbSupervision.xStart := TRUE;
    fbSupervision();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSupervision.ERR_FLT, Message := 'Supervision#2 ERR_FLT');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSupervision.xReady, Message := 'Supervision#2 xReady');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbSupervision.xDrainValve, Message := 'Supervision#2 xDrainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSupervision.xBlower, Message := 'Supervision#2 xBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSupervision.xAirValve, Message := 'Supervision#2 xAirValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSupervision.xWashPump, Message := 'Supervision#2 xWashPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSupervision.xInletValve, Message := 'Supervision#2 xInletValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbSupervision.xWashActive, Message := 'Supervision#2 xWashActive');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbSupervision.xValvesBusy, Message := 'Supervision#2 xValvesBusy');
    AssertEquals_INT(Expected := 1, Actual := fbSupervision.iWashCount, Message := 'Supervision#2 iWashCount');

    // #3, t = 200 мс — слив
    GVL_S7Clock.tSimNow := T#200MS;
    fbSupervision.xStart := FALSE;
    fbSupervision();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSupervision.ERR_FLT, Message := 'Supervision#3 ERR_FLT');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSupervision.xReady, Message := 'Supervision#3 xReady');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbSupervision.xDrainValve, Message := 'Supervision#3 xDrainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSupervision.xBlower, Message := 'Supervision#3 xBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSupervision.xAirValve, Message := 'Supervision#3 xAirValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSupervision.xWashPump, Message := 'Supervision#3 xWashPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSupervision.xInletValve, Message := 'Supervision#3 xInletValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbSupervision.xWashActive, Message := 'Supervision#3 xWashActive');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbSupervision.xValvesBusy, Message := 'Supervision#3 xValvesBusy');
    AssertEquals_INT(Expected := 1, Actual := fbSupervision.iWashCount, Message := 'Supervision#3 iWashCount');

    // #4, t = 500 мс — неисправность задвижки: ERR_FLT
    GVL_S7Clock.tSimNow := T#500MS;
    fbSupervision.xValveFault := TRUE;
    fbSupervision();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbSupervision.ERR_FLT, Message := 'Supervision#4 ERR_FLT');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSupervision.xReady, Message := 'Supervision#4 xReady');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbSupervision.xDrainValve, Message := 'Supervision#4 xDrainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSupervision.xBlower, Message := 'Supervision#4 xBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSupervision.xAirValve, Message := 'Supervision#4 xAirValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSupervision.xWashPump, Message := 'Supervision#4 xWashPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSupervision.xInletValve, Message := 'Supervision#4 xInletValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbSupervision.xWashActive, Message := 'Supervision#4 xWashActive');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbSupervision.xValvesBusy, Message := 'Supervision#4 xValvesBusy');
    AssertEquals_INT(Expected := 1, Actual := fbSupervision.iWashCount, Message := 'Supervision#4 iWashCount');

    // #5, t = 600 мс — уровень низкий, но переход заблокирован ошибкой
    GVL_S7Clock.tSimNow := T#600MS;
    fbSupervision.xLevelLow := TRUE;
    fbSupervision();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbSupervision.ERR_FLT, Message := 'Supervision#5 ERR_FLT');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSupervision.xReady, Message := 'Supervision#5 xReady');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbSupervision.xDrainValve, Message := 'Supervision#5 xDrainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSupervision.xBlower, Message := 'Supervision#5 xBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSupervision.xAirValve, Message := 'Supervision#5 xAirValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSupervision.xWashPump, Message := 'Supervision#5 xWashPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSupervision.xInletValve, Message := 'Supervision#5 xInletValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbSupervision.xWashActive, Message := 'Supervision#5 xWashActive');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbSupervision.xValvesBusy, Message := 'Supervision#5 xValvesBusy');
    AssertEquals_INT(Expected := 1, Actual := fbSupervision.iWashCount, Message := 'Supervision#5 iWashCount');

    // #6, t = 700 мс — квитирование при неисправности: ошибка сразу снова
    GVL_S7Clock.tSimNow := T#700MS;
    fbSupervision.ACK_EF := TRUE;
    fbSupervision.xLevelLow := FALSE;
    fbSupervision();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbSupervision.ERR_FLT, Message := 'Supervision#6 ERR_FLT');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSupervision.xReady, Message := 'Supervision#6 xReady');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbSupervision.xDrainValve, Message := 'Supervision#6 xDrainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSupervision.xBlower, Message := 'Supervision#6 xBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSupervision.xAirValve, Message := 'Supervision#6 xAirValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSupervision.xWashPump, Message := 'Supervision#6 xWashPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSupervision.xInletValve, Message := 'Supervision#6 xInletValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbSupervision.xWashActive, Message := 'Supervision#6 xWashActive');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbSupervision.xValvesBusy, Message := 'Supervision#6 xValvesBusy');
    AssertEquals_INT(Expected := 1, Actual := fbSupervision.iWashCount, Message := 'Supervision#6 iWashCount');

    // #7, t = 800 мс — неисправность ушла, ошибка держится
    GVL_S7Clock.tSimNow := T#800MS;
    fbSupervision.ACK_EF := FALSE;
    fbSupervision.xValveFault := FALSE;
    fbSupervision();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbSupervision.ERR_FLT, Message := 'Supervision#7 ERR_FLT');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSupervision.xReady, Message := 'Supervision#7 xReady');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbSupervision.xDrainValve, Message := 'Supervision#7 xDrainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSupervision.xBlower, Message := 'Supervision#7 xBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSupervision.xAirValve, Message := 'Supervision#7 xAirValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSupervision.xWashPump, Message := 'Supervision#7 xWashPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSupervision.xInletValve, Message := 'Supervision#7 xInletValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbSupervision.xWashActive, Message := 'Supervision#7 xWashActive');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbSupervision.xValvesBusy, Message := 'Supervision#7 xValvesBusy');
    AssertEquals_INT(Expected := 1, Actual := fbSupervision.iWashCount, Message := 'Supervision#7 iWashCount');

    // #8, t = 900 мс — квитирование: ошибка снята
    GVL_S7Clock.tSimNow := T#900MS;
    fbSupervision.ACK_EF := TRUE;
    fbSupervision();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSupervision.ERR_FLT, Message := 'Supervision#8 ERR_FLT');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSupervision.xReady, Message := 'Supervision#8 xReady');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbSupervision.xDrainValve, Message := 'Supervision#8 xDrainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSupervision.xBlower, Message := 'Supervision#8 xBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSupervision.xAirValve, Message := 'Supervision#8 xAirValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSupervision.xWashPump, Message := 'Supervision#8 xWashPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSupervision.xInletValve, Message := 'Supervision#8 xInletValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbSupervision.xWashActive, Message := 'Supervision#8 xWashActive');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbSupervision.xValvesBusy, Message := 'Supervision#8 xValvesBusy');
    AssertEquals_INT(Expected := 1, Actual := fbSupervision.iWashCount, Message := 'Supervision#8 iWashCount');

    // #9, t = 1000 мс — T2 LongWash: Air и Rinse
    GVL_S7Clock.tSimNow := T#1000MS;
    fbSupervision.ACK_EF := FALSE;
    fbSupervision.xLevelLow := TRUE;
    fbSupervision();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSupervision.ERR_FLT, Message := 'Supervision#9 ERR_FLT');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSupervision.xReady, Message := 'Supervision#9 xReady');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSupervision.xDrainValve, Message := 'Supervision#9 xDrainValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbSupervision.xBlower, Message := 'Supervision#9 xBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSupervision.xAirValve, Message := 'Supervision#9 xAirValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbSupervision.xWashPump, Message := 'Supervision#9 xWashPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSupervision.xInletValve, Message := 'Supervision#9 xInletValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbSupervision.xWashActive, Message := 'Supervision#9 xWashActive');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSupervision.xValvesBusy, Message := 'Supervision#9 xValvesBusy');
    AssertEquals_INT(Expected := 1, Actual := fbSupervision.iWashCount, Message := 'Supervision#9 iWashCount');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
