// AUTO-GENERATED — не редактировать: scenarios/lang/FB_Starter.csv, сценарий InterlockBlocksStart
coUnit.TEST('InterlockBlocksStart');
IF NOT xInterlockBlocksStartDone THEN
    xInterlockBlocksStartDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;

    // #1, t = 0 мс — блокировка
    GVL_S7Clock.tSimNow := T#0MS;
    fbInterlockBlocksStart.xStart := FALSE;
    fbInterlockBlocksStart.xStop := FALSE;
    fbInterlockBlocksStart.xInterlock := FALSE;
    fbInterlockBlocksStart.xFeedback := FALSE;
    fbInterlockBlocksStart.tFeedbackTime := T#2000MS;
    fbInterlockBlocksStart.xReset := FALSE;
    fbInterlockBlocksStart();
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbInterlockBlocksStart.xRun,
                      Message := 'InterlockBlocksStart#1 xRun');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbInterlockBlocksStart.xFault,
                      Message := 'InterlockBlocksStart#1 xFault');
    AssertEquals_INT(Expected := 0,
                     Actual := fbInterlockBlocksStart.iStarts,
                     Message := 'InterlockBlocksStart#1 iStarts');

    // #2, t = 100 мс — Пуск при блокировке: не включается
    GVL_S7Clock.tSimNow := T#100MS;
    fbInterlockBlocksStart.xStart := TRUE;
    fbInterlockBlocksStart();
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbInterlockBlocksStart.xRun,
                      Message := 'InterlockBlocksStart#2 xRun');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbInterlockBlocksStart.xFault,
                      Message := 'InterlockBlocksStart#2 xFault');
    AssertEquals_INT(Expected := 0,
                     Actual := fbInterlockBlocksStart.iStarts,
                     Message := 'InterlockBlocksStart#2 iStarts');

    // #3, t = 200 мс — кнопка отпущена
    GVL_S7Clock.tSimNow := T#200MS;
    fbInterlockBlocksStart.xStart := FALSE;
    fbInterlockBlocksStart();
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbInterlockBlocksStart.xRun,
                      Message := 'InterlockBlocksStart#3 xRun');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbInterlockBlocksStart.xFault,
                      Message := 'InterlockBlocksStart#3 xFault');
    AssertEquals_INT(Expected := 0,
                     Actual := fbInterlockBlocksStart.iStarts,
                     Message := 'InterlockBlocksStart#3 iStarts');

    // #4, t = 300 мс — блокировка снята: пуск не запомнен
    GVL_S7Clock.tSimNow := T#300MS;
    fbInterlockBlocksStart.xInterlock := TRUE;
    fbInterlockBlocksStart();
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbInterlockBlocksStart.xRun,
                      Message := 'InterlockBlocksStart#4 xRun');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbInterlockBlocksStart.xFault,
                      Message := 'InterlockBlocksStart#4 xFault');
    AssertEquals_INT(Expected := 0,
                     Actual := fbInterlockBlocksStart.iStarts,
                     Message := 'InterlockBlocksStart#4 iStarts');

    // #5, t = 400 мс — новый Пуск: включается, пуск №1
    GVL_S7Clock.tSimNow := T#400MS;
    fbInterlockBlocksStart.xStart := TRUE;
    fbInterlockBlocksStart();
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbInterlockBlocksStart.xRun,
                      Message := 'InterlockBlocksStart#5 xRun');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbInterlockBlocksStart.xFault,
                      Message := 'InterlockBlocksStart#5 xFault');
    AssertEquals_INT(Expected := 1,
                     Actual := fbInterlockBlocksStart.iStarts,
                     Message := 'InterlockBlocksStart#5 iStarts');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
