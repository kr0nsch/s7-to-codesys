// AUTO-GENERATED — не редактировать: scenarios/lang/FB_Starter.csv, сценарий FeedbackOk
coUnit.TEST('FeedbackOk');
IF NOT xFeedbackOkDone THEN
    xFeedbackOkDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;

    // #1, t = 0 мс — покой
    GVL_S7Clock.tSimNow := T#0MS;
    fbFeedbackOk.xStart := FALSE;
    fbFeedbackOk.xStop := FALSE;
    fbFeedbackOk.xInterlock := TRUE;
    fbFeedbackOk.xFeedback := FALSE;
    fbFeedbackOk.tFeedbackTime := T#2000MS;
    fbFeedbackOk.xReset := FALSE;
    fbFeedbackOk();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFeedbackOk.xRun, Message := 'FeedbackOk#1 xRun');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFeedbackOk.xFault, Message := 'FeedbackOk#1 xFault');
    AssertEquals_INT(Expected := 0, Actual := fbFeedbackOk.iStarts, Message := 'FeedbackOk#1 iStarts');

    // #2, t = 100 мс — Пуск, таймер обратной связи с 0.1 с
    GVL_S7Clock.tSimNow := T#100MS;
    fbFeedbackOk.xStart := TRUE;
    fbFeedbackOk();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbFeedbackOk.xRun, Message := 'FeedbackOk#2 xRun');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFeedbackOk.xFault, Message := 'FeedbackOk#2 xFault');
    AssertEquals_INT(Expected := 1, Actual := fbFeedbackOk.iStarts, Message := 'FeedbackOk#2 iStarts');

    // #3, t = 1000 мс — обратная связь через 0.9 с
    GVL_S7Clock.tSimNow := T#1000MS;
    fbFeedbackOk.xStart := FALSE;
    fbFeedbackOk.xFeedback := TRUE;
    fbFeedbackOk();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbFeedbackOk.xRun, Message := 'FeedbackOk#3 xRun');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFeedbackOk.xFault, Message := 'FeedbackOk#3 xFault');
    AssertEquals_INT(Expected := 1, Actual := fbFeedbackOk.iStarts, Message := 'FeedbackOk#3 iStarts');

    // #4, t = 5000 мс — работает, аварии нет
    GVL_S7Clock.tSimNow := T#5000MS;
    fbFeedbackOk();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbFeedbackOk.xRun, Message := 'FeedbackOk#4 xRun');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFeedbackOk.xFault, Message := 'FeedbackOk#4 xFault');
    AssertEquals_INT(Expected := 1, Actual := fbFeedbackOk.iStarts, Message := 'FeedbackOk#4 iStarts');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
