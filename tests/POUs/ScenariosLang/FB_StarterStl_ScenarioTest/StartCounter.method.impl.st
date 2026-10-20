// AUTO-GENERATED — не редактировать: scenarios/lang/FB_Starter.csv, сценарий StartCounter
coUnit.TEST('StartCounter');
IF NOT xStartCounterDone THEN
    xStartCounterDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;

    // #1, t = 0 мс — пуск №1
    GVL_S7Clock.tSimNow := T#0MS;
    fbStartCounter.xStart := TRUE;
    fbStartCounter.xStop := FALSE;
    fbStartCounter.xInterlock := TRUE;
    fbStartCounter.xFeedback := TRUE;
    fbStartCounter.tFeedbackTime := T#2000MS;
    fbStartCounter.xReset := FALSE;
    fbStartCounter();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbStartCounter.xRun, Message := 'StartCounter#1 xRun');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStartCounter.xFault, Message := 'StartCounter#1 xFault');
    AssertEquals_INT(Expected := 1, Actual := fbStartCounter.iStarts, Message := 'StartCounter#1 iStarts');

    // #2, t = 100 мс — Пуск держится: без нового счёта
    GVL_S7Clock.tSimNow := T#100MS;
    fbStartCounter();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbStartCounter.xRun, Message := 'StartCounter#2 xRun');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStartCounter.xFault, Message := 'StartCounter#2 xFault');
    AssertEquals_INT(Expected := 1, Actual := fbStartCounter.iStarts, Message := 'StartCounter#2 iStarts');

    // #3, t = 200 мс — стоп
    GVL_S7Clock.tSimNow := T#200MS;
    fbStartCounter.xStart := FALSE;
    fbStartCounter.xStop := TRUE;
    fbStartCounter();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStartCounter.xRun, Message := 'StartCounter#3 xRun');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStartCounter.xFault, Message := 'StartCounter#3 xFault');
    AssertEquals_INT(Expected := 1, Actual := fbStartCounter.iStarts, Message := 'StartCounter#3 iStarts');

    // #4, t = 300 мс — пуск №2
    GVL_S7Clock.tSimNow := T#300MS;
    fbStartCounter.xStart := TRUE;
    fbStartCounter.xStop := FALSE;
    fbStartCounter();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbStartCounter.xRun, Message := 'StartCounter#4 xRun');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStartCounter.xFault, Message := 'StartCounter#4 xFault');
    AssertEquals_INT(Expected := 2, Actual := fbStartCounter.iStarts, Message := 'StartCounter#4 iStarts');

    // #5, t = 400 мс — стоп
    GVL_S7Clock.tSimNow := T#400MS;
    fbStartCounter.xStart := FALSE;
    fbStartCounter.xStop := TRUE;
    fbStartCounter();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStartCounter.xRun, Message := 'StartCounter#5 xRun');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStartCounter.xFault, Message := 'StartCounter#5 xFault');
    AssertEquals_INT(Expected := 2, Actual := fbStartCounter.iStarts, Message := 'StartCounter#5 iStarts');

    // #6, t = 500 мс — покой: 2 пуска
    GVL_S7Clock.tSimNow := T#500MS;
    fbStartCounter.xStop := FALSE;
    fbStartCounter();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStartCounter.xRun, Message := 'StartCounter#6 xRun');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStartCounter.xFault, Message := 'StartCounter#6 xFault');
    AssertEquals_INT(Expected := 2, Actual := fbStartCounter.iStarts, Message := 'StartCounter#6 iStarts');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
