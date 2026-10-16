// AUTO-GENERATED — не редактировать: scenarios/FB_PumpAlternation.csv, сценарий NoPumpsAvailable
coUnit.TEST('NoPumpsAvailable');
IF NOT xNoPumpsAvailableDone THEN
    xNoPumpsAvailableDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;

    // #1, t = 0 мс — нужно 2, доступных нет: нехватка
    GVL_S7Clock.tSimNow := T#0MS;
    fbNoPumpsAvailable.demand := 2;
    fbNoPumpsAvailable.available1 := FALSE;
    fbNoPumpsAvailable.available2 := FALSE;
    fbNoPumpsAvailable.available3 := FALSE;
    fbNoPumpsAvailable.alternate := FALSE;
    fbNoPumpsAvailable.rotateOnStop := TRUE;
    fbNoPumpsAvailable();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbNoPumpsAvailable.run1, Message := 'NoPumpsAvailable#1 run1');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbNoPumpsAvailable.run2, Message := 'NoPumpsAvailable#1 run2');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbNoPumpsAvailable.run3, Message := 'NoPumpsAvailable#1 run3');
    AssertEquals_INT(Expected := 1, Actual := fbNoPumpsAvailable.leadPump, Message := 'NoPumpsAvailable#1 leadPump');
    AssertEquals_INT(Expected := 0,
                     Actual := fbNoPumpsAvailable.runningCount,
                     Message := 'NoPumpsAvailable#1 runningCount');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbNoPumpsAvailable.shortage,
                      Message := 'NoPumpsAvailable#1 shortage');

    // #2, t = 100 мс — останов: искать некого, ведущий 1
    GVL_S7Clock.tSimNow := T#100MS;
    fbNoPumpsAvailable.demand := 0;
    fbNoPumpsAvailable();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbNoPumpsAvailable.run1, Message := 'NoPumpsAvailable#2 run1');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbNoPumpsAvailable.run2, Message := 'NoPumpsAvailable#2 run2');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbNoPumpsAvailable.run3, Message := 'NoPumpsAvailable#2 run3');
    AssertEquals_INT(Expected := 1, Actual := fbNoPumpsAvailable.leadPump, Message := 'NoPumpsAvailable#2 leadPump');
    AssertEquals_INT(Expected := 0,
                     Actual := fbNoPumpsAvailable.runningCount,
                     Message := 'NoPumpsAvailable#2 runningCount');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbNoPumpsAvailable.shortage,
                      Message := 'NoPumpsAvailable#2 shortage');

    // #3, t = 200 мс — фронт alternate: искать некого, ведущий 1
    GVL_S7Clock.tSimNow := T#200MS;
    fbNoPumpsAvailable.alternate := TRUE;
    fbNoPumpsAvailable();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbNoPumpsAvailable.run1, Message := 'NoPumpsAvailable#3 run1');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbNoPumpsAvailable.run2, Message := 'NoPumpsAvailable#3 run2');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbNoPumpsAvailable.run3, Message := 'NoPumpsAvailable#3 run3');
    AssertEquals_INT(Expected := 1, Actual := fbNoPumpsAvailable.leadPump, Message := 'NoPumpsAvailable#3 leadPump');
    AssertEquals_INT(Expected := 0,
                     Actual := fbNoPumpsAvailable.runningCount,
                     Message := 'NoPumpsAvailable#3 runningCount');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbNoPumpsAvailable.shortage,
                      Message := 'NoPumpsAvailable#3 shortage');

    // #4, t = 300 мс — доступен только 3: работает 3, ведущий 1
    GVL_S7Clock.tSimNow := T#300MS;
    fbNoPumpsAvailable.demand := 1;
    fbNoPumpsAvailable.available3 := TRUE;
    fbNoPumpsAvailable.alternate := FALSE;
    fbNoPumpsAvailable();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbNoPumpsAvailable.run1, Message := 'NoPumpsAvailable#4 run1');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbNoPumpsAvailable.run2, Message := 'NoPumpsAvailable#4 run2');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbNoPumpsAvailable.run3, Message := 'NoPumpsAvailable#4 run3');
    AssertEquals_INT(Expected := 1, Actual := fbNoPumpsAvailable.leadPump, Message := 'NoPumpsAvailable#4 leadPump');
    AssertEquals_INT(Expected := 1,
                     Actual := fbNoPumpsAvailable.runningCount,
                     Message := 'NoPumpsAvailable#4 runningCount');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbNoPumpsAvailable.shortage,
                      Message := 'NoPumpsAvailable#4 shortage');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
