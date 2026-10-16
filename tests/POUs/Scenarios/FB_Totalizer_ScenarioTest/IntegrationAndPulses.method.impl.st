// AUTO-GENERATED — не редактировать: scenarios/FB_Totalizer.csv, сценарий IntegrationAndPulses
coUnit.TEST('IntegrationAndPulses');
IF NOT xIntegrationAndPulsesDone THEN
    xIntegrationAndPulsesDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;

    // #1, t = 0 мс — 0.125 м3
    GVL_S7Clock.tSimNow := T#0MS;
    fbIntegrationAndPulses.flow := 450.0;
    fbIntegrationAndPulses.cycleTime := T#1000MS;
    fbIntegrationAndPulses.lowFlowCutoff := 0.5;
    fbIntegrationAndPulses.enable := TRUE;
    fbIntegrationAndPulses.reset := FALSE;
    fbIntegrationAndPulses.pulseVolume := 0.5;
    fbIntegrationAndPulses();
    AssertEquals_LREAL(Expected := 0.125,
                       Actual := fbIntegrationAndPulses.total,
                       Delta := 0.000001,
                       Message := 'IntegrationAndPulses#1 total');
    AssertEquals_LREAL(Expected := 0.125,
                       Actual := fbIntegrationAndPulses.lifetimeTotal,
                       Delta := 0.000001,
                       Message := 'IntegrationAndPulses#1 lifetimeTotal');
    AssertEquals_DINT(Expected := 0,
                      Actual := fbIntegrationAndPulses.pulseCount,
                      Message := 'IntegrationAndPulses#1 pulseCount');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbIntegrationAndPulses.pulse,
                      Message := 'IntegrationAndPulses#1 pulse');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbIntegrationAndPulses.cutoffActive,
                      Message := 'IntegrationAndPulses#1 cutoffActive');

    // #2, t = 1000 мс — 0.25 м3
    GVL_S7Clock.tSimNow := T#1000MS;
    fbIntegrationAndPulses();
    AssertEquals_LREAL(Expected := 0.25,
                       Actual := fbIntegrationAndPulses.total,
                       Delta := 0.000001,
                       Message := 'IntegrationAndPulses#2 total');
    AssertEquals_LREAL(Expected := 0.25,
                       Actual := fbIntegrationAndPulses.lifetimeTotal,
                       Delta := 0.000001,
                       Message := 'IntegrationAndPulses#2 lifetimeTotal');
    AssertEquals_DINT(Expected := 0,
                      Actual := fbIntegrationAndPulses.pulseCount,
                      Message := 'IntegrationAndPulses#2 pulseCount');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbIntegrationAndPulses.pulse,
                      Message := 'IntegrationAndPulses#2 pulse');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbIntegrationAndPulses.cutoffActive,
                      Message := 'IntegrationAndPulses#2 cutoffActive');

    // #3, t = 2000 мс — 0.375 м3
    GVL_S7Clock.tSimNow := T#2000MS;
    fbIntegrationAndPulses();
    AssertEquals_LREAL(Expected := 0.375,
                       Actual := fbIntegrationAndPulses.total,
                       Delta := 0.000001,
                       Message := 'IntegrationAndPulses#3 total');
    AssertEquals_LREAL(Expected := 0.375,
                       Actual := fbIntegrationAndPulses.lifetimeTotal,
                       Delta := 0.000001,
                       Message := 'IntegrationAndPulses#3 lifetimeTotal');
    AssertEquals_DINT(Expected := 0,
                      Actual := fbIntegrationAndPulses.pulseCount,
                      Message := 'IntegrationAndPulses#3 pulseCount');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbIntegrationAndPulses.pulse,
                      Message := 'IntegrationAndPulses#3 pulse');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbIntegrationAndPulses.cutoffActive,
                      Message := 'IntegrationAndPulses#3 cutoffActive');

    // #4, t = 3000 мс — 0.5 м3: импульс №1
    GVL_S7Clock.tSimNow := T#3000MS;
    fbIntegrationAndPulses();
    AssertEquals_LREAL(Expected := 0.5,
                       Actual := fbIntegrationAndPulses.total,
                       Delta := 0.000001,
                       Message := 'IntegrationAndPulses#4 total');
    AssertEquals_LREAL(Expected := 0.5,
                       Actual := fbIntegrationAndPulses.lifetimeTotal,
                       Delta := 0.000001,
                       Message := 'IntegrationAndPulses#4 lifetimeTotal');
    AssertEquals_DINT(Expected := 1,
                      Actual := fbIntegrationAndPulses.pulseCount,
                      Message := 'IntegrationAndPulses#4 pulseCount');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbIntegrationAndPulses.pulse,
                      Message := 'IntegrationAndPulses#4 pulse');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbIntegrationAndPulses.cutoffActive,
                      Message := 'IntegrationAndPulses#4 cutoffActive');

    // #5, t = 4000 мс — 0.625 м3, импульса нет
    GVL_S7Clock.tSimNow := T#4000MS;
    fbIntegrationAndPulses();
    AssertEquals_LREAL(Expected := 0.625,
                       Actual := fbIntegrationAndPulses.total,
                       Delta := 0.000001,
                       Message := 'IntegrationAndPulses#5 total');
    AssertEquals_LREAL(Expected := 0.625,
                       Actual := fbIntegrationAndPulses.lifetimeTotal,
                       Delta := 0.000001,
                       Message := 'IntegrationAndPulses#5 lifetimeTotal');
    AssertEquals_DINT(Expected := 1,
                      Actual := fbIntegrationAndPulses.pulseCount,
                      Message := 'IntegrationAndPulses#5 pulseCount');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbIntegrationAndPulses.pulse,
                      Message := 'IntegrationAndPulses#5 pulse');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbIntegrationAndPulses.cutoffActive,
                      Message := 'IntegrationAndPulses#5 cutoffActive');

    // #6, t = 5000 мс — 0.75 м3
    GVL_S7Clock.tSimNow := T#5000MS;
    fbIntegrationAndPulses();
    AssertEquals_LREAL(Expected := 0.75,
                       Actual := fbIntegrationAndPulses.total,
                       Delta := 0.000001,
                       Message := 'IntegrationAndPulses#6 total');
    AssertEquals_LREAL(Expected := 0.75,
                       Actual := fbIntegrationAndPulses.lifetimeTotal,
                       Delta := 0.000001,
                       Message := 'IntegrationAndPulses#6 lifetimeTotal');
    AssertEquals_DINT(Expected := 1,
                      Actual := fbIntegrationAndPulses.pulseCount,
                      Message := 'IntegrationAndPulses#6 pulseCount');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbIntegrationAndPulses.pulse,
                      Message := 'IntegrationAndPulses#6 pulse');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbIntegrationAndPulses.cutoffActive,
                      Message := 'IntegrationAndPulses#6 cutoffActive');

    // #7, t = 6000 мс — 0.875 м3
    GVL_S7Clock.tSimNow := T#6000MS;
    fbIntegrationAndPulses();
    AssertEquals_LREAL(Expected := 0.875,
                       Actual := fbIntegrationAndPulses.total,
                       Delta := 0.000001,
                       Message := 'IntegrationAndPulses#7 total');
    AssertEquals_LREAL(Expected := 0.875,
                       Actual := fbIntegrationAndPulses.lifetimeTotal,
                       Delta := 0.000001,
                       Message := 'IntegrationAndPulses#7 lifetimeTotal');
    AssertEquals_DINT(Expected := 1,
                      Actual := fbIntegrationAndPulses.pulseCount,
                      Message := 'IntegrationAndPulses#7 pulseCount');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbIntegrationAndPulses.pulse,
                      Message := 'IntegrationAndPulses#7 pulse');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbIntegrationAndPulses.cutoffActive,
                      Message := 'IntegrationAndPulses#7 cutoffActive');

    // #8, t = 7000 мс — 1.0 м3: импульс №2
    GVL_S7Clock.tSimNow := T#7000MS;
    fbIntegrationAndPulses();
    AssertEquals_LREAL(Expected := 1.0,
                       Actual := fbIntegrationAndPulses.total,
                       Delta := 0.000001,
                       Message := 'IntegrationAndPulses#8 total');
    AssertEquals_LREAL(Expected := 1.0,
                       Actual := fbIntegrationAndPulses.lifetimeTotal,
                       Delta := 0.000001,
                       Message := 'IntegrationAndPulses#8 lifetimeTotal');
    AssertEquals_DINT(Expected := 2,
                      Actual := fbIntegrationAndPulses.pulseCount,
                      Message := 'IntegrationAndPulses#8 pulseCount');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbIntegrationAndPulses.pulse,
                      Message := 'IntegrationAndPulses#8 pulse');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbIntegrationAndPulses.cutoffActive,
                      Message := 'IntegrationAndPulses#8 cutoffActive');

    // #9, t = 8000 мс — 900 м3/ч: +0.25 м3 = 1.25
    GVL_S7Clock.tSimNow := T#8000MS;
    fbIntegrationAndPulses.flow := 900.0;
    fbIntegrationAndPulses();
    AssertEquals_LREAL(Expected := 1.25,
                       Actual := fbIntegrationAndPulses.total,
                       Delta := 0.000001,
                       Message := 'IntegrationAndPulses#9 total');
    AssertEquals_LREAL(Expected := 1.25,
                       Actual := fbIntegrationAndPulses.lifetimeTotal,
                       Delta := 0.000001,
                       Message := 'IntegrationAndPulses#9 lifetimeTotal');
    AssertEquals_DINT(Expected := 2,
                      Actual := fbIntegrationAndPulses.pulseCount,
                      Message := 'IntegrationAndPulses#9 pulseCount');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbIntegrationAndPulses.pulse,
                      Message := 'IntegrationAndPulses#9 pulse');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbIntegrationAndPulses.cutoffActive,
                      Message := 'IntegrationAndPulses#9 cutoffActive');

    // #10, t = 9000 мс — 1.5 м3: импульс №3
    GVL_S7Clock.tSimNow := T#9000MS;
    fbIntegrationAndPulses();
    AssertEquals_LREAL(Expected := 1.5,
                       Actual := fbIntegrationAndPulses.total,
                       Delta := 0.000001,
                       Message := 'IntegrationAndPulses#10 total');
    AssertEquals_LREAL(Expected := 1.5,
                       Actual := fbIntegrationAndPulses.lifetimeTotal,
                       Delta := 0.000001,
                       Message := 'IntegrationAndPulses#10 lifetimeTotal');
    AssertEquals_DINT(Expected := 3,
                      Actual := fbIntegrationAndPulses.pulseCount,
                      Message := 'IntegrationAndPulses#10 pulseCount');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbIntegrationAndPulses.pulse,
                      Message := 'IntegrationAndPulses#10 pulse');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbIntegrationAndPulses.cutoffActive,
                      Message := 'IntegrationAndPulses#10 cutoffActive');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
