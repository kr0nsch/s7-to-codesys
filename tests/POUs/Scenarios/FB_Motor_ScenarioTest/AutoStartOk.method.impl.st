// AUTO-GENERATED — не редактировать: scenarios/FB_Motor.csv, сценарий AutoStartOk
coUnit.TEST('AutoStartOk');
IF NOT xAutoStartOkDone THEN
    xAutoStartOkDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;

    // #1, t = 0 мс — авто, команды нет
    GVL_S7Clock.tSimNow := T#0MS;
    fbAutoStartOk.autoMode := TRUE;
    fbAutoStartOk.autoStart := FALSE;
    fbAutoStartOk.manStart := FALSE;
    fbAutoStartOk.manStop := FALSE;
    fbAutoStartOk.feedback := FALSE;
    fbAutoStartOk.thermalOk := TRUE;
    fbAutoStartOk.reset := FALSE;
    fbAutoStartOk.feedbackTime := T#3000MS;
    fbAutoStartOk();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAutoStartOk.runCmd, Message := 'AutoStartOk#1 runCmd');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAutoStartOk.fault, Message := 'AutoStartOk#1 fault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbAutoStartOk.status.running,
                      Message := 'AutoStartOk#1 status.running');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAutoStartOk.status.fault, Message := 'AutoStartOk#1 status.fault');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbAutoStartOk.status.autoMode,
                      Message := 'AutoStartOk#1 status.autoMode');
    AssertEquals_INT(Expected := 0,
                     Actual := fbAutoStartOk.status.faultCode,
                     Message := 'AutoStartOk#1 status.faultCode');
    AssertEquals_DINT(Expected := 0,
                      Actual := fbAutoStartOk.status.startCount,
                      Message := 'AutoStartOk#1 status.startCount');

    // #2, t = 100 мс — пуск: runCmd, пуск №1; таймер рассогласования запущен
    GVL_S7Clock.tSimNow := T#100MS;
    fbAutoStartOk.autoStart := TRUE;
    fbAutoStartOk();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbAutoStartOk.runCmd, Message := 'AutoStartOk#2 runCmd');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAutoStartOk.fault, Message := 'AutoStartOk#2 fault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbAutoStartOk.status.running,
                      Message := 'AutoStartOk#2 status.running');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAutoStartOk.status.fault, Message := 'AutoStartOk#2 status.fault');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbAutoStartOk.status.autoMode,
                      Message := 'AutoStartOk#2 status.autoMode');
    AssertEquals_INT(Expected := 0,
                     Actual := fbAutoStartOk.status.faultCode,
                     Message := 'AutoStartOk#2 status.faultCode');
    AssertEquals_DINT(Expected := 1,
                      Actual := fbAutoStartOk.status.startCount,
                      Message := 'AutoStartOk#2 status.startCount');

    // #3, t = 1100 мс — обратная связь через 1 с: работает
    GVL_S7Clock.tSimNow := T#1100MS;
    fbAutoStartOk.feedback := TRUE;
    fbAutoStartOk();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbAutoStartOk.runCmd, Message := 'AutoStartOk#3 runCmd');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAutoStartOk.fault, Message := 'AutoStartOk#3 fault');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbAutoStartOk.status.running,
                      Message := 'AutoStartOk#3 status.running');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAutoStartOk.status.fault, Message := 'AutoStartOk#3 status.fault');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbAutoStartOk.status.autoMode,
                      Message := 'AutoStartOk#3 status.autoMode');
    AssertEquals_INT(Expected := 0,
                     Actual := fbAutoStartOk.status.faultCode,
                     Message := 'AutoStartOk#3 status.faultCode');
    AssertEquals_DINT(Expected := 1,
                      Actual := fbAutoStartOk.status.startCount,
                      Message := 'AutoStartOk#3 status.startCount');

    // #4, t = 5000 мс — работает, аварии нет
    GVL_S7Clock.tSimNow := T#5000MS;
    fbAutoStartOk();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbAutoStartOk.runCmd, Message := 'AutoStartOk#4 runCmd');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAutoStartOk.fault, Message := 'AutoStartOk#4 fault');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbAutoStartOk.status.running,
                      Message := 'AutoStartOk#4 status.running');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAutoStartOk.status.fault, Message := 'AutoStartOk#4 status.fault');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbAutoStartOk.status.autoMode,
                      Message := 'AutoStartOk#4 status.autoMode');
    AssertEquals_INT(Expected := 0,
                     Actual := fbAutoStartOk.status.faultCode,
                     Message := 'AutoStartOk#4 status.faultCode');
    AssertEquals_DINT(Expected := 1,
                      Actual := fbAutoStartOk.status.startCount,
                      Message := 'AutoStartOk#4 status.startCount');

    // #5, t = 5100 мс — стоп: runCmd снят, контактор ещё держит — рассогласование
    GVL_S7Clock.tSimNow := T#5100MS;
    fbAutoStartOk.autoStart := FALSE;
    fbAutoStartOk();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAutoStartOk.runCmd, Message := 'AutoStartOk#5 runCmd');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAutoStartOk.fault, Message := 'AutoStartOk#5 fault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbAutoStartOk.status.running,
                      Message := 'AutoStartOk#5 status.running');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAutoStartOk.status.fault, Message := 'AutoStartOk#5 status.fault');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbAutoStartOk.status.autoMode,
                      Message := 'AutoStartOk#5 status.autoMode');
    AssertEquals_INT(Expected := 0,
                     Actual := fbAutoStartOk.status.faultCode,
                     Message := 'AutoStartOk#5 status.faultCode');
    AssertEquals_DINT(Expected := 1,
                      Actual := fbAutoStartOk.status.startCount,
                      Message := 'AutoStartOk#5 status.startCount');

    // #6, t = 6000 мс — обратная связь пропала через 0.9 с — нормальный останов
    GVL_S7Clock.tSimNow := T#6000MS;
    fbAutoStartOk.feedback := FALSE;
    fbAutoStartOk();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAutoStartOk.runCmd, Message := 'AutoStartOk#6 runCmd');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAutoStartOk.fault, Message := 'AutoStartOk#6 fault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbAutoStartOk.status.running,
                      Message := 'AutoStartOk#6 status.running');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAutoStartOk.status.fault, Message := 'AutoStartOk#6 status.fault');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbAutoStartOk.status.autoMode,
                      Message := 'AutoStartOk#6 status.autoMode');
    AssertEquals_INT(Expected := 0,
                     Actual := fbAutoStartOk.status.faultCode,
                     Message := 'AutoStartOk#6 status.faultCode');
    AssertEquals_DINT(Expected := 1,
                      Actual := fbAutoStartOk.status.startCount,
                      Message := 'AutoStartOk#6 status.startCount');

    // #7, t = 9500 мс — покой
    GVL_S7Clock.tSimNow := T#9500MS;
    fbAutoStartOk();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAutoStartOk.runCmd, Message := 'AutoStartOk#7 runCmd');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAutoStartOk.fault, Message := 'AutoStartOk#7 fault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbAutoStartOk.status.running,
                      Message := 'AutoStartOk#7 status.running');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAutoStartOk.status.fault, Message := 'AutoStartOk#7 status.fault');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbAutoStartOk.status.autoMode,
                      Message := 'AutoStartOk#7 status.autoMode');
    AssertEquals_INT(Expected := 0,
                     Actual := fbAutoStartOk.status.faultCode,
                     Message := 'AutoStartOk#7 status.faultCode');
    AssertEquals_DINT(Expected := 1,
                      Actual := fbAutoStartOk.status.startCount,
                      Message := 'AutoStartOk#7 status.startCount');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
