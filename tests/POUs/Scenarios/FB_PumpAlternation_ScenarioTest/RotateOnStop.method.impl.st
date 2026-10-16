// AUTO-GENERATED — не редактировать: scenarios/FB_PumpAlternation.csv, сценарий RotateOnStop
coUnit.TEST('RotateOnStop');
IF NOT xRotateOnStopDone THEN
    xRotateOnStopDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;

    // #1, t = 0 мс — первый вызов при demand = 0: спада нет, ведущий 1
    GVL_S7Clock.tSimNow := T#0MS;
    fbRotateOnStop.demand := 0;
    fbRotateOnStop.available1 := TRUE;
    fbRotateOnStop.available2 := TRUE;
    fbRotateOnStop.available3 := TRUE;
    fbRotateOnStop.alternate := FALSE;
    fbRotateOnStop.rotateOnStop := TRUE;
    fbRotateOnStop();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbRotateOnStop.run1, Message := 'RotateOnStop#1 run1');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbRotateOnStop.run2, Message := 'RotateOnStop#1 run2');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbRotateOnStop.run3, Message := 'RotateOnStop#1 run3');
    AssertEquals_INT(Expected := 1, Actual := fbRotateOnStop.leadPump, Message := 'RotateOnStop#1 leadPump');
    AssertEquals_INT(Expected := 0, Actual := fbRotateOnStop.runningCount, Message := 'RotateOnStop#1 runningCount');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbRotateOnStop.shortage, Message := 'RotateOnStop#1 shortage');

    // #2, t = 100 мс — один насос: ведущий 1
    GVL_S7Clock.tSimNow := T#100MS;
    fbRotateOnStop.demand := 1;
    fbRotateOnStop();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbRotateOnStop.run1, Message := 'RotateOnStop#2 run1');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbRotateOnStop.run2, Message := 'RotateOnStop#2 run2');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbRotateOnStop.run3, Message := 'RotateOnStop#2 run3');
    AssertEquals_INT(Expected := 1, Actual := fbRotateOnStop.leadPump, Message := 'RotateOnStop#2 leadPump');
    AssertEquals_INT(Expected := 1, Actual := fbRotateOnStop.runningCount, Message := 'RotateOnStop#2 runningCount');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbRotateOnStop.shortage, Message := 'RotateOnStop#2 shortage');

    // #3, t = 200 мс — два насоса: 1 и 2
    GVL_S7Clock.tSimNow := T#200MS;
    fbRotateOnStop.demand := 2;
    fbRotateOnStop();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbRotateOnStop.run1, Message := 'RotateOnStop#3 run1');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbRotateOnStop.run2, Message := 'RotateOnStop#3 run2');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbRotateOnStop.run3, Message := 'RotateOnStop#3 run3');
    AssertEquals_INT(Expected := 1, Actual := fbRotateOnStop.leadPump, Message := 'RotateOnStop#3 leadPump');
    AssertEquals_INT(Expected := 2, Actual := fbRotateOnStop.runningCount, Message := 'RotateOnStop#3 runningCount');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbRotateOnStop.shortage, Message := 'RotateOnStop#3 shortage');

    // #4, t = 300 мс — останов группы: ведущий -> 2
    GVL_S7Clock.tSimNow := T#300MS;
    fbRotateOnStop.demand := 0;
    fbRotateOnStop();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbRotateOnStop.run1, Message := 'RotateOnStop#4 run1');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbRotateOnStop.run2, Message := 'RotateOnStop#4 run2');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbRotateOnStop.run3, Message := 'RotateOnStop#4 run3');
    AssertEquals_INT(Expected := 2, Actual := fbRotateOnStop.leadPump, Message := 'RotateOnStop#4 leadPump');
    AssertEquals_INT(Expected := 0, Actual := fbRotateOnStop.runningCount, Message := 'RotateOnStop#4 runningCount');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbRotateOnStop.shortage, Message := 'RotateOnStop#4 shortage');

    // #5, t = 400 мс — один насос: 2
    GVL_S7Clock.tSimNow := T#400MS;
    fbRotateOnStop.demand := 1;
    fbRotateOnStop();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbRotateOnStop.run1, Message := 'RotateOnStop#5 run1');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbRotateOnStop.run2, Message := 'RotateOnStop#5 run2');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbRotateOnStop.run3, Message := 'RotateOnStop#5 run3');
    AssertEquals_INT(Expected := 2, Actual := fbRotateOnStop.leadPump, Message := 'RotateOnStop#5 leadPump');
    AssertEquals_INT(Expected := 1, Actual := fbRotateOnStop.runningCount, Message := 'RotateOnStop#5 runningCount');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbRotateOnStop.shortage, Message := 'RotateOnStop#5 shortage');

    // #6, t = 500 мс — три насоса: 2, 3, 1
    GVL_S7Clock.tSimNow := T#500MS;
    fbRotateOnStop.demand := 3;
    fbRotateOnStop();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbRotateOnStop.run1, Message := 'RotateOnStop#6 run1');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbRotateOnStop.run2, Message := 'RotateOnStop#6 run2');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbRotateOnStop.run3, Message := 'RotateOnStop#6 run3');
    AssertEquals_INT(Expected := 2, Actual := fbRotateOnStop.leadPump, Message := 'RotateOnStop#6 leadPump');
    AssertEquals_INT(Expected := 3, Actual := fbRotateOnStop.runningCount, Message := 'RotateOnStop#6 runningCount');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbRotateOnStop.shortage, Message := 'RotateOnStop#6 shortage');

    // #7, t = 600 мс — останов: ведущий -> 3
    GVL_S7Clock.tSimNow := T#600MS;
    fbRotateOnStop.demand := 0;
    fbRotateOnStop();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbRotateOnStop.run1, Message := 'RotateOnStop#7 run1');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbRotateOnStop.run2, Message := 'RotateOnStop#7 run2');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbRotateOnStop.run3, Message := 'RotateOnStop#7 run3');
    AssertEquals_INT(Expected := 3, Actual := fbRotateOnStop.leadPump, Message := 'RotateOnStop#7 leadPump');
    AssertEquals_INT(Expected := 0, Actual := fbRotateOnStop.runningCount, Message := 'RotateOnStop#7 runningCount');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbRotateOnStop.shortage, Message := 'RotateOnStop#7 shortage');

    // #8, t = 700 мс — один насос: 3
    GVL_S7Clock.tSimNow := T#700MS;
    fbRotateOnStop.demand := 1;
    fbRotateOnStop();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbRotateOnStop.run1, Message := 'RotateOnStop#8 run1');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbRotateOnStop.run2, Message := 'RotateOnStop#8 run2');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbRotateOnStop.run3, Message := 'RotateOnStop#8 run3');
    AssertEquals_INT(Expected := 3, Actual := fbRotateOnStop.leadPump, Message := 'RotateOnStop#8 leadPump');
    AssertEquals_INT(Expected := 1, Actual := fbRotateOnStop.runningCount, Message := 'RotateOnStop#8 runningCount');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbRotateOnStop.shortage, Message := 'RotateOnStop#8 shortage');

    // #9, t = 800 мс — останов: ведущий -> 1 (по кругу)
    GVL_S7Clock.tSimNow := T#800MS;
    fbRotateOnStop.demand := 0;
    fbRotateOnStop();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbRotateOnStop.run1, Message := 'RotateOnStop#9 run1');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbRotateOnStop.run2, Message := 'RotateOnStop#9 run2');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbRotateOnStop.run3, Message := 'RotateOnStop#9 run3');
    AssertEquals_INT(Expected := 1, Actual := fbRotateOnStop.leadPump, Message := 'RotateOnStop#9 leadPump');
    AssertEquals_INT(Expected := 0, Actual := fbRotateOnStop.runningCount, Message := 'RotateOnStop#9 runningCount');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbRotateOnStop.shortage, Message := 'RotateOnStop#9 shortage');

    // #10, t = 900 мс — demand остаётся 0: спада нет, ведущий 1
    GVL_S7Clock.tSimNow := T#900MS;
    fbRotateOnStop();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbRotateOnStop.run1, Message := 'RotateOnStop#10 run1');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbRotateOnStop.run2, Message := 'RotateOnStop#10 run2');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbRotateOnStop.run3, Message := 'RotateOnStop#10 run3');
    AssertEquals_INT(Expected := 1, Actual := fbRotateOnStop.leadPump, Message := 'RotateOnStop#10 leadPump');
    AssertEquals_INT(Expected := 0, Actual := fbRotateOnStop.runningCount, Message := 'RotateOnStop#10 runningCount');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbRotateOnStop.shortage, Message := 'RotateOnStop#10 shortage');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
