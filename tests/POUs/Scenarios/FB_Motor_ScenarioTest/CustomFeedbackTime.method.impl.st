// AUTO-GENERATED — не редактировать: scenarios/FB_Motor.csv, сценарий CustomFeedbackTime
coUnit.TEST('CustomFeedbackTime');
IF NOT xCustomFeedbackTimeDone THEN
    xCustomFeedbackTimeDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;

    // #1, t = 0 мс — пуск, feedbackTime 5 с
    GVL_S7Clock.tSimNow := T#0MS;
    fbCustomFeedbackTime.autoMode := TRUE;
    fbCustomFeedbackTime.autoStart := TRUE;
    fbCustomFeedbackTime.manStart := FALSE;
    fbCustomFeedbackTime.manStop := FALSE;
    fbCustomFeedbackTime.feedback := FALSE;
    fbCustomFeedbackTime.thermalOk := TRUE;
    fbCustomFeedbackTime.reset := FALSE;
    fbCustomFeedbackTime.feedbackTime := T#5000MS;
    fbCustomFeedbackTime();
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbCustomFeedbackTime.runCmd,
                      Message := 'CustomFeedbackTime#1 runCmd');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCustomFeedbackTime.fault, Message := 'CustomFeedbackTime#1 fault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbCustomFeedbackTime.status.running,
                      Message := 'CustomFeedbackTime#1 status.running');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbCustomFeedbackTime.status.fault,
                      Message := 'CustomFeedbackTime#1 status.fault');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbCustomFeedbackTime.status.autoMode,
                      Message := 'CustomFeedbackTime#1 status.autoMode');
    AssertEquals_INT(Expected := 0,
                     Actual := fbCustomFeedbackTime.status.faultCode,
                     Message := 'CustomFeedbackTime#1 status.faultCode');
    AssertEquals_DINT(Expected := 1,
                      Actual := fbCustomFeedbackTime.status.startCount,
                      Message := 'CustomFeedbackTime#1 status.startCount');

    // #2, t = 4500 мс — обратная связь через 4.5 с — аварии нет
    GVL_S7Clock.tSimNow := T#4500MS;
    fbCustomFeedbackTime.feedback := TRUE;
    fbCustomFeedbackTime();
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbCustomFeedbackTime.runCmd,
                      Message := 'CustomFeedbackTime#2 runCmd');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCustomFeedbackTime.fault, Message := 'CustomFeedbackTime#2 fault');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbCustomFeedbackTime.status.running,
                      Message := 'CustomFeedbackTime#2 status.running');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbCustomFeedbackTime.status.fault,
                      Message := 'CustomFeedbackTime#2 status.fault');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbCustomFeedbackTime.status.autoMode,
                      Message := 'CustomFeedbackTime#2 status.autoMode');
    AssertEquals_INT(Expected := 0,
                     Actual := fbCustomFeedbackTime.status.faultCode,
                     Message := 'CustomFeedbackTime#2 status.faultCode');
    AssertEquals_DINT(Expected := 1,
                      Actual := fbCustomFeedbackTime.status.startCount,
                      Message := 'CustomFeedbackTime#2 status.startCount');

    // #3, t = 6000 мс — работает
    GVL_S7Clock.tSimNow := T#6000MS;
    fbCustomFeedbackTime();
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbCustomFeedbackTime.runCmd,
                      Message := 'CustomFeedbackTime#3 runCmd');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCustomFeedbackTime.fault, Message := 'CustomFeedbackTime#3 fault');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbCustomFeedbackTime.status.running,
                      Message := 'CustomFeedbackTime#3 status.running');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbCustomFeedbackTime.status.fault,
                      Message := 'CustomFeedbackTime#3 status.fault');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbCustomFeedbackTime.status.autoMode,
                      Message := 'CustomFeedbackTime#3 status.autoMode');
    AssertEquals_INT(Expected := 0,
                     Actual := fbCustomFeedbackTime.status.faultCode,
                     Message := 'CustomFeedbackTime#3 status.faultCode');
    AssertEquals_DINT(Expected := 1,
                      Actual := fbCustomFeedbackTime.status.startCount,
                      Message := 'CustomFeedbackTime#3 status.startCount');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
