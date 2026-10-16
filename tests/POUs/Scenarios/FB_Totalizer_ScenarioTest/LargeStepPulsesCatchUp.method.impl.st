// AUTO-GENERATED — не редактировать: scenarios/FB_Totalizer.csv, сценарий LargeStepPulsesCatchUp
coUnit.TEST('LargeStepPulsesCatchUp');
IF NOT xLargeStepPulsesCatchUpDone THEN
    xLargeStepPulsesCatchUpDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;

    // #1, t = 0 мс — +1.0 м3 за вызов: импульс №1, остаток 0.5
    GVL_S7Clock.tSimNow := T#0MS;
    fbLargeStepPulsesCatchUp.flow := 3600.0;
    fbLargeStepPulsesCatchUp.cycleTime := T#1000MS;
    fbLargeStepPulsesCatchUp.lowFlowCutoff := 0.5;
    fbLargeStepPulsesCatchUp.enable := TRUE;
    fbLargeStepPulsesCatchUp.reset := FALSE;
    fbLargeStepPulsesCatchUp.pulseVolume := 0.5;
    fbLargeStepPulsesCatchUp();
    AssertEquals_LREAL(Expected := 1.0,
                       Actual := fbLargeStepPulsesCatchUp.total,
                       Delta := 0.000001,
                       Message := 'LargeStepPulsesCatchUp#1 total');
    AssertEquals_LREAL(Expected := 1.0,
                       Actual := fbLargeStepPulsesCatchUp.lifetimeTotal,
                       Delta := 0.000001,
                       Message := 'LargeStepPulsesCatchUp#1 lifetimeTotal');
    AssertEquals_DINT(Expected := 1,
                      Actual := fbLargeStepPulsesCatchUp.pulseCount,
                      Message := 'LargeStepPulsesCatchUp#1 pulseCount');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbLargeStepPulsesCatchUp.pulse,
                      Message := 'LargeStepPulsesCatchUp#1 pulse');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbLargeStepPulsesCatchUp.cutoffActive,
                      Message := 'LargeStepPulsesCatchUp#1 cutoffActive');

    // #2, t = 1000 мс — 2.0 м3: импульс №2, остаток 1.0
    GVL_S7Clock.tSimNow := T#1000MS;
    fbLargeStepPulsesCatchUp();
    AssertEquals_LREAL(Expected := 2.0,
                       Actual := fbLargeStepPulsesCatchUp.total,
                       Delta := 0.000001,
                       Message := 'LargeStepPulsesCatchUp#2 total');
    AssertEquals_LREAL(Expected := 2.0,
                       Actual := fbLargeStepPulsesCatchUp.lifetimeTotal,
                       Delta := 0.000001,
                       Message := 'LargeStepPulsesCatchUp#2 lifetimeTotal');
    AssertEquals_DINT(Expected := 2,
                      Actual := fbLargeStepPulsesCatchUp.pulseCount,
                      Message := 'LargeStepPulsesCatchUp#2 pulseCount');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbLargeStepPulsesCatchUp.pulse,
                      Message := 'LargeStepPulsesCatchUp#2 pulse');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbLargeStepPulsesCatchUp.cutoffActive,
                      Message := 'LargeStepPulsesCatchUp#2 cutoffActive');

    // #3, t = 2000 мс — расход 0: импульс №3 из остатка, остаток 0.5
    GVL_S7Clock.tSimNow := T#2000MS;
    fbLargeStepPulsesCatchUp.flow := 0.0;
    fbLargeStepPulsesCatchUp();
    AssertEquals_LREAL(Expected := 2.0,
                       Actual := fbLargeStepPulsesCatchUp.total,
                       Delta := 0.000001,
                       Message := 'LargeStepPulsesCatchUp#3 total');
    AssertEquals_LREAL(Expected := 2.0,
                       Actual := fbLargeStepPulsesCatchUp.lifetimeTotal,
                       Delta := 0.000001,
                       Message := 'LargeStepPulsesCatchUp#3 lifetimeTotal');
    AssertEquals_DINT(Expected := 3,
                      Actual := fbLargeStepPulsesCatchUp.pulseCount,
                      Message := 'LargeStepPulsesCatchUp#3 pulseCount');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbLargeStepPulsesCatchUp.pulse,
                      Message := 'LargeStepPulsesCatchUp#3 pulse');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbLargeStepPulsesCatchUp.cutoffActive,
                      Message := 'LargeStepPulsesCatchUp#3 cutoffActive');

    // #4, t = 3000 мс — импульс №4, остаток 0
    GVL_S7Clock.tSimNow := T#3000MS;
    fbLargeStepPulsesCatchUp();
    AssertEquals_LREAL(Expected := 2.0,
                       Actual := fbLargeStepPulsesCatchUp.total,
                       Delta := 0.000001,
                       Message := 'LargeStepPulsesCatchUp#4 total');
    AssertEquals_LREAL(Expected := 2.0,
                       Actual := fbLargeStepPulsesCatchUp.lifetimeTotal,
                       Delta := 0.000001,
                       Message := 'LargeStepPulsesCatchUp#4 lifetimeTotal');
    AssertEquals_DINT(Expected := 4,
                      Actual := fbLargeStepPulsesCatchUp.pulseCount,
                      Message := 'LargeStepPulsesCatchUp#4 pulseCount');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbLargeStepPulsesCatchUp.pulse,
                      Message := 'LargeStepPulsesCatchUp#4 pulse');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbLargeStepPulsesCatchUp.cutoffActive,
                      Message := 'LargeStepPulsesCatchUp#4 cutoffActive');

    // #5, t = 4000 мс — импульсов нет: 4 x 0.5 = 2.0 м3
    GVL_S7Clock.tSimNow := T#4000MS;
    fbLargeStepPulsesCatchUp();
    AssertEquals_LREAL(Expected := 2.0,
                       Actual := fbLargeStepPulsesCatchUp.total,
                       Delta := 0.000001,
                       Message := 'LargeStepPulsesCatchUp#5 total');
    AssertEquals_LREAL(Expected := 2.0,
                       Actual := fbLargeStepPulsesCatchUp.lifetimeTotal,
                       Delta := 0.000001,
                       Message := 'LargeStepPulsesCatchUp#5 lifetimeTotal');
    AssertEquals_DINT(Expected := 4,
                      Actual := fbLargeStepPulsesCatchUp.pulseCount,
                      Message := 'LargeStepPulsesCatchUp#5 pulseCount');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbLargeStepPulsesCatchUp.pulse,
                      Message := 'LargeStepPulsesCatchUp#5 pulse');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbLargeStepPulsesCatchUp.cutoffActive,
                      Message := 'LargeStepPulsesCatchUp#5 cutoffActive');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
