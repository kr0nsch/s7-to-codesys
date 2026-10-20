// AUTO-GENERATED — не редактировать: scenarios/lang/FB_Starter.csv, сценарий FaultResetAndBlock
coUnit.TEST('FaultResetAndBlock');
IF NOT xFaultResetAndBlockDone THEN
    xFaultResetAndBlockDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;

    // #1, t = 0 мс — Пуск без обратной связи, пуск №1
    GVL_S7Clock.tSimNow := T#0MS;
    fbFaultResetAndBlock.xStart := TRUE;
    fbFaultResetAndBlock.xStop := FALSE;
    fbFaultResetAndBlock.xInterlock := TRUE;
    fbFaultResetAndBlock.xFeedback := FALSE;
    fbFaultResetAndBlock.tFeedbackTime := T#2000MS;
    fbFaultResetAndBlock.xReset := FALSE;
    fbFaultResetAndBlock();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbFaultResetAndBlock.xRun, Message := 'FaultResetAndBlock#1 xRun');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbFaultResetAndBlock.xFault,
                      Message := 'FaultResetAndBlock#1 xFault');
    AssertEquals_INT(Expected := 1, Actual := fbFaultResetAndBlock.iStarts, Message := 'FaultResetAndBlock#1 iStarts');

    // #2, t = 100 мс — ждём
    GVL_S7Clock.tSimNow := T#100MS;
    fbFaultResetAndBlock.xStart := FALSE;
    fbFaultResetAndBlock();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbFaultResetAndBlock.xRun, Message := 'FaultResetAndBlock#2 xRun');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbFaultResetAndBlock.xFault,
                      Message := 'FaultResetAndBlock#2 xFault');
    AssertEquals_INT(Expected := 1, Actual := fbFaultResetAndBlock.iStarts, Message := 'FaultResetAndBlock#2 iStarts');

    // #3, t = 2400 мс — 2.4 с: авария
    GVL_S7Clock.tSimNow := T#2400MS;
    fbFaultResetAndBlock();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbFaultResetAndBlock.xRun, Message := 'FaultResetAndBlock#3 xRun');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbFaultResetAndBlock.xFault,
                      Message := 'FaultResetAndBlock#3 xFault');
    AssertEquals_INT(Expected := 1, Actual := fbFaultResetAndBlock.iStarts, Message := 'FaultResetAndBlock#3 iStarts');

    // #4, t = 2600 мс — Пуск при аварии: R1 = 1 главнее — не включается
    GVL_S7Clock.tSimNow := T#2600MS;
    fbFaultResetAndBlock.xStart := TRUE;
    fbFaultResetAndBlock();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFaultResetAndBlock.xRun, Message := 'FaultResetAndBlock#4 xRun');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbFaultResetAndBlock.xFault,
                      Message := 'FaultResetAndBlock#4 xFault');
    AssertEquals_INT(Expected := 1, Actual := fbFaultResetAndBlock.iStarts, Message := 'FaultResetAndBlock#4 iStarts');

    // #5, t = 2700 мс — сброс: авария снята
    GVL_S7Clock.tSimNow := T#2700MS;
    fbFaultResetAndBlock.xStart := FALSE;
    fbFaultResetAndBlock.xReset := TRUE;
    fbFaultResetAndBlock();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFaultResetAndBlock.xRun, Message := 'FaultResetAndBlock#5 xRun');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbFaultResetAndBlock.xFault,
                      Message := 'FaultResetAndBlock#5 xFault');
    AssertEquals_INT(Expected := 1, Actual := fbFaultResetAndBlock.iStarts, Message := 'FaultResetAndBlock#5 iStarts');

    // #6, t = 2800 мс — Пуск: включается, пуск №2
    GVL_S7Clock.tSimNow := T#2800MS;
    fbFaultResetAndBlock.xStart := TRUE;
    fbFaultResetAndBlock.xReset := FALSE;
    fbFaultResetAndBlock();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbFaultResetAndBlock.xRun, Message := 'FaultResetAndBlock#6 xRun');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbFaultResetAndBlock.xFault,
                      Message := 'FaultResetAndBlock#6 xFault');
    AssertEquals_INT(Expected := 2, Actual := fbFaultResetAndBlock.iStarts, Message := 'FaultResetAndBlock#6 iStarts');

    // #7, t = 2900 мс — обратная связь: работает без аварии
    GVL_S7Clock.tSimNow := T#2900MS;
    fbFaultResetAndBlock.xStart := FALSE;
    fbFaultResetAndBlock.xFeedback := TRUE;
    fbFaultResetAndBlock();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbFaultResetAndBlock.xRun, Message := 'FaultResetAndBlock#7 xRun');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbFaultResetAndBlock.xFault,
                      Message := 'FaultResetAndBlock#7 xFault');
    AssertEquals_INT(Expected := 2, Actual := fbFaultResetAndBlock.iStarts, Message := 'FaultResetAndBlock#7 iStarts');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
