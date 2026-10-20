// AUTO-GENERATED — не редактировать: scenarios/lang/FB_Starter.csv, сценарий InterlockDropStops
coUnit.TEST('InterlockDropStops');
IF NOT xInterlockDropStopsDone THEN
    xInterlockDropStopsDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;

    // #1, t = 0 мс — Пуск, пуск №1
    GVL_S7Clock.tSimNow := T#0MS;
    fbInterlockDropStops.xStart := TRUE;
    fbInterlockDropStops.xStop := FALSE;
    fbInterlockDropStops.xInterlock := TRUE;
    fbInterlockDropStops.xFeedback := FALSE;
    fbInterlockDropStops.tFeedbackTime := T#2000MS;
    fbInterlockDropStops.xReset := FALSE;
    fbInterlockDropStops();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbInterlockDropStops.xRun, Message := 'InterlockDropStops#1 xRun');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbInterlockDropStops.xFault,
                      Message := 'InterlockDropStops#1 xFault');
    AssertEquals_INT(Expected := 1, Actual := fbInterlockDropStops.iStarts, Message := 'InterlockDropStops#1 iStarts');

    // #2, t = 100 мс — работает
    GVL_S7Clock.tSimNow := T#100MS;
    fbInterlockDropStops.xStart := FALSE;
    fbInterlockDropStops.xFeedback := TRUE;
    fbInterlockDropStops();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbInterlockDropStops.xRun, Message := 'InterlockDropStops#2 xRun');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbInterlockDropStops.xFault,
                      Message := 'InterlockDropStops#2 xFault');
    AssertEquals_INT(Expected := 1, Actual := fbInterlockDropStops.iStarts, Message := 'InterlockDropStops#2 iStarts');

    // #3, t = 500 мс — блокировка пропала: выключается
    GVL_S7Clock.tSimNow := T#500MS;
    fbInterlockDropStops.xInterlock := FALSE;
    fbInterlockDropStops();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbInterlockDropStops.xRun, Message := 'InterlockDropStops#3 xRun');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbInterlockDropStops.xFault,
                      Message := 'InterlockDropStops#3 xFault');
    AssertEquals_INT(Expected := 1, Actual := fbInterlockDropStops.iStarts, Message := 'InterlockDropStops#3 iStarts');

    // #4, t = 600 мс — блокировка вернулась: остаётся выключенным
    GVL_S7Clock.tSimNow := T#600MS;
    fbInterlockDropStops.xInterlock := TRUE;
    fbInterlockDropStops.xFeedback := FALSE;
    fbInterlockDropStops();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbInterlockDropStops.xRun, Message := 'InterlockDropStops#4 xRun');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbInterlockDropStops.xFault,
                      Message := 'InterlockDropStops#4 xFault');
    AssertEquals_INT(Expected := 1, Actual := fbInterlockDropStops.iStarts, Message := 'InterlockDropStops#4 iStarts');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
