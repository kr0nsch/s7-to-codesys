// AUTO-GENERATED — не редактировать: scenarios/FB_Motor.csv, сценарий UnexpectedFeedback
coUnit.TEST('UnexpectedFeedback');
IF NOT xUnexpectedFeedbackDone THEN
    xUnexpectedFeedbackDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;

    // #1, t = 0 мс — команды нет, обратная связь есть
    GVL_S7Clock.tSimNow := T#0MS;
    fbUnexpectedFeedback.autoMode := TRUE;
    fbUnexpectedFeedback.autoStart := FALSE;
    fbUnexpectedFeedback.manStart := FALSE;
    fbUnexpectedFeedback.manStop := FALSE;
    fbUnexpectedFeedback.feedback := TRUE;
    fbUnexpectedFeedback.thermalOk := TRUE;
    fbUnexpectedFeedback.reset := FALSE;
    fbUnexpectedFeedback.feedbackTime := T#3000MS;
    fbUnexpectedFeedback();
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbUnexpectedFeedback.runCmd,
                      Message := 'UnexpectedFeedback#1 runCmd');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbUnexpectedFeedback.fault, Message := 'UnexpectedFeedback#1 fault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbUnexpectedFeedback.status.running,
                      Message := 'UnexpectedFeedback#1 status.running');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbUnexpectedFeedback.status.fault,
                      Message := 'UnexpectedFeedback#1 status.fault');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbUnexpectedFeedback.status.autoMode,
                      Message := 'UnexpectedFeedback#1 status.autoMode');
    AssertEquals_INT(Expected := 0,
                     Actual := fbUnexpectedFeedback.status.faultCode,
                     Message := 'UnexpectedFeedback#1 status.faultCode');
    AssertEquals_DINT(Expected := 0,
                      Actual := fbUnexpectedFeedback.status.startCount,
                      Message := 'UnexpectedFeedback#1 status.startCount');

    // #2, t = 3200 мс — 3.2 с: авария 4
    GVL_S7Clock.tSimNow := T#3200MS;
    fbUnexpectedFeedback();
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbUnexpectedFeedback.runCmd,
                      Message := 'UnexpectedFeedback#2 runCmd');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbUnexpectedFeedback.fault, Message := 'UnexpectedFeedback#2 fault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbUnexpectedFeedback.status.running,
                      Message := 'UnexpectedFeedback#2 status.running');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbUnexpectedFeedback.status.fault,
                      Message := 'UnexpectedFeedback#2 status.fault');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbUnexpectedFeedback.status.autoMode,
                      Message := 'UnexpectedFeedback#2 status.autoMode');
    AssertEquals_INT(Expected := 4,
                     Actual := fbUnexpectedFeedback.status.faultCode,
                     Message := 'UnexpectedFeedback#2 status.faultCode');
    AssertEquals_DINT(Expected := 0,
                      Actual := fbUnexpectedFeedback.status.startCount,
                      Message := 'UnexpectedFeedback#2 status.startCount');

    // #3, t = 4000 мс — сброс: таймер всё ещё в Q — авария 4 снова в том же вызове
    GVL_S7Clock.tSimNow := T#4000MS;
    fbUnexpectedFeedback.reset := TRUE;
    fbUnexpectedFeedback();
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbUnexpectedFeedback.runCmd,
                      Message := 'UnexpectedFeedback#3 runCmd');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbUnexpectedFeedback.fault, Message := 'UnexpectedFeedback#3 fault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbUnexpectedFeedback.status.running,
                      Message := 'UnexpectedFeedback#3 status.running');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbUnexpectedFeedback.status.fault,
                      Message := 'UnexpectedFeedback#3 status.fault');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbUnexpectedFeedback.status.autoMode,
                      Message := 'UnexpectedFeedback#3 status.autoMode');
    AssertEquals_INT(Expected := 4,
                     Actual := fbUnexpectedFeedback.status.faultCode,
                     Message := 'UnexpectedFeedback#3 status.faultCode');
    AssertEquals_DINT(Expected := 0,
                      Actual := fbUnexpectedFeedback.status.startCount,
                      Message := 'UnexpectedFeedback#3 status.startCount');

    // #4, t = 4500 мс — контактор отпал, авария держится
    GVL_S7Clock.tSimNow := T#4500MS;
    fbUnexpectedFeedback.feedback := FALSE;
    fbUnexpectedFeedback.reset := FALSE;
    fbUnexpectedFeedback();
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbUnexpectedFeedback.runCmd,
                      Message := 'UnexpectedFeedback#4 runCmd');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbUnexpectedFeedback.fault, Message := 'UnexpectedFeedback#4 fault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbUnexpectedFeedback.status.running,
                      Message := 'UnexpectedFeedback#4 status.running');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbUnexpectedFeedback.status.fault,
                      Message := 'UnexpectedFeedback#4 status.fault');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbUnexpectedFeedback.status.autoMode,
                      Message := 'UnexpectedFeedback#4 status.autoMode');
    AssertEquals_INT(Expected := 4,
                     Actual := fbUnexpectedFeedback.status.faultCode,
                     Message := 'UnexpectedFeedback#4 status.faultCode');
    AssertEquals_DINT(Expected := 0,
                      Actual := fbUnexpectedFeedback.status.startCount,
                      Message := 'UnexpectedFeedback#4 status.startCount');

    // #5, t = 5000 мс — сброс: авария снята
    GVL_S7Clock.tSimNow := T#5000MS;
    fbUnexpectedFeedback.reset := TRUE;
    fbUnexpectedFeedback();
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbUnexpectedFeedback.runCmd,
                      Message := 'UnexpectedFeedback#5 runCmd');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbUnexpectedFeedback.fault, Message := 'UnexpectedFeedback#5 fault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbUnexpectedFeedback.status.running,
                      Message := 'UnexpectedFeedback#5 status.running');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbUnexpectedFeedback.status.fault,
                      Message := 'UnexpectedFeedback#5 status.fault');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbUnexpectedFeedback.status.autoMode,
                      Message := 'UnexpectedFeedback#5 status.autoMode');
    AssertEquals_INT(Expected := 0,
                     Actual := fbUnexpectedFeedback.status.faultCode,
                     Message := 'UnexpectedFeedback#5 status.faultCode');
    AssertEquals_DINT(Expected := 0,
                      Actual := fbUnexpectedFeedback.status.startCount,
                      Message := 'UnexpectedFeedback#5 status.startCount');

    // #6, t = 5500 мс — пуск №1
    GVL_S7Clock.tSimNow := T#5500MS;
    fbUnexpectedFeedback.autoStart := TRUE;
    fbUnexpectedFeedback.reset := FALSE;
    fbUnexpectedFeedback();
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbUnexpectedFeedback.runCmd,
                      Message := 'UnexpectedFeedback#6 runCmd');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbUnexpectedFeedback.fault, Message := 'UnexpectedFeedback#6 fault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbUnexpectedFeedback.status.running,
                      Message := 'UnexpectedFeedback#6 status.running');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbUnexpectedFeedback.status.fault,
                      Message := 'UnexpectedFeedback#6 status.fault');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbUnexpectedFeedback.status.autoMode,
                      Message := 'UnexpectedFeedback#6 status.autoMode');
    AssertEquals_INT(Expected := 0,
                     Actual := fbUnexpectedFeedback.status.faultCode,
                     Message := 'UnexpectedFeedback#6 status.faultCode');
    AssertEquals_DINT(Expected := 1,
                      Actual := fbUnexpectedFeedback.status.startCount,
                      Message := 'UnexpectedFeedback#6 status.startCount');

    // #7, t = 6000 мс — работает
    GVL_S7Clock.tSimNow := T#6000MS;
    fbUnexpectedFeedback.feedback := TRUE;
    fbUnexpectedFeedback();
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbUnexpectedFeedback.runCmd,
                      Message := 'UnexpectedFeedback#7 runCmd');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbUnexpectedFeedback.fault, Message := 'UnexpectedFeedback#7 fault');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbUnexpectedFeedback.status.running,
                      Message := 'UnexpectedFeedback#7 status.running');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbUnexpectedFeedback.status.fault,
                      Message := 'UnexpectedFeedback#7 status.fault');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbUnexpectedFeedback.status.autoMode,
                      Message := 'UnexpectedFeedback#7 status.autoMode');
    AssertEquals_INT(Expected := 0,
                     Actual := fbUnexpectedFeedback.status.faultCode,
                     Message := 'UnexpectedFeedback#7 status.faultCode');
    AssertEquals_DINT(Expected := 1,
                      Actual := fbUnexpectedFeedback.status.startCount,
                      Message := 'UnexpectedFeedback#7 status.startCount');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
