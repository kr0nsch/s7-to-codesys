// AUTO-GENERATED — не редактировать: scenarios/FB_Motor.csv, сценарий NoFeedbackTimeout
coUnit.TEST('NoFeedbackTimeout');
IF NOT xNoFeedbackTimeoutDone THEN
    xNoFeedbackTimeoutDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;

    // #1, t = 0 мс — пуск, обратной связи нет
    GVL_S7Clock.tSimNow := T#0MS;
    fbNoFeedbackTimeout.autoMode := TRUE;
    fbNoFeedbackTimeout.autoStart := TRUE;
    fbNoFeedbackTimeout.manStart := FALSE;
    fbNoFeedbackTimeout.manStop := FALSE;
    fbNoFeedbackTimeout.feedback := FALSE;
    fbNoFeedbackTimeout.thermalOk := TRUE;
    fbNoFeedbackTimeout.reset := FALSE;
    fbNoFeedbackTimeout.feedbackTime := T#3000MS;
    fbNoFeedbackTimeout();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbNoFeedbackTimeout.runCmd, Message := 'NoFeedbackTimeout#1 runCmd');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbNoFeedbackTimeout.fault, Message := 'NoFeedbackTimeout#1 fault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbNoFeedbackTimeout.status.running,
                      Message := 'NoFeedbackTimeout#1 status.running');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbNoFeedbackTimeout.status.fault,
                      Message := 'NoFeedbackTimeout#1 status.fault');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbNoFeedbackTimeout.status.autoMode,
                      Message := 'NoFeedbackTimeout#1 status.autoMode');
    AssertEquals_INT(Expected := 0,
                     Actual := fbNoFeedbackTimeout.status.faultCode,
                     Message := 'NoFeedbackTimeout#1 status.faultCode');
    AssertEquals_DINT(Expected := 1,
                      Actual := fbNoFeedbackTimeout.status.startCount,
                      Message := 'NoFeedbackTimeout#1 status.startCount');

    // #2, t = 2800 мс — 2.8 с < 3 с: аварии нет
    GVL_S7Clock.tSimNow := T#2800MS;
    fbNoFeedbackTimeout();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbNoFeedbackTimeout.runCmd, Message := 'NoFeedbackTimeout#2 runCmd');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbNoFeedbackTimeout.fault, Message := 'NoFeedbackTimeout#2 fault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbNoFeedbackTimeout.status.running,
                      Message := 'NoFeedbackTimeout#2 status.running');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbNoFeedbackTimeout.status.fault,
                      Message := 'NoFeedbackTimeout#2 status.fault');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbNoFeedbackTimeout.status.autoMode,
                      Message := 'NoFeedbackTimeout#2 status.autoMode');
    AssertEquals_INT(Expected := 0,
                     Actual := fbNoFeedbackTimeout.status.faultCode,
                     Message := 'NoFeedbackTimeout#2 status.faultCode');
    AssertEquals_DINT(Expected := 1,
                      Actual := fbNoFeedbackTimeout.status.startCount,
                      Message := 'NoFeedbackTimeout#2 status.startCount');

    // #3, t = 3000 мс, на пороге таймера — 3.0 с = feedbackTime: авария 1, runCmd снят в этом же вызове
    GVL_S7Clock.tSimNow := T#3000MS;
    fbNoFeedbackTimeout();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbNoFeedbackTimeout.runCmd, Message := 'NoFeedbackTimeout#3 runCmd');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbNoFeedbackTimeout.fault, Message := 'NoFeedbackTimeout#3 fault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbNoFeedbackTimeout.status.running,
                      Message := 'NoFeedbackTimeout#3 status.running');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbNoFeedbackTimeout.status.fault,
                      Message := 'NoFeedbackTimeout#3 status.fault');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbNoFeedbackTimeout.status.autoMode,
                      Message := 'NoFeedbackTimeout#3 status.autoMode');
    AssertEquals_INT(Expected := 1,
                     Actual := fbNoFeedbackTimeout.status.faultCode,
                     Message := 'NoFeedbackTimeout#3 status.faultCode');
    AssertEquals_DINT(Expected := 1,
                      Actual := fbNoFeedbackTimeout.status.startCount,
                      Message := 'NoFeedbackTimeout#3 status.startCount');

    // #4, t = 3200 мс — авария держится, код 1
    GVL_S7Clock.tSimNow := T#3200MS;
    fbNoFeedbackTimeout();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbNoFeedbackTimeout.runCmd, Message := 'NoFeedbackTimeout#4 runCmd');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbNoFeedbackTimeout.fault, Message := 'NoFeedbackTimeout#4 fault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbNoFeedbackTimeout.status.running,
                      Message := 'NoFeedbackTimeout#4 status.running');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbNoFeedbackTimeout.status.fault,
                      Message := 'NoFeedbackTimeout#4 status.fault');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbNoFeedbackTimeout.status.autoMode,
                      Message := 'NoFeedbackTimeout#4 status.autoMode');
    AssertEquals_INT(Expected := 1,
                     Actual := fbNoFeedbackTimeout.status.faultCode,
                     Message := 'NoFeedbackTimeout#4 status.faultCode');
    AssertEquals_DINT(Expected := 1,
                      Actual := fbNoFeedbackTimeout.status.startCount,
                      Message := 'NoFeedbackTimeout#4 status.startCount');

    // #5, t = 4000 мс — сброс по фронту: авто-запрос ещё есть — повторный пуск №2
    GVL_S7Clock.tSimNow := T#4000MS;
    fbNoFeedbackTimeout.reset := TRUE;
    fbNoFeedbackTimeout();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbNoFeedbackTimeout.runCmd, Message := 'NoFeedbackTimeout#5 runCmd');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbNoFeedbackTimeout.fault, Message := 'NoFeedbackTimeout#5 fault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbNoFeedbackTimeout.status.running,
                      Message := 'NoFeedbackTimeout#5 status.running');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbNoFeedbackTimeout.status.fault,
                      Message := 'NoFeedbackTimeout#5 status.fault');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbNoFeedbackTimeout.status.autoMode,
                      Message := 'NoFeedbackTimeout#5 status.autoMode');
    AssertEquals_INT(Expected := 0,
                     Actual := fbNoFeedbackTimeout.status.faultCode,
                     Message := 'NoFeedbackTimeout#5 status.faultCode');
    AssertEquals_DINT(Expected := 2,
                      Actual := fbNoFeedbackTimeout.status.startCount,
                      Message := 'NoFeedbackTimeout#5 status.startCount');

    // #6, t = 4500 мс — обратная связь пришла: работает
    GVL_S7Clock.tSimNow := T#4500MS;
    fbNoFeedbackTimeout.feedback := TRUE;
    fbNoFeedbackTimeout.reset := FALSE;
    fbNoFeedbackTimeout();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbNoFeedbackTimeout.runCmd, Message := 'NoFeedbackTimeout#6 runCmd');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbNoFeedbackTimeout.fault, Message := 'NoFeedbackTimeout#6 fault');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbNoFeedbackTimeout.status.running,
                      Message := 'NoFeedbackTimeout#6 status.running');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbNoFeedbackTimeout.status.fault,
                      Message := 'NoFeedbackTimeout#6 status.fault');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbNoFeedbackTimeout.status.autoMode,
                      Message := 'NoFeedbackTimeout#6 status.autoMode');
    AssertEquals_INT(Expected := 0,
                     Actual := fbNoFeedbackTimeout.status.faultCode,
                     Message := 'NoFeedbackTimeout#6 status.faultCode');
    AssertEquals_DINT(Expected := 2,
                      Actual := fbNoFeedbackTimeout.status.startCount,
                      Message := 'NoFeedbackTimeout#6 status.startCount');

    // #7, t = 8000 мс — работает
    GVL_S7Clock.tSimNow := T#8000MS;
    fbNoFeedbackTimeout();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbNoFeedbackTimeout.runCmd, Message := 'NoFeedbackTimeout#7 runCmd');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbNoFeedbackTimeout.fault, Message := 'NoFeedbackTimeout#7 fault');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbNoFeedbackTimeout.status.running,
                      Message := 'NoFeedbackTimeout#7 status.running');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbNoFeedbackTimeout.status.fault,
                      Message := 'NoFeedbackTimeout#7 status.fault');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbNoFeedbackTimeout.status.autoMode,
                      Message := 'NoFeedbackTimeout#7 status.autoMode');
    AssertEquals_INT(Expected := 0,
                     Actual := fbNoFeedbackTimeout.status.faultCode,
                     Message := 'NoFeedbackTimeout#7 status.faultCode');
    AssertEquals_DINT(Expected := 2,
                      Actual := fbNoFeedbackTimeout.status.startCount,
                      Message := 'NoFeedbackTimeout#7 status.startCount');

    // #8, t = 8100 мс — стоп
    GVL_S7Clock.tSimNow := T#8100MS;
    fbNoFeedbackTimeout.autoStart := FALSE;
    fbNoFeedbackTimeout();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbNoFeedbackTimeout.runCmd, Message := 'NoFeedbackTimeout#8 runCmd');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbNoFeedbackTimeout.fault, Message := 'NoFeedbackTimeout#8 fault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbNoFeedbackTimeout.status.running,
                      Message := 'NoFeedbackTimeout#8 status.running');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbNoFeedbackTimeout.status.fault,
                      Message := 'NoFeedbackTimeout#8 status.fault');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbNoFeedbackTimeout.status.autoMode,
                      Message := 'NoFeedbackTimeout#8 status.autoMode');
    AssertEquals_INT(Expected := 0,
                     Actual := fbNoFeedbackTimeout.status.faultCode,
                     Message := 'NoFeedbackTimeout#8 status.faultCode');
    AssertEquals_DINT(Expected := 2,
                      Actual := fbNoFeedbackTimeout.status.startCount,
                      Message := 'NoFeedbackTimeout#8 status.startCount');

    // #9, t = 8300 мс — контактор отпал
    GVL_S7Clock.tSimNow := T#8300MS;
    fbNoFeedbackTimeout.feedback := FALSE;
    fbNoFeedbackTimeout();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbNoFeedbackTimeout.runCmd, Message := 'NoFeedbackTimeout#9 runCmd');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbNoFeedbackTimeout.fault, Message := 'NoFeedbackTimeout#9 fault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbNoFeedbackTimeout.status.running,
                      Message := 'NoFeedbackTimeout#9 status.running');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbNoFeedbackTimeout.status.fault,
                      Message := 'NoFeedbackTimeout#9 status.fault');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbNoFeedbackTimeout.status.autoMode,
                      Message := 'NoFeedbackTimeout#9 status.autoMode');
    AssertEquals_INT(Expected := 0,
                     Actual := fbNoFeedbackTimeout.status.faultCode,
                     Message := 'NoFeedbackTimeout#9 status.faultCode');
    AssertEquals_DINT(Expected := 2,
                      Actual := fbNoFeedbackTimeout.status.startCount,
                      Message := 'NoFeedbackTimeout#9 status.startCount');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
