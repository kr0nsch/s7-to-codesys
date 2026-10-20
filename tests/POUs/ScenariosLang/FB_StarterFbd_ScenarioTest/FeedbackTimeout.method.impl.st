// AUTO-GENERATED — не редактировать: scenarios/lang/FB_Starter.csv, сценарий FeedbackTimeout
coUnit.TEST('FeedbackTimeout');
IF NOT xFeedbackTimeoutDone THEN
    xFeedbackTimeoutDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;

    // #1, t = 0 мс — покой
    GVL_S7Clock.tSimNow := T#0MS;
    fbFeedbackTimeout.xStart := FALSE;
    fbFeedbackTimeout.xStop := FALSE;
    fbFeedbackTimeout.xInterlock := TRUE;
    fbFeedbackTimeout.xFeedback := FALSE;
    fbFeedbackTimeout.tFeedbackTime := T#2000MS;
    fbFeedbackTimeout.xReset := FALSE;
    fbFeedbackTimeout();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFeedbackTimeout.xRun, Message := 'FeedbackTimeout#1 xRun');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFeedbackTimeout.xFault, Message := 'FeedbackTimeout#1 xFault');
    AssertEquals_INT(Expected := 0, Actual := fbFeedbackTimeout.iStarts, Message := 'FeedbackTimeout#1 iStarts');

    // #2, t = 100 мс — Пуск без обратной связи, таймер с 0.1 с
    GVL_S7Clock.tSimNow := T#100MS;
    fbFeedbackTimeout.xStart := TRUE;
    fbFeedbackTimeout();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbFeedbackTimeout.xRun, Message := 'FeedbackTimeout#2 xRun');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFeedbackTimeout.xFault, Message := 'FeedbackTimeout#2 xFault');
    AssertEquals_INT(Expected := 1, Actual := fbFeedbackTimeout.iStarts, Message := 'FeedbackTimeout#2 iStarts');

    // #3, t = 1900 мс — 1.8 с < 2 с: аварии нет
    GVL_S7Clock.tSimNow := T#1900MS;
    fbFeedbackTimeout.xStart := FALSE;
    fbFeedbackTimeout();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbFeedbackTimeout.xRun, Message := 'FeedbackTimeout#3 xRun');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFeedbackTimeout.xFault, Message := 'FeedbackTimeout#3 xFault');
    AssertEquals_INT(Expected := 1, Actual := fbFeedbackTimeout.iStarts, Message := 'FeedbackTimeout#3 iStarts');

    // #4, t = 2100 мс, на пороге таймера — 2.0 с = tFeedbackTime: авария; xRun ещё TRUE (сеть 1 раньше сети 3)
    GVL_S7Clock.tSimNow := T#2100MS;
    fbFeedbackTimeout();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbFeedbackTimeout.xRun, Message := 'FeedbackTimeout#4 xRun');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbFeedbackTimeout.xFault, Message := 'FeedbackTimeout#4 xFault');
    AssertEquals_INT(Expected := 1, Actual := fbFeedbackTimeout.iStarts, Message := 'FeedbackTimeout#4 iStarts');

    // #5, t = 2300 мс — R1 = xFault: насос выключен, авария держится
    GVL_S7Clock.tSimNow := T#2300MS;
    fbFeedbackTimeout();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFeedbackTimeout.xRun, Message := 'FeedbackTimeout#5 xRun');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbFeedbackTimeout.xFault, Message := 'FeedbackTimeout#5 xFault');
    AssertEquals_INT(Expected := 1, Actual := fbFeedbackTimeout.iStarts, Message := 'FeedbackTimeout#5 iStarts');

    // #6, t = 3000 мс — авария держится (самоподхват)
    GVL_S7Clock.tSimNow := T#3000MS;
    fbFeedbackTimeout();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFeedbackTimeout.xRun, Message := 'FeedbackTimeout#6 xRun');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbFeedbackTimeout.xFault, Message := 'FeedbackTimeout#6 xFault');
    AssertEquals_INT(Expected := 1, Actual := fbFeedbackTimeout.iStarts, Message := 'FeedbackTimeout#6 iStarts');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
