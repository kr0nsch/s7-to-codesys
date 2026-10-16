// AUTO-GENERATED — не редактировать: scenarios/FB_Motor.csv, сценарий FeedbackLost
coUnit.TEST('FeedbackLost');
IF NOT xFeedbackLostDone THEN
    xFeedbackLostDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;

    // #1, t = 0 мс — пуск
    GVL_S7Clock.tSimNow := T#0MS;
    fbFeedbackLost.autoMode := TRUE;
    fbFeedbackLost.autoStart := TRUE;
    fbFeedbackLost.manStart := FALSE;
    fbFeedbackLost.manStop := FALSE;
    fbFeedbackLost.feedback := FALSE;
    fbFeedbackLost.thermalOk := TRUE;
    fbFeedbackLost.reset := FALSE;
    fbFeedbackLost.feedbackTime := T#3000MS;
    fbFeedbackLost();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbFeedbackLost.runCmd, Message := 'FeedbackLost#1 runCmd');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFeedbackLost.fault, Message := 'FeedbackLost#1 fault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbFeedbackLost.status.running,
                      Message := 'FeedbackLost#1 status.running');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbFeedbackLost.status.fault,
                      Message := 'FeedbackLost#1 status.fault');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbFeedbackLost.status.autoMode,
                      Message := 'FeedbackLost#1 status.autoMode');
    AssertEquals_INT(Expected := 0,
                     Actual := fbFeedbackLost.status.faultCode,
                     Message := 'FeedbackLost#1 status.faultCode');
    AssertEquals_DINT(Expected := 1,
                      Actual := fbFeedbackLost.status.startCount,
                      Message := 'FeedbackLost#1 status.startCount');

    // #2, t = 500 мс — обратная связь есть
    GVL_S7Clock.tSimNow := T#500MS;
    fbFeedbackLost.feedback := TRUE;
    fbFeedbackLost();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbFeedbackLost.runCmd, Message := 'FeedbackLost#2 runCmd');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFeedbackLost.fault, Message := 'FeedbackLost#2 fault');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbFeedbackLost.status.running,
                      Message := 'FeedbackLost#2 status.running');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbFeedbackLost.status.fault,
                      Message := 'FeedbackLost#2 status.fault');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbFeedbackLost.status.autoMode,
                      Message := 'FeedbackLost#2 status.autoMode');
    AssertEquals_INT(Expected := 0,
                     Actual := fbFeedbackLost.status.faultCode,
                     Message := 'FeedbackLost#2 status.faultCode');
    AssertEquals_DINT(Expected := 1,
                      Actual := fbFeedbackLost.status.startCount,
                      Message := 'FeedbackLost#2 status.startCount');

    // #3, t = 10000 мс — обратная связь пропала; отсчёт с 10.0 с
    GVL_S7Clock.tSimNow := T#10000MS;
    fbFeedbackLost.feedback := FALSE;
    fbFeedbackLost();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbFeedbackLost.runCmd, Message := 'FeedbackLost#3 runCmd');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFeedbackLost.fault, Message := 'FeedbackLost#3 fault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbFeedbackLost.status.running,
                      Message := 'FeedbackLost#3 status.running');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbFeedbackLost.status.fault,
                      Message := 'FeedbackLost#3 status.fault');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbFeedbackLost.status.autoMode,
                      Message := 'FeedbackLost#3 status.autoMode');
    AssertEquals_INT(Expected := 0,
                     Actual := fbFeedbackLost.status.faultCode,
                     Message := 'FeedbackLost#3 status.faultCode');
    AssertEquals_DINT(Expected := 1,
                      Actual := fbFeedbackLost.status.startCount,
                      Message := 'FeedbackLost#3 status.startCount');

    // #4, t = 12800 мс — 2.8 с без обратной связи: аварии нет
    GVL_S7Clock.tSimNow := T#12800MS;
    fbFeedbackLost();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbFeedbackLost.runCmd, Message := 'FeedbackLost#4 runCmd');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFeedbackLost.fault, Message := 'FeedbackLost#4 fault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbFeedbackLost.status.running,
                      Message := 'FeedbackLost#4 status.running');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbFeedbackLost.status.fault,
                      Message := 'FeedbackLost#4 status.fault');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbFeedbackLost.status.autoMode,
                      Message := 'FeedbackLost#4 status.autoMode');
    AssertEquals_INT(Expected := 0,
                     Actual := fbFeedbackLost.status.faultCode,
                     Message := 'FeedbackLost#4 status.faultCode');
    AssertEquals_DINT(Expected := 1,
                      Actual := fbFeedbackLost.status.startCount,
                      Message := 'FeedbackLost#4 status.startCount');

    // #5, t = 13200 мс — 3.2 с: авария 2 (обратная связь уже была), runCmd снят
    GVL_S7Clock.tSimNow := T#13200MS;
    fbFeedbackLost();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFeedbackLost.runCmd, Message := 'FeedbackLost#5 runCmd');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbFeedbackLost.fault, Message := 'FeedbackLost#5 fault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbFeedbackLost.status.running,
                      Message := 'FeedbackLost#5 status.running');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbFeedbackLost.status.fault,
                      Message := 'FeedbackLost#5 status.fault');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbFeedbackLost.status.autoMode,
                      Message := 'FeedbackLost#5 status.autoMode');
    AssertEquals_INT(Expected := 2,
                     Actual := fbFeedbackLost.status.faultCode,
                     Message := 'FeedbackLost#5 status.faultCode');
    AssertEquals_DINT(Expected := 1,
                      Actual := fbFeedbackLost.status.startCount,
                      Message := 'FeedbackLost#5 status.startCount');

    // #6, t = 14000 мс — сброс, запроса нет — стоит без аварии
    GVL_S7Clock.tSimNow := T#14000MS;
    fbFeedbackLost.autoStart := FALSE;
    fbFeedbackLost.reset := TRUE;
    fbFeedbackLost();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFeedbackLost.runCmd, Message := 'FeedbackLost#6 runCmd');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFeedbackLost.fault, Message := 'FeedbackLost#6 fault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbFeedbackLost.status.running,
                      Message := 'FeedbackLost#6 status.running');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbFeedbackLost.status.fault,
                      Message := 'FeedbackLost#6 status.fault');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbFeedbackLost.status.autoMode,
                      Message := 'FeedbackLost#6 status.autoMode');
    AssertEquals_INT(Expected := 0,
                     Actual := fbFeedbackLost.status.faultCode,
                     Message := 'FeedbackLost#6 status.faultCode');
    AssertEquals_DINT(Expected := 1,
                      Actual := fbFeedbackLost.status.startCount,
                      Message := 'FeedbackLost#6 status.startCount');

    // #7, t = 14500 мс — покой
    GVL_S7Clock.tSimNow := T#14500MS;
    fbFeedbackLost.reset := FALSE;
    fbFeedbackLost();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFeedbackLost.runCmd, Message := 'FeedbackLost#7 runCmd');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFeedbackLost.fault, Message := 'FeedbackLost#7 fault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbFeedbackLost.status.running,
                      Message := 'FeedbackLost#7 status.running');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbFeedbackLost.status.fault,
                      Message := 'FeedbackLost#7 status.fault');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbFeedbackLost.status.autoMode,
                      Message := 'FeedbackLost#7 status.autoMode');
    AssertEquals_INT(Expected := 0,
                     Actual := fbFeedbackLost.status.faultCode,
                     Message := 'FeedbackLost#7 status.faultCode');
    AssertEquals_DINT(Expected := 1,
                      Actual := fbFeedbackLost.status.startCount,
                      Message := 'FeedbackLost#7 status.startCount');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
