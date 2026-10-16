// AUTO-GENERATED — не редактировать: scenarios/FB_Totalizer.csv, сценарий CutoffAndEnable
coUnit.TEST('CutoffAndEnable');
IF NOT xCutoffAndEnableDone THEN
    xCutoffAndEnableDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;

    // #1, t = 0 мс — 0.25 < отсечки 0.5: не считается
    GVL_S7Clock.tSimNow := T#0MS;
    fbCutoffAndEnable.flow := 0.25;
    fbCutoffAndEnable.cycleTime := T#1000MS;
    fbCutoffAndEnable.lowFlowCutoff := 0.5;
    fbCutoffAndEnable.enable := TRUE;
    fbCutoffAndEnable.reset := FALSE;
    fbCutoffAndEnable.pulseVolume := 1.0;
    fbCutoffAndEnable();
    AssertEquals_LREAL(Expected := 0.0,
                       Actual := fbCutoffAndEnable.total,
                       Delta := 0.000001,
                       Message := 'CutoffAndEnable#1 total');
    AssertEquals_LREAL(Expected := 0.0,
                       Actual := fbCutoffAndEnable.lifetimeTotal,
                       Delta := 0.000001,
                       Message := 'CutoffAndEnable#1 lifetimeTotal');
    AssertEquals_DINT(Expected := 0, Actual := fbCutoffAndEnable.pulseCount, Message := 'CutoffAndEnable#1 pulseCount');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCutoffAndEnable.pulse, Message := 'CutoffAndEnable#1 pulse');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbCutoffAndEnable.cutoffActive,
                      Message := 'CutoffAndEnable#1 cutoffActive');

    // #2, t = 1000 мс — обратный расход ниже отсечки: не считается
    GVL_S7Clock.tSimNow := T#1000MS;
    fbCutoffAndEnable.flow := -10.0;
    fbCutoffAndEnable();
    AssertEquals_LREAL(Expected := 0.0,
                       Actual := fbCutoffAndEnable.total,
                       Delta := 0.000001,
                       Message := 'CutoffAndEnable#2 total');
    AssertEquals_LREAL(Expected := 0.0,
                       Actual := fbCutoffAndEnable.lifetimeTotal,
                       Delta := 0.000001,
                       Message := 'CutoffAndEnable#2 lifetimeTotal');
    AssertEquals_DINT(Expected := 0, Actual := fbCutoffAndEnable.pulseCount, Message := 'CutoffAndEnable#2 pulseCount');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCutoffAndEnable.pulse, Message := 'CutoffAndEnable#2 pulse');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbCutoffAndEnable.cutoffActive,
                      Message := 'CutoffAndEnable#2 cutoffActive');

    // #3, t = 2000 мс — интегрирование запрещено (отсечка не активна)
    GVL_S7Clock.tSimNow := T#2000MS;
    fbCutoffAndEnable.flow := 450.0;
    fbCutoffAndEnable.enable := FALSE;
    fbCutoffAndEnable();
    AssertEquals_LREAL(Expected := 0.0,
                       Actual := fbCutoffAndEnable.total,
                       Delta := 0.000001,
                       Message := 'CutoffAndEnable#3 total');
    AssertEquals_LREAL(Expected := 0.0,
                       Actual := fbCutoffAndEnable.lifetimeTotal,
                       Delta := 0.000001,
                       Message := 'CutoffAndEnable#3 lifetimeTotal');
    AssertEquals_DINT(Expected := 0, Actual := fbCutoffAndEnable.pulseCount, Message := 'CutoffAndEnable#3 pulseCount');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCutoffAndEnable.pulse, Message := 'CutoffAndEnable#3 pulse');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbCutoffAndEnable.cutoffActive,
                      Message := 'CutoffAndEnable#3 cutoffActive');

    // #4, t = 3000 мс — разрешено: 0.125 м3
    GVL_S7Clock.tSimNow := T#3000MS;
    fbCutoffAndEnable.enable := TRUE;
    fbCutoffAndEnable();
    AssertEquals_LREAL(Expected := 0.125,
                       Actual := fbCutoffAndEnable.total,
                       Delta := 0.000001,
                       Message := 'CutoffAndEnable#4 total');
    AssertEquals_LREAL(Expected := 0.125,
                       Actual := fbCutoffAndEnable.lifetimeTotal,
                       Delta := 0.000001,
                       Message := 'CutoffAndEnable#4 lifetimeTotal');
    AssertEquals_DINT(Expected := 0, Actual := fbCutoffAndEnable.pulseCount, Message := 'CutoffAndEnable#4 pulseCount');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCutoffAndEnable.pulse, Message := 'CutoffAndEnable#4 pulse');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbCutoffAndEnable.cutoffActive,
                      Message := 'CutoffAndEnable#4 cutoffActive');

    // #5, t = 4000 мс — 0.5 = отсечке — считается: +0.5/3600 м3
    GVL_S7Clock.tSimNow := T#4000MS;
    fbCutoffAndEnable.flow := 0.5;
    fbCutoffAndEnable();
    AssertEquals_LREAL(Expected := 0.125138889,
                       Actual := fbCutoffAndEnable.total,
                       Delta := 0.000001,
                       Message := 'CutoffAndEnable#5 total');
    AssertEquals_LREAL(Expected := 0.125138889,
                       Actual := fbCutoffAndEnable.lifetimeTotal,
                       Delta := 0.000001,
                       Message := 'CutoffAndEnable#5 lifetimeTotal');
    AssertEquals_DINT(Expected := 0, Actual := fbCutoffAndEnable.pulseCount, Message := 'CutoffAndEnable#5 pulseCount');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCutoffAndEnable.pulse, Message := 'CutoffAndEnable#5 pulse');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbCutoffAndEnable.cutoffActive,
                      Message := 'CutoffAndEnable#5 cutoffActive');

    // #6, t = 5000 мс — 0.49 < 0.5: не считается
    GVL_S7Clock.tSimNow := T#5000MS;
    fbCutoffAndEnable.flow := 0.49;
    fbCutoffAndEnable();
    AssertEquals_LREAL(Expected := 0.125138889,
                       Actual := fbCutoffAndEnable.total,
                       Delta := 0.000001,
                       Message := 'CutoffAndEnable#6 total');
    AssertEquals_LREAL(Expected := 0.125138889,
                       Actual := fbCutoffAndEnable.lifetimeTotal,
                       Delta := 0.000001,
                       Message := 'CutoffAndEnable#6 lifetimeTotal');
    AssertEquals_DINT(Expected := 0, Actual := fbCutoffAndEnable.pulseCount, Message := 'CutoffAndEnable#6 pulseCount');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCutoffAndEnable.pulse, Message := 'CutoffAndEnable#6 pulse');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbCutoffAndEnable.cutoffActive,
                      Message := 'CutoffAndEnable#6 cutoffActive');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
