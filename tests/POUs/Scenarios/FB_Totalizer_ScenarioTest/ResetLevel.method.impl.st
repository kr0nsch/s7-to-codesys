// AUTO-GENERATED — не редактировать: scenarios/FB_Totalizer.csv, сценарий ResetLevel
coUnit.TEST('ResetLevel');
IF NOT xResetLevelDone THEN
    xResetLevelDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;

    // #1, t = 0 мс — 0.25 м3
    GVL_S7Clock.tSimNow := T#0MS;
    fbResetLevel.flow := 900.0;
    fbResetLevel.cycleTime := T#1000MS;
    fbResetLevel.lowFlowCutoff := 0.5;
    fbResetLevel.enable := TRUE;
    fbResetLevel.reset := FALSE;
    fbResetLevel.pulseVolume := 1.0;
    fbResetLevel();
    AssertEquals_LREAL(Expected := 0.25,
                       Actual := fbResetLevel.total,
                       Delta := 0.000001,
                       Message := 'ResetLevel#1 total');
    AssertEquals_LREAL(Expected := 0.25,
                       Actual := fbResetLevel.lifetimeTotal,
                       Delta := 0.000001,
                       Message := 'ResetLevel#1 lifetimeTotal');
    AssertEquals_DINT(Expected := 0, Actual := fbResetLevel.pulseCount, Message := 'ResetLevel#1 pulseCount');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbResetLevel.pulse, Message := 'ResetLevel#1 pulse');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbResetLevel.cutoffActive, Message := 'ResetLevel#1 cutoffActive');

    // #2, t = 1000 мс — 0.5 м3
    GVL_S7Clock.tSimNow := T#1000MS;
    fbResetLevel();
    AssertEquals_LREAL(Expected := 0.5,
                       Actual := fbResetLevel.total,
                       Delta := 0.000001,
                       Message := 'ResetLevel#2 total');
    AssertEquals_LREAL(Expected := 0.5,
                       Actual := fbResetLevel.lifetimeTotal,
                       Delta := 0.000001,
                       Message := 'ResetLevel#2 lifetimeTotal');
    AssertEquals_DINT(Expected := 0, Actual := fbResetLevel.pulseCount, Message := 'ResetLevel#2 pulseCount');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbResetLevel.pulse, Message := 'ResetLevel#2 pulse');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbResetLevel.cutoffActive, Message := 'ResetLevel#2 cutoffActive');

    // #3, t = 2000 мс — сброс: total 0, общий 0.75
    GVL_S7Clock.tSimNow := T#2000MS;
    fbResetLevel.reset := TRUE;
    fbResetLevel();
    AssertEquals_LREAL(Expected := 0.0,
                       Actual := fbResetLevel.total,
                       Delta := 0.000001,
                       Message := 'ResetLevel#3 total');
    AssertEquals_LREAL(Expected := 0.75,
                       Actual := fbResetLevel.lifetimeTotal,
                       Delta := 0.000001,
                       Message := 'ResetLevel#3 lifetimeTotal');
    AssertEquals_DINT(Expected := 0, Actual := fbResetLevel.pulseCount, Message := 'ResetLevel#3 pulseCount');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbResetLevel.pulse, Message := 'ResetLevel#3 pulse');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbResetLevel.cutoffActive, Message := 'ResetLevel#3 cutoffActive');

    // #4, t = 3000 мс — сброс держится: total 0, общий 1.0
    GVL_S7Clock.tSimNow := T#3000MS;
    fbResetLevel();
    AssertEquals_LREAL(Expected := 0.0,
                       Actual := fbResetLevel.total,
                       Delta := 0.000001,
                       Message := 'ResetLevel#4 total');
    AssertEquals_LREAL(Expected := 1.0,
                       Actual := fbResetLevel.lifetimeTotal,
                       Delta := 0.000001,
                       Message := 'ResetLevel#4 lifetimeTotal');
    AssertEquals_DINT(Expected := 0, Actual := fbResetLevel.pulseCount, Message := 'ResetLevel#4 pulseCount');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbResetLevel.pulse, Message := 'ResetLevel#4 pulse');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbResetLevel.cutoffActive, Message := 'ResetLevel#4 cutoffActive');

    // #5, t = 4000 мс — сброс снят: total 0.25, общий 1.25
    GVL_S7Clock.tSimNow := T#4000MS;
    fbResetLevel.reset := FALSE;
    fbResetLevel();
    AssertEquals_LREAL(Expected := 0.25,
                       Actual := fbResetLevel.total,
                       Delta := 0.000001,
                       Message := 'ResetLevel#5 total');
    AssertEquals_LREAL(Expected := 1.25,
                       Actual := fbResetLevel.lifetimeTotal,
                       Delta := 0.000001,
                       Message := 'ResetLevel#5 lifetimeTotal');
    AssertEquals_DINT(Expected := 0, Actual := fbResetLevel.pulseCount, Message := 'ResetLevel#5 pulseCount');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbResetLevel.pulse, Message := 'ResetLevel#5 pulse');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbResetLevel.cutoffActive, Message := 'ResetLevel#5 cutoffActive');

    // #6, t = 5000 мс — 0.5
    GVL_S7Clock.tSimNow := T#5000MS;
    fbResetLevel();
    AssertEquals_LREAL(Expected := 0.5,
                       Actual := fbResetLevel.total,
                       Delta := 0.000001,
                       Message := 'ResetLevel#6 total');
    AssertEquals_LREAL(Expected := 1.5,
                       Actual := fbResetLevel.lifetimeTotal,
                       Delta := 0.000001,
                       Message := 'ResetLevel#6 lifetimeTotal');
    AssertEquals_DINT(Expected := 0, Actual := fbResetLevel.pulseCount, Message := 'ResetLevel#6 pulseCount');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbResetLevel.pulse, Message := 'ResetLevel#6 pulse');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbResetLevel.cutoffActive, Message := 'ResetLevel#6 cutoffActive');

    // #7, t = 6000 мс — 0.75
    GVL_S7Clock.tSimNow := T#6000MS;
    fbResetLevel();
    AssertEquals_LREAL(Expected := 0.75,
                       Actual := fbResetLevel.total,
                       Delta := 0.000001,
                       Message := 'ResetLevel#7 total');
    AssertEquals_LREAL(Expected := 1.75,
                       Actual := fbResetLevel.lifetimeTotal,
                       Delta := 0.000001,
                       Message := 'ResetLevel#7 lifetimeTotal');
    AssertEquals_DINT(Expected := 0, Actual := fbResetLevel.pulseCount, Message := 'ResetLevel#7 pulseCount');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbResetLevel.pulse, Message := 'ResetLevel#7 pulse');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbResetLevel.cutoffActive, Message := 'ResetLevel#7 cutoffActive');

    // #8, t = 7000 мс — 1.0 м3 после сброса: импульс №1
    GVL_S7Clock.tSimNow := T#7000MS;
    fbResetLevel();
    AssertEquals_LREAL(Expected := 1.0,
                       Actual := fbResetLevel.total,
                       Delta := 0.000001,
                       Message := 'ResetLevel#8 total');
    AssertEquals_LREAL(Expected := 2.0,
                       Actual := fbResetLevel.lifetimeTotal,
                       Delta := 0.000001,
                       Message := 'ResetLevel#8 lifetimeTotal');
    AssertEquals_DINT(Expected := 1, Actual := fbResetLevel.pulseCount, Message := 'ResetLevel#8 pulseCount');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbResetLevel.pulse, Message := 'ResetLevel#8 pulse');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbResetLevel.cutoffActive, Message := 'ResetLevel#8 cutoffActive');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
