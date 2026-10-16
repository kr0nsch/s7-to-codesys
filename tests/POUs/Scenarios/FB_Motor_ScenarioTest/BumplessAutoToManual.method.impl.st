// AUTO-GENERATED — не редактировать: scenarios/FB_Motor.csv, сценарий BumplessAutoToManual
coUnit.TEST('BumplessAutoToManual');
IF NOT xBumplessAutoToManualDone THEN
    xBumplessAutoToManualDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;

    // #1, t = 0 мс — авто, пуск №1
    GVL_S7Clock.tSimNow := T#0MS;
    fbBumplessAutoToManual.autoMode := TRUE;
    fbBumplessAutoToManual.autoStart := TRUE;
    fbBumplessAutoToManual.manStart := FALSE;
    fbBumplessAutoToManual.manStop := FALSE;
    fbBumplessAutoToManual.feedback := FALSE;
    fbBumplessAutoToManual.thermalOk := TRUE;
    fbBumplessAutoToManual.reset := FALSE;
    fbBumplessAutoToManual.feedbackTime := T#3000MS;
    fbBumplessAutoToManual();
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbBumplessAutoToManual.runCmd,
                      Message := 'BumplessAutoToManual#1 runCmd');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbBumplessAutoToManual.fault,
                      Message := 'BumplessAutoToManual#1 fault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbBumplessAutoToManual.status.running,
                      Message := 'BumplessAutoToManual#1 status.running');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbBumplessAutoToManual.status.fault,
                      Message := 'BumplessAutoToManual#1 status.fault');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbBumplessAutoToManual.status.autoMode,
                      Message := 'BumplessAutoToManual#1 status.autoMode');
    AssertEquals_INT(Expected := 0,
                     Actual := fbBumplessAutoToManual.status.faultCode,
                     Message := 'BumplessAutoToManual#1 status.faultCode');
    AssertEquals_DINT(Expected := 1,
                      Actual := fbBumplessAutoToManual.status.startCount,
                      Message := 'BumplessAutoToManual#1 status.startCount');

    // #2, t = 500 мс — работает
    GVL_S7Clock.tSimNow := T#500MS;
    fbBumplessAutoToManual.feedback := TRUE;
    fbBumplessAutoToManual();
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbBumplessAutoToManual.runCmd,
                      Message := 'BumplessAutoToManual#2 runCmd');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbBumplessAutoToManual.fault,
                      Message := 'BumplessAutoToManual#2 fault');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbBumplessAutoToManual.status.running,
                      Message := 'BumplessAutoToManual#2 status.running');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbBumplessAutoToManual.status.fault,
                      Message := 'BumplessAutoToManual#2 status.fault');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbBumplessAutoToManual.status.autoMode,
                      Message := 'BumplessAutoToManual#2 status.autoMode');
    AssertEquals_INT(Expected := 0,
                     Actual := fbBumplessAutoToManual.status.faultCode,
                     Message := 'BumplessAutoToManual#2 status.faultCode');
    AssertEquals_DINT(Expected := 1,
                      Actual := fbBumplessAutoToManual.status.startCount,
                      Message := 'BumplessAutoToManual#2 status.startCount');

    // #3, t = 1000 мс — в ручной: защёлка следила за авто — продолжает работать
    GVL_S7Clock.tSimNow := T#1000MS;
    fbBumplessAutoToManual.autoMode := FALSE;
    fbBumplessAutoToManual();
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbBumplessAutoToManual.runCmd,
                      Message := 'BumplessAutoToManual#3 runCmd');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbBumplessAutoToManual.fault,
                      Message := 'BumplessAutoToManual#3 fault');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbBumplessAutoToManual.status.running,
                      Message := 'BumplessAutoToManual#3 status.running');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbBumplessAutoToManual.status.fault,
                      Message := 'BumplessAutoToManual#3 status.fault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbBumplessAutoToManual.status.autoMode,
                      Message := 'BumplessAutoToManual#3 status.autoMode');
    AssertEquals_INT(Expected := 0,
                     Actual := fbBumplessAutoToManual.status.faultCode,
                     Message := 'BumplessAutoToManual#3 status.faultCode');
    AssertEquals_DINT(Expected := 1,
                      Actual := fbBumplessAutoToManual.status.startCount,
                      Message := 'BumplessAutoToManual#3 status.startCount');

    // #4, t = 2000 мс — стоп оператором
    GVL_S7Clock.tSimNow := T#2000MS;
    fbBumplessAutoToManual.manStop := TRUE;
    fbBumplessAutoToManual();
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbBumplessAutoToManual.runCmd,
                      Message := 'BumplessAutoToManual#4 runCmd');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbBumplessAutoToManual.fault,
                      Message := 'BumplessAutoToManual#4 fault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbBumplessAutoToManual.status.running,
                      Message := 'BumplessAutoToManual#4 status.running');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbBumplessAutoToManual.status.fault,
                      Message := 'BumplessAutoToManual#4 status.fault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbBumplessAutoToManual.status.autoMode,
                      Message := 'BumplessAutoToManual#4 status.autoMode');
    AssertEquals_INT(Expected := 0,
                     Actual := fbBumplessAutoToManual.status.faultCode,
                     Message := 'BumplessAutoToManual#4 status.faultCode');
    AssertEquals_DINT(Expected := 1,
                      Actual := fbBumplessAutoToManual.status.startCount,
                      Message := 'BumplessAutoToManual#4 status.startCount');

    // #5, t = 2500 мс — остановлен
    GVL_S7Clock.tSimNow := T#2500MS;
    fbBumplessAutoToManual.manStop := FALSE;
    fbBumplessAutoToManual.feedback := FALSE;
    fbBumplessAutoToManual();
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbBumplessAutoToManual.runCmd,
                      Message := 'BumplessAutoToManual#5 runCmd');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbBumplessAutoToManual.fault,
                      Message := 'BumplessAutoToManual#5 fault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbBumplessAutoToManual.status.running,
                      Message := 'BumplessAutoToManual#5 status.running');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbBumplessAutoToManual.status.fault,
                      Message := 'BumplessAutoToManual#5 status.fault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbBumplessAutoToManual.status.autoMode,
                      Message := 'BumplessAutoToManual#5 status.autoMode');
    AssertEquals_INT(Expected := 0,
                     Actual := fbBumplessAutoToManual.status.faultCode,
                     Message := 'BumplessAutoToManual#5 status.faultCode');
    AssertEquals_DINT(Expected := 1,
                      Actual := fbBumplessAutoToManual.status.startCount,
                      Message := 'BumplessAutoToManual#5 status.startCount');

    // #6, t = 3000 мс — в авто без запроса
    GVL_S7Clock.tSimNow := T#3000MS;
    fbBumplessAutoToManual.autoMode := TRUE;
    fbBumplessAutoToManual.autoStart := FALSE;
    fbBumplessAutoToManual();
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbBumplessAutoToManual.runCmd,
                      Message := 'BumplessAutoToManual#6 runCmd');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbBumplessAutoToManual.fault,
                      Message := 'BumplessAutoToManual#6 fault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbBumplessAutoToManual.status.running,
                      Message := 'BumplessAutoToManual#6 status.running');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbBumplessAutoToManual.status.fault,
                      Message := 'BumplessAutoToManual#6 status.fault');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbBumplessAutoToManual.status.autoMode,
                      Message := 'BumplessAutoToManual#6 status.autoMode');
    AssertEquals_INT(Expected := 0,
                     Actual := fbBumplessAutoToManual.status.faultCode,
                     Message := 'BumplessAutoToManual#6 status.faultCode');
    AssertEquals_DINT(Expected := 1,
                      Actual := fbBumplessAutoToManual.status.startCount,
                      Message := 'BumplessAutoToManual#6 status.startCount');

    // #7, t = 3500 мс — запрос авто: пуск №2
    GVL_S7Clock.tSimNow := T#3500MS;
    fbBumplessAutoToManual.autoStart := TRUE;
    fbBumplessAutoToManual();
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbBumplessAutoToManual.runCmd,
                      Message := 'BumplessAutoToManual#7 runCmd');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbBumplessAutoToManual.fault,
                      Message := 'BumplessAutoToManual#7 fault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbBumplessAutoToManual.status.running,
                      Message := 'BumplessAutoToManual#7 status.running');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbBumplessAutoToManual.status.fault,
                      Message := 'BumplessAutoToManual#7 status.fault');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbBumplessAutoToManual.status.autoMode,
                      Message := 'BumplessAutoToManual#7 status.autoMode');
    AssertEquals_INT(Expected := 0,
                     Actual := fbBumplessAutoToManual.status.faultCode,
                     Message := 'BumplessAutoToManual#7 status.faultCode');
    AssertEquals_DINT(Expected := 2,
                      Actual := fbBumplessAutoToManual.status.startCount,
                      Message := 'BumplessAutoToManual#7 status.startCount');

    // #8, t = 4000 мс — работает
    GVL_S7Clock.tSimNow := T#4000MS;
    fbBumplessAutoToManual.feedback := TRUE;
    fbBumplessAutoToManual();
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbBumplessAutoToManual.runCmd,
                      Message := 'BumplessAutoToManual#8 runCmd');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbBumplessAutoToManual.fault,
                      Message := 'BumplessAutoToManual#8 fault');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbBumplessAutoToManual.status.running,
                      Message := 'BumplessAutoToManual#8 status.running');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbBumplessAutoToManual.status.fault,
                      Message := 'BumplessAutoToManual#8 status.fault');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbBumplessAutoToManual.status.autoMode,
                      Message := 'BumplessAutoToManual#8 status.autoMode');
    AssertEquals_INT(Expected := 0,
                     Actual := fbBumplessAutoToManual.status.faultCode,
                     Message := 'BumplessAutoToManual#8 status.faultCode');
    AssertEquals_DINT(Expected := 2,
                      Actual := fbBumplessAutoToManual.status.startCount,
                      Message := 'BumplessAutoToManual#8 status.startCount');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
