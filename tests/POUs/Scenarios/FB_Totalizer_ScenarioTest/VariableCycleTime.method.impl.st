// AUTO-GENERATED — не редактировать: scenarios/FB_Totalizer.csv, сценарий VariableCycleTime
coUnit.TEST('VariableCycleTime');
IF NOT xVariableCycleTimeDone THEN
    xVariableCycleTimeDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;

    // #1, t = 0 мс — 0.5 с: 0.0625 м3
    GVL_S7Clock.tSimNow := T#0MS;
    fbVariableCycleTime.flow := 450.0;
    fbVariableCycleTime.cycleTime := T#500MS;
    fbVariableCycleTime.lowFlowCutoff := 0.5;
    fbVariableCycleTime.enable := TRUE;
    fbVariableCycleTime.reset := FALSE;
    fbVariableCycleTime.pulseVolume := 0.5;
    fbVariableCycleTime();
    AssertEquals_LREAL(Expected := 0.0625,
                       Actual := fbVariableCycleTime.total,
                       Delta := 0.000001,
                       Message := 'VariableCycleTime#1 total');
    AssertEquals_LREAL(Expected := 0.0625,
                       Actual := fbVariableCycleTime.lifetimeTotal,
                       Delta := 0.000001,
                       Message := 'VariableCycleTime#1 lifetimeTotal');
    AssertEquals_DINT(Expected := 0,
                      Actual := fbVariableCycleTime.pulseCount,
                      Message := 'VariableCycleTime#1 pulseCount');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbVariableCycleTime.pulse, Message := 'VariableCycleTime#1 pulse');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbVariableCycleTime.cutoffActive,
                      Message := 'VariableCycleTime#1 cutoffActive');

    // #2, t = 500 мс — 0.125 м3
    GVL_S7Clock.tSimNow := T#500MS;
    fbVariableCycleTime();
    AssertEquals_LREAL(Expected := 0.125,
                       Actual := fbVariableCycleTime.total,
                       Delta := 0.000001,
                       Message := 'VariableCycleTime#2 total');
    AssertEquals_LREAL(Expected := 0.125,
                       Actual := fbVariableCycleTime.lifetimeTotal,
                       Delta := 0.000001,
                       Message := 'VariableCycleTime#2 lifetimeTotal');
    AssertEquals_DINT(Expected := 0,
                      Actual := fbVariableCycleTime.pulseCount,
                      Message := 'VariableCycleTime#2 pulseCount');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbVariableCycleTime.pulse, Message := 'VariableCycleTime#2 pulse');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbVariableCycleTime.cutoffActive,
                      Message := 'VariableCycleTime#2 cutoffActive');

    // #3, t = 2500 мс — 2 с: +0.25 = 0.375 м3
    GVL_S7Clock.tSimNow := T#2500MS;
    fbVariableCycleTime.cycleTime := T#2000MS;
    fbVariableCycleTime();
    AssertEquals_LREAL(Expected := 0.375,
                       Actual := fbVariableCycleTime.total,
                       Delta := 0.000001,
                       Message := 'VariableCycleTime#3 total');
    AssertEquals_LREAL(Expected := 0.375,
                       Actual := fbVariableCycleTime.lifetimeTotal,
                       Delta := 0.000001,
                       Message := 'VariableCycleTime#3 lifetimeTotal');
    AssertEquals_DINT(Expected := 0,
                      Actual := fbVariableCycleTime.pulseCount,
                      Message := 'VariableCycleTime#3 pulseCount');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbVariableCycleTime.pulse, Message := 'VariableCycleTime#3 pulse');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbVariableCycleTime.cutoffActive,
                      Message := 'VariableCycleTime#3 cutoffActive');

    // #4, t = 2600 мс — 0.1 с: +0.0125 = 0.3875 м3
    GVL_S7Clock.tSimNow := T#2600MS;
    fbVariableCycleTime.cycleTime := T#100MS;
    fbVariableCycleTime();
    AssertEquals_LREAL(Expected := 0.3875,
                       Actual := fbVariableCycleTime.total,
                       Delta := 0.000001,
                       Message := 'VariableCycleTime#4 total');
    AssertEquals_LREAL(Expected := 0.3875,
                       Actual := fbVariableCycleTime.lifetimeTotal,
                       Delta := 0.000001,
                       Message := 'VariableCycleTime#4 lifetimeTotal');
    AssertEquals_DINT(Expected := 0,
                      Actual := fbVariableCycleTime.pulseCount,
                      Message := 'VariableCycleTime#4 pulseCount');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbVariableCycleTime.pulse, Message := 'VariableCycleTime#4 pulse');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbVariableCycleTime.cutoffActive,
                      Message := 'VariableCycleTime#4 cutoffActive');

    // #5, t = 2700 мс — 0.4 м3, до импульса 0.1 м3
    GVL_S7Clock.tSimNow := T#2700MS;
    fbVariableCycleTime();
    AssertEquals_LREAL(Expected := 0.4,
                       Actual := fbVariableCycleTime.total,
                       Delta := 0.000001,
                       Message := 'VariableCycleTime#5 total');
    AssertEquals_LREAL(Expected := 0.4,
                       Actual := fbVariableCycleTime.lifetimeTotal,
                       Delta := 0.000001,
                       Message := 'VariableCycleTime#5 lifetimeTotal');
    AssertEquals_DINT(Expected := 0,
                      Actual := fbVariableCycleTime.pulseCount,
                      Message := 'VariableCycleTime#5 pulseCount');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbVariableCycleTime.pulse, Message := 'VariableCycleTime#5 pulse');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbVariableCycleTime.cutoffActive,
                      Message := 'VariableCycleTime#5 cutoffActive');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
