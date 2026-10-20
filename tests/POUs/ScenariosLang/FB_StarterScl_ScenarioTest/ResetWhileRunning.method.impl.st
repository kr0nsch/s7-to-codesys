// AUTO-GENERATED — не редактировать: scenarios/lang/FB_Starter.csv, сценарий ResetWhileRunning
coUnit.TEST('ResetWhileRunning');
IF NOT xResetWhileRunningDone THEN
    xResetWhileRunningDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;

    // #1, t = 0 мс — пуск №1
    GVL_S7Clock.tSimNow := T#0MS;
    fbResetWhileRunning.xStart := TRUE;
    fbResetWhileRunning.xStop := FALSE;
    fbResetWhileRunning.xInterlock := TRUE;
    fbResetWhileRunning.xFeedback := TRUE;
    fbResetWhileRunning.tFeedbackTime := T#2000MS;
    fbResetWhileRunning.xReset := FALSE;
    fbResetWhileRunning();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbResetWhileRunning.xRun, Message := 'ResetWhileRunning#1 xRun');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbResetWhileRunning.xFault, Message := 'ResetWhileRunning#1 xFault');
    AssertEquals_INT(Expected := 1, Actual := fbResetWhileRunning.iStarts, Message := 'ResetWhileRunning#1 iStarts');

    // #2, t = 100 мс — сброс в работе: без изменений
    GVL_S7Clock.tSimNow := T#100MS;
    fbResetWhileRunning.xStart := FALSE;
    fbResetWhileRunning.xReset := TRUE;
    fbResetWhileRunning();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbResetWhileRunning.xRun, Message := 'ResetWhileRunning#2 xRun');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbResetWhileRunning.xFault, Message := 'ResetWhileRunning#2 xFault');
    AssertEquals_INT(Expected := 1, Actual := fbResetWhileRunning.iStarts, Message := 'ResetWhileRunning#2 iStarts');

    // #3, t = 200 мс — Пуск в работе: SR уже установлен, счёта нет
    GVL_S7Clock.tSimNow := T#200MS;
    fbResetWhileRunning.xStart := TRUE;
    fbResetWhileRunning.xReset := FALSE;
    fbResetWhileRunning();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbResetWhileRunning.xRun, Message := 'ResetWhileRunning#3 xRun');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbResetWhileRunning.xFault, Message := 'ResetWhileRunning#3 xFault');
    AssertEquals_INT(Expected := 1, Actual := fbResetWhileRunning.iStarts, Message := 'ResetWhileRunning#3 iStarts');

    // #4, t = 300 мс — работает
    GVL_S7Clock.tSimNow := T#300MS;
    fbResetWhileRunning.xStart := FALSE;
    fbResetWhileRunning();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbResetWhileRunning.xRun, Message := 'ResetWhileRunning#4 xRun');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbResetWhileRunning.xFault, Message := 'ResetWhileRunning#4 xFault');
    AssertEquals_INT(Expected := 1, Actual := fbResetWhileRunning.iStarts, Message := 'ResetWhileRunning#4 iStarts');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
