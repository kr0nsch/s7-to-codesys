// AUTO-GENERATED — не редактировать: scenarios/lang/FB_Starter.csv, сценарий StartAndStopTogether
coUnit.TEST('StartAndStopTogether');
IF NOT xStartAndStopTogetherDone THEN
    xStartAndStopTogetherDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;

    // #1, t = 0 мс — покой
    GVL_S7Clock.tSimNow := T#0MS;
    fbStartAndStopTogether.xStart := FALSE;
    fbStartAndStopTogether.xStop := FALSE;
    fbStartAndStopTogether.xInterlock := TRUE;
    fbStartAndStopTogether.xFeedback := FALSE;
    fbStartAndStopTogether.tFeedbackTime := T#2000MS;
    fbStartAndStopTogether.xReset := FALSE;
    fbStartAndStopTogether();
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbStartAndStopTogether.xRun,
                      Message := 'StartAndStopTogether#1 xRun');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbStartAndStopTogether.xFault,
                      Message := 'StartAndStopTogether#1 xFault');
    AssertEquals_INT(Expected := 0,
                     Actual := fbStartAndStopTogether.iStarts,
                     Message := 'StartAndStopTogether#1 iStarts');

    // #2, t = 100 мс — S = R1 = 1: не включается
    GVL_S7Clock.tSimNow := T#100MS;
    fbStartAndStopTogether.xStart := TRUE;
    fbStartAndStopTogether.xStop := TRUE;
    fbStartAndStopTogether();
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbStartAndStopTogether.xRun,
                      Message := 'StartAndStopTogether#2 xRun');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbStartAndStopTogether.xFault,
                      Message := 'StartAndStopTogether#2 xFault');
    AssertEquals_INT(Expected := 0,
                     Actual := fbStartAndStopTogether.iStarts,
                     Message := 'StartAndStopTogether#2 iStarts');

    // #3, t = 200 мс — Стоп отпущен, Пуск держится: включается, пуск №1
    GVL_S7Clock.tSimNow := T#200MS;
    fbStartAndStopTogether.xStop := FALSE;
    fbStartAndStopTogether();
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbStartAndStopTogether.xRun,
                      Message := 'StartAndStopTogether#3 xRun');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbStartAndStopTogether.xFault,
                      Message := 'StartAndStopTogether#3 xFault');
    AssertEquals_INT(Expected := 1,
                     Actual := fbStartAndStopTogether.iStarts,
                     Message := 'StartAndStopTogether#3 iStarts');

    // #4, t = 300 мс — работает
    GVL_S7Clock.tSimNow := T#300MS;
    fbStartAndStopTogether.xStart := FALSE;
    fbStartAndStopTogether.xFeedback := TRUE;
    fbStartAndStopTogether();
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbStartAndStopTogether.xRun,
                      Message := 'StartAndStopTogether#4 xRun');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbStartAndStopTogether.xFault,
                      Message := 'StartAndStopTogether#4 xFault');
    AssertEquals_INT(Expected := 1,
                     Actual := fbStartAndStopTogether.iStarts,
                     Message := 'StartAndStopTogether#4 iStarts');

    // #5, t = 400 мс — в работе снова S = R1 = 1: выключается
    GVL_S7Clock.tSimNow := T#400MS;
    fbStartAndStopTogether.xStart := TRUE;
    fbStartAndStopTogether.xStop := TRUE;
    fbStartAndStopTogether();
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbStartAndStopTogether.xRun,
                      Message := 'StartAndStopTogether#5 xRun');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbStartAndStopTogether.xFault,
                      Message := 'StartAndStopTogether#5 xFault');
    AssertEquals_INT(Expected := 1,
                     Actual := fbStartAndStopTogether.iStarts,
                     Message := 'StartAndStopTogether#5 iStarts');

    // #6, t = 500 мс — выключен
    GVL_S7Clock.tSimNow := T#500MS;
    fbStartAndStopTogether.xStart := FALSE;
    fbStartAndStopTogether.xStop := FALSE;
    fbStartAndStopTogether.xFeedback := FALSE;
    fbStartAndStopTogether();
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbStartAndStopTogether.xRun,
                      Message := 'StartAndStopTogether#6 xRun');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbStartAndStopTogether.xFault,
                      Message := 'StartAndStopTogether#6 xFault');
    AssertEquals_INT(Expected := 1,
                     Actual := fbStartAndStopTogether.iStarts,
                     Message := 'StartAndStopTogether#6 iStarts');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
