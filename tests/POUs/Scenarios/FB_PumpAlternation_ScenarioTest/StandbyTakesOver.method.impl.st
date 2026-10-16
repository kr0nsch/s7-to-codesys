// AUTO-GENERATED — не редактировать: scenarios/FB_PumpAlternation.csv, сценарий StandbyTakesOver
coUnit.TEST('StandbyTakesOver');
IF NOT xStandbyTakesOverDone THEN
    xStandbyTakesOverDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;

    // #1, t = 0 мс — один насос: 1
    GVL_S7Clock.tSimNow := T#0MS;
    fbStandbyTakesOver.demand := 1;
    fbStandbyTakesOver.available1 := TRUE;
    fbStandbyTakesOver.available2 := TRUE;
    fbStandbyTakesOver.available3 := TRUE;
    fbStandbyTakesOver.alternate := FALSE;
    fbStandbyTakesOver.rotateOnStop := TRUE;
    fbStandbyTakesOver();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbStandbyTakesOver.run1, Message := 'StandbyTakesOver#1 run1');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStandbyTakesOver.run2, Message := 'StandbyTakesOver#1 run2');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStandbyTakesOver.run3, Message := 'StandbyTakesOver#1 run3');
    AssertEquals_INT(Expected := 1, Actual := fbStandbyTakesOver.leadPump, Message := 'StandbyTakesOver#1 leadPump');
    AssertEquals_INT(Expected := 1,
                     Actual := fbStandbyTakesOver.runningCount,
                     Message := 'StandbyTakesOver#1 runningCount');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbStandbyTakesOver.shortage,
                      Message := 'StandbyTakesOver#1 shortage');

    // #2, t = 100 мс — насос 1 недоступен: работает 2, ведущий остаётся 1
    GVL_S7Clock.tSimNow := T#100MS;
    fbStandbyTakesOver.available1 := FALSE;
    fbStandbyTakesOver();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStandbyTakesOver.run1, Message := 'StandbyTakesOver#2 run1');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbStandbyTakesOver.run2, Message := 'StandbyTakesOver#2 run2');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStandbyTakesOver.run3, Message := 'StandbyTakesOver#2 run3');
    AssertEquals_INT(Expected := 1, Actual := fbStandbyTakesOver.leadPump, Message := 'StandbyTakesOver#2 leadPump');
    AssertEquals_INT(Expected := 1,
                     Actual := fbStandbyTakesOver.runningCount,
                     Message := 'StandbyTakesOver#2 runningCount');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbStandbyTakesOver.shortage,
                      Message := 'StandbyTakesOver#2 shortage');

    // #3, t = 200 мс — насос 1 вернулся: снова 1
    GVL_S7Clock.tSimNow := T#200MS;
    fbStandbyTakesOver.available1 := TRUE;
    fbStandbyTakesOver();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbStandbyTakesOver.run1, Message := 'StandbyTakesOver#3 run1');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStandbyTakesOver.run2, Message := 'StandbyTakesOver#3 run2');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStandbyTakesOver.run3, Message := 'StandbyTakesOver#3 run3');
    AssertEquals_INT(Expected := 1, Actual := fbStandbyTakesOver.leadPump, Message := 'StandbyTakesOver#3 leadPump');
    AssertEquals_INT(Expected := 1,
                     Actual := fbStandbyTakesOver.runningCount,
                     Message := 'StandbyTakesOver#3 runningCount');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbStandbyTakesOver.shortage,
                      Message := 'StandbyTakesOver#3 shortage');

    // #4, t = 300 мс — нужно 3, доступно 2: 1 и 3, нехватка
    GVL_S7Clock.tSimNow := T#300MS;
    fbStandbyTakesOver.demand := 3;
    fbStandbyTakesOver.available2 := FALSE;
    fbStandbyTakesOver();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbStandbyTakesOver.run1, Message := 'StandbyTakesOver#4 run1');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStandbyTakesOver.run2, Message := 'StandbyTakesOver#4 run2');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbStandbyTakesOver.run3, Message := 'StandbyTakesOver#4 run3');
    AssertEquals_INT(Expected := 1, Actual := fbStandbyTakesOver.leadPump, Message := 'StandbyTakesOver#4 leadPump');
    AssertEquals_INT(Expected := 2,
                     Actual := fbStandbyTakesOver.runningCount,
                     Message := 'StandbyTakesOver#4 runningCount');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbStandbyTakesOver.shortage,
                      Message := 'StandbyTakesOver#4 shortage');

    // #5, t = 400 мс — останов: после 1 недоступен 2 — ведущий 3
    GVL_S7Clock.tSimNow := T#400MS;
    fbStandbyTakesOver.demand := 0;
    fbStandbyTakesOver();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStandbyTakesOver.run1, Message := 'StandbyTakesOver#5 run1');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStandbyTakesOver.run2, Message := 'StandbyTakesOver#5 run2');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStandbyTakesOver.run3, Message := 'StandbyTakesOver#5 run3');
    AssertEquals_INT(Expected := 3, Actual := fbStandbyTakesOver.leadPump, Message := 'StandbyTakesOver#5 leadPump');
    AssertEquals_INT(Expected := 0,
                     Actual := fbStandbyTakesOver.runningCount,
                     Message := 'StandbyTakesOver#5 runningCount');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbStandbyTakesOver.shortage,
                      Message := 'StandbyTakesOver#5 shortage');

    // #6, t = 500 мс — один насос: 3
    GVL_S7Clock.tSimNow := T#500MS;
    fbStandbyTakesOver.demand := 1;
    fbStandbyTakesOver();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStandbyTakesOver.run1, Message := 'StandbyTakesOver#6 run1');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStandbyTakesOver.run2, Message := 'StandbyTakesOver#6 run2');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbStandbyTakesOver.run3, Message := 'StandbyTakesOver#6 run3');
    AssertEquals_INT(Expected := 3, Actual := fbStandbyTakesOver.leadPump, Message := 'StandbyTakesOver#6 leadPump');
    AssertEquals_INT(Expected := 1,
                     Actual := fbStandbyTakesOver.runningCount,
                     Message := 'StandbyTakesOver#6 runningCount');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbStandbyTakesOver.shortage,
                      Message := 'StandbyTakesOver#6 shortage');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
