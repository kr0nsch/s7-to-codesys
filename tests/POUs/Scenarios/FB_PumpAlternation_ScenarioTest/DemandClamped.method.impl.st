// AUTO-GENERATED — не редактировать: scenarios/FB_PumpAlternation.csv, сценарий DemandClamped
coUnit.TEST('DemandClamped');
IF NOT xDemandClampedDone THEN
    xDemandClampedDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;

    // #1, t = 0 мс — demand 5 -> 3: все три
    GVL_S7Clock.tSimNow := T#0MS;
    fbDemandClamped.demand := 5;
    fbDemandClamped.available1 := TRUE;
    fbDemandClamped.available2 := TRUE;
    fbDemandClamped.available3 := TRUE;
    fbDemandClamped.alternate := FALSE;
    fbDemandClamped.rotateOnStop := TRUE;
    fbDemandClamped();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbDemandClamped.run1, Message := 'DemandClamped#1 run1');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbDemandClamped.run2, Message := 'DemandClamped#1 run2');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbDemandClamped.run3, Message := 'DemandClamped#1 run3');
    AssertEquals_INT(Expected := 1, Actual := fbDemandClamped.leadPump, Message := 'DemandClamped#1 leadPump');
    AssertEquals_INT(Expected := 3, Actual := fbDemandClamped.runningCount, Message := 'DemandClamped#1 runningCount');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDemandClamped.shortage, Message := 'DemandClamped#1 shortage');

    // #2, t = 100 мс — demand -1 -> 0: останов, ведущий -> 2
    GVL_S7Clock.tSimNow := T#100MS;
    fbDemandClamped.demand := -1;
    fbDemandClamped();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDemandClamped.run1, Message := 'DemandClamped#2 run1');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDemandClamped.run2, Message := 'DemandClamped#2 run2');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDemandClamped.run3, Message := 'DemandClamped#2 run3');
    AssertEquals_INT(Expected := 2, Actual := fbDemandClamped.leadPump, Message := 'DemandClamped#2 leadPump');
    AssertEquals_INT(Expected := 0, Actual := fbDemandClamped.runningCount, Message := 'DemandClamped#2 runningCount');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDemandClamped.shortage, Message := 'DemandClamped#2 shortage');

    // #3, t = 200 мс — demand 4 -> 3: 2, 3, 1
    GVL_S7Clock.tSimNow := T#200MS;
    fbDemandClamped.demand := 4;
    fbDemandClamped();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbDemandClamped.run1, Message := 'DemandClamped#3 run1');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbDemandClamped.run2, Message := 'DemandClamped#3 run2');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbDemandClamped.run3, Message := 'DemandClamped#3 run3');
    AssertEquals_INT(Expected := 2, Actual := fbDemandClamped.leadPump, Message := 'DemandClamped#3 leadPump');
    AssertEquals_INT(Expected := 3, Actual := fbDemandClamped.runningCount, Message := 'DemandClamped#3 runningCount');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDemandClamped.shortage, Message := 'DemandClamped#3 shortage');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
