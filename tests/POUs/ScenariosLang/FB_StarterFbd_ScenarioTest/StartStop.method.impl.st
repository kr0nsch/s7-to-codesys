// AUTO-GENERATED — не редактировать: scenarios/lang/FB_Starter.csv, сценарий StartStop
coUnit.TEST('StartStop');
IF NOT xStartStopDone THEN
    xStartStopDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;

    // #1, t = 0 мс — покой
    GVL_S7Clock.tSimNow := T#0MS;
    fbStartStop.xStart := FALSE;
    fbStartStop.xStop := FALSE;
    fbStartStop.xInterlock := TRUE;
    fbStartStop.xFeedback := FALSE;
    fbStartStop.tFeedbackTime := T#2000MS;
    fbStartStop.xReset := FALSE;
    fbStartStop();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStartStop.xRun, Message := 'StartStop#1 xRun');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStartStop.xFault, Message := 'StartStop#1 xFault');
    AssertEquals_INT(Expected := 0, Actual := fbStartStop.iStarts, Message := 'StartStop#1 iStarts');

    // #2, t = 100 мс — Пуск: SR установлен, пуск №1
    GVL_S7Clock.tSimNow := T#100MS;
    fbStartStop.xStart := TRUE;
    fbStartStop();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbStartStop.xRun, Message := 'StartStop#2 xRun');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStartStop.xFault, Message := 'StartStop#2 xFault');
    AssertEquals_INT(Expected := 1, Actual := fbStartStop.iStarts, Message := 'StartStop#2 iStarts');

    // #3, t = 200 мс — кнопка отпущена, обратная связь: работает
    GVL_S7Clock.tSimNow := T#200MS;
    fbStartStop.xStart := FALSE;
    fbStartStop.xFeedback := TRUE;
    fbStartStop();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbStartStop.xRun, Message := 'StartStop#3 xRun');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStartStop.xFault, Message := 'StartStop#3 xFault');
    AssertEquals_INT(Expected := 1, Actual := fbStartStop.iStarts, Message := 'StartStop#3 iStarts');

    // #4, t = 1000 мс — Стоп: SR сброшен
    GVL_S7Clock.tSimNow := T#1000MS;
    fbStartStop.xStop := TRUE;
    fbStartStop();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStartStop.xRun, Message := 'StartStop#4 xRun');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStartStop.xFault, Message := 'StartStop#4 xFault');
    AssertEquals_INT(Expected := 1, Actual := fbStartStop.iStarts, Message := 'StartStop#4 iStarts');

    // #5, t = 1100 мс — стоп отпущен: остаётся выключенным
    GVL_S7Clock.tSimNow := T#1100MS;
    fbStartStop.xStop := FALSE;
    fbStartStop.xFeedback := FALSE;
    fbStartStop();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStartStop.xRun, Message := 'StartStop#5 xRun');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStartStop.xFault, Message := 'StartStop#5 xFault');
    AssertEquals_INT(Expected := 1, Actual := fbStartStop.iStarts, Message := 'StartStop#5 iStarts');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
