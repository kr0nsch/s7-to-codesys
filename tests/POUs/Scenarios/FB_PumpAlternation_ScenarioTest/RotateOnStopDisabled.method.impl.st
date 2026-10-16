// AUTO-GENERATED — не редактировать: scenarios/FB_PumpAlternation.csv, сценарий RotateOnStopDisabled
coUnit.TEST('RotateOnStopDisabled');
IF NOT xRotateOnStopDisabledDone THEN
    xRotateOnStopDisabledDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;

    // #1, t = 0 мс — один насос: 1
    GVL_S7Clock.tSimNow := T#0MS;
    fbRotateOnStopDisabled.demand := 1;
    fbRotateOnStopDisabled.available1 := TRUE;
    fbRotateOnStopDisabled.available2 := TRUE;
    fbRotateOnStopDisabled.available3 := TRUE;
    fbRotateOnStopDisabled.alternate := FALSE;
    fbRotateOnStopDisabled.rotateOnStop := FALSE;
    fbRotateOnStopDisabled();
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbRotateOnStopDisabled.run1,
                      Message := 'RotateOnStopDisabled#1 run1');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbRotateOnStopDisabled.run2,
                      Message := 'RotateOnStopDisabled#1 run2');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbRotateOnStopDisabled.run3,
                      Message := 'RotateOnStopDisabled#1 run3');
    AssertEquals_INT(Expected := 1,
                     Actual := fbRotateOnStopDisabled.leadPump,
                     Message := 'RotateOnStopDisabled#1 leadPump');
    AssertEquals_INT(Expected := 1,
                     Actual := fbRotateOnStopDisabled.runningCount,
                     Message := 'RotateOnStopDisabled#1 runningCount');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbRotateOnStopDisabled.shortage,
                      Message := 'RotateOnStopDisabled#1 shortage');

    // #2, t = 100 мс — останов: ведущий остаётся 1
    GVL_S7Clock.tSimNow := T#100MS;
    fbRotateOnStopDisabled.demand := 0;
    fbRotateOnStopDisabled();
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbRotateOnStopDisabled.run1,
                      Message := 'RotateOnStopDisabled#2 run1');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbRotateOnStopDisabled.run2,
                      Message := 'RotateOnStopDisabled#2 run2');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbRotateOnStopDisabled.run3,
                      Message := 'RotateOnStopDisabled#2 run3');
    AssertEquals_INT(Expected := 1,
                     Actual := fbRotateOnStopDisabled.leadPump,
                     Message := 'RotateOnStopDisabled#2 leadPump');
    AssertEquals_INT(Expected := 0,
                     Actual := fbRotateOnStopDisabled.runningCount,
                     Message := 'RotateOnStopDisabled#2 runningCount');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbRotateOnStopDisabled.shortage,
                      Message := 'RotateOnStopDisabled#2 shortage');

    // #3, t = 200 мс — снова 1
    GVL_S7Clock.tSimNow := T#200MS;
    fbRotateOnStopDisabled.demand := 1;
    fbRotateOnStopDisabled();
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbRotateOnStopDisabled.run1,
                      Message := 'RotateOnStopDisabled#3 run1');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbRotateOnStopDisabled.run2,
                      Message := 'RotateOnStopDisabled#3 run2');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbRotateOnStopDisabled.run3,
                      Message := 'RotateOnStopDisabled#3 run3');
    AssertEquals_INT(Expected := 1,
                     Actual := fbRotateOnStopDisabled.leadPump,
                     Message := 'RotateOnStopDisabled#3 leadPump');
    AssertEquals_INT(Expected := 1,
                     Actual := fbRotateOnStopDisabled.runningCount,
                     Message := 'RotateOnStopDisabled#3 runningCount');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbRotateOnStopDisabled.shortage,
                      Message := 'RotateOnStopDisabled#3 shortage');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
