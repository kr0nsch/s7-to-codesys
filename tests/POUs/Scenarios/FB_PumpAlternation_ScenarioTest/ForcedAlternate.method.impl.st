// AUTO-GENERATED — не редактировать: scenarios/FB_PumpAlternation.csv, сценарий ForcedAlternate
coUnit.TEST('ForcedAlternate');
IF NOT xForcedAlternateDone THEN
    xForcedAlternateDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;

    // #1, t = 0 мс — один насос: 1
    GVL_S7Clock.tSimNow := T#0MS;
    fbForcedAlternate.demand := 1;
    fbForcedAlternate.available1 := TRUE;
    fbForcedAlternate.available2 := TRUE;
    fbForcedAlternate.available3 := TRUE;
    fbForcedAlternate.alternate := FALSE;
    fbForcedAlternate.rotateOnStop := TRUE;
    fbForcedAlternate();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbForcedAlternate.run1, Message := 'ForcedAlternate#1 run1');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbForcedAlternate.run2, Message := 'ForcedAlternate#1 run2');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbForcedAlternate.run3, Message := 'ForcedAlternate#1 run3');
    AssertEquals_INT(Expected := 1, Actual := fbForcedAlternate.leadPump, Message := 'ForcedAlternate#1 leadPump');
    AssertEquals_INT(Expected := 1,
                     Actual := fbForcedAlternate.runningCount,
                     Message := 'ForcedAlternate#1 runningCount');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbForcedAlternate.shortage, Message := 'ForcedAlternate#1 shortage');

    // #2, t = 100 мс — фронт alternate: ведущий 2, переключение в работе
    GVL_S7Clock.tSimNow := T#100MS;
    fbForcedAlternate.alternate := TRUE;
    fbForcedAlternate();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbForcedAlternate.run1, Message := 'ForcedAlternate#2 run1');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbForcedAlternate.run2, Message := 'ForcedAlternate#2 run2');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbForcedAlternate.run3, Message := 'ForcedAlternate#2 run3');
    AssertEquals_INT(Expected := 2, Actual := fbForcedAlternate.leadPump, Message := 'ForcedAlternate#2 leadPump');
    AssertEquals_INT(Expected := 1,
                     Actual := fbForcedAlternate.runningCount,
                     Message := 'ForcedAlternate#2 runningCount');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbForcedAlternate.shortage, Message := 'ForcedAlternate#2 shortage');

    // #3, t = 200 мс — alternate держится: фронта нет
    GVL_S7Clock.tSimNow := T#200MS;
    fbForcedAlternate();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbForcedAlternate.run1, Message := 'ForcedAlternate#3 run1');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbForcedAlternate.run2, Message := 'ForcedAlternate#3 run2');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbForcedAlternate.run3, Message := 'ForcedAlternate#3 run3');
    AssertEquals_INT(Expected := 2, Actual := fbForcedAlternate.leadPump, Message := 'ForcedAlternate#3 leadPump');
    AssertEquals_INT(Expected := 1,
                     Actual := fbForcedAlternate.runningCount,
                     Message := 'ForcedAlternate#3 runningCount');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbForcedAlternate.shortage, Message := 'ForcedAlternate#3 shortage');

    // #4, t = 300 мс — отпущен
    GVL_S7Clock.tSimNow := T#300MS;
    fbForcedAlternate.alternate := FALSE;
    fbForcedAlternate();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbForcedAlternate.run1, Message := 'ForcedAlternate#4 run1');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbForcedAlternate.run2, Message := 'ForcedAlternate#4 run2');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbForcedAlternate.run3, Message := 'ForcedAlternate#4 run3');
    AssertEquals_INT(Expected := 2, Actual := fbForcedAlternate.leadPump, Message := 'ForcedAlternate#4 leadPump');
    AssertEquals_INT(Expected := 1,
                     Actual := fbForcedAlternate.runningCount,
                     Message := 'ForcedAlternate#4 runningCount');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbForcedAlternate.shortage, Message := 'ForcedAlternate#4 shortage');

    // #5, t = 400 мс — фронт: ведущий 3
    GVL_S7Clock.tSimNow := T#400MS;
    fbForcedAlternate.alternate := TRUE;
    fbForcedAlternate();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbForcedAlternate.run1, Message := 'ForcedAlternate#5 run1');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbForcedAlternate.run2, Message := 'ForcedAlternate#5 run2');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbForcedAlternate.run3, Message := 'ForcedAlternate#5 run3');
    AssertEquals_INT(Expected := 3, Actual := fbForcedAlternate.leadPump, Message := 'ForcedAlternate#5 leadPump');
    AssertEquals_INT(Expected := 1,
                     Actual := fbForcedAlternate.runningCount,
                     Message := 'ForcedAlternate#5 runningCount');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbForcedAlternate.shortage, Message := 'ForcedAlternate#5 shortage');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
