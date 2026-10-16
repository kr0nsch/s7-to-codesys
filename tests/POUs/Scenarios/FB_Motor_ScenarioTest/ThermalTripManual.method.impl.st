// AUTO-GENERATED — не редактировать: scenarios/FB_Motor.csv, сценарий ThermalTripManual
coUnit.TEST('ThermalTripManual');
IF NOT xThermalTripManualDone THEN
    xThermalTripManualDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;

    // #1, t = 0 мс — ручной режим, покой
    GVL_S7Clock.tSimNow := T#0MS;
    fbThermalTripManual.autoMode := FALSE;
    fbThermalTripManual.autoStart := FALSE;
    fbThermalTripManual.manStart := FALSE;
    fbThermalTripManual.manStop := FALSE;
    fbThermalTripManual.feedback := FALSE;
    fbThermalTripManual.thermalOk := TRUE;
    fbThermalTripManual.reset := FALSE;
    fbThermalTripManual.feedbackTime := T#3000MS;
    fbThermalTripManual();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbThermalTripManual.runCmd, Message := 'ThermalTripManual#1 runCmd');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbThermalTripManual.fault, Message := 'ThermalTripManual#1 fault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbThermalTripManual.status.running,
                      Message := 'ThermalTripManual#1 status.running');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbThermalTripManual.status.fault,
                      Message := 'ThermalTripManual#1 status.fault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbThermalTripManual.status.autoMode,
                      Message := 'ThermalTripManual#1 status.autoMode');
    AssertEquals_INT(Expected := 0,
                     Actual := fbThermalTripManual.status.faultCode,
                     Message := 'ThermalTripManual#1 status.faultCode');
    AssertEquals_DINT(Expected := 0,
                      Actual := fbThermalTripManual.status.startCount,
                      Message := 'ThermalTripManual#1 status.startCount');

    // #2, t = 100 мс — пуск оператором: пуск №1
    GVL_S7Clock.tSimNow := T#100MS;
    fbThermalTripManual.manStart := TRUE;
    fbThermalTripManual();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbThermalTripManual.runCmd, Message := 'ThermalTripManual#2 runCmd');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbThermalTripManual.fault, Message := 'ThermalTripManual#2 fault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbThermalTripManual.status.running,
                      Message := 'ThermalTripManual#2 status.running');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbThermalTripManual.status.fault,
                      Message := 'ThermalTripManual#2 status.fault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbThermalTripManual.status.autoMode,
                      Message := 'ThermalTripManual#2 status.autoMode');
    AssertEquals_INT(Expected := 0,
                     Actual := fbThermalTripManual.status.faultCode,
                     Message := 'ThermalTripManual#2 status.faultCode');
    AssertEquals_DINT(Expected := 1,
                      Actual := fbThermalTripManual.status.startCount,
                      Message := 'ThermalTripManual#2 status.startCount');

    // #3, t = 200 мс — работает
    GVL_S7Clock.tSimNow := T#200MS;
    fbThermalTripManual.manStart := FALSE;
    fbThermalTripManual.feedback := TRUE;
    fbThermalTripManual();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbThermalTripManual.runCmd, Message := 'ThermalTripManual#3 runCmd');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbThermalTripManual.fault, Message := 'ThermalTripManual#3 fault');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbThermalTripManual.status.running,
                      Message := 'ThermalTripManual#3 status.running');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbThermalTripManual.status.fault,
                      Message := 'ThermalTripManual#3 status.fault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbThermalTripManual.status.autoMode,
                      Message := 'ThermalTripManual#3 status.autoMode');
    AssertEquals_INT(Expected := 0,
                     Actual := fbThermalTripManual.status.faultCode,
                     Message := 'ThermalTripManual#3 status.faultCode');
    AssertEquals_DINT(Expected := 1,
                      Actual := fbThermalTripManual.status.startCount,
                      Message := 'ThermalTripManual#3 status.startCount');

    // #4, t = 1000 мс — тепловая защита: авария 3, ручная защёлка сброшена
    GVL_S7Clock.tSimNow := T#1000MS;
    fbThermalTripManual.thermalOk := FALSE;
    fbThermalTripManual();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbThermalTripManual.runCmd, Message := 'ThermalTripManual#4 runCmd');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbThermalTripManual.fault, Message := 'ThermalTripManual#4 fault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbThermalTripManual.status.running,
                      Message := 'ThermalTripManual#4 status.running');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbThermalTripManual.status.fault,
                      Message := 'ThermalTripManual#4 status.fault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbThermalTripManual.status.autoMode,
                      Message := 'ThermalTripManual#4 status.autoMode');
    AssertEquals_INT(Expected := 3,
                     Actual := fbThermalTripManual.status.faultCode,
                     Message := 'ThermalTripManual#4 status.faultCode');
    AssertEquals_DINT(Expected := 1,
                      Actual := fbThermalTripManual.status.startCount,
                      Message := 'ThermalTripManual#4 status.startCount');

    // #5, t = 1500 мс — контактор отпал
    GVL_S7Clock.tSimNow := T#1500MS;
    fbThermalTripManual.feedback := FALSE;
    fbThermalTripManual();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbThermalTripManual.runCmd, Message := 'ThermalTripManual#5 runCmd');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbThermalTripManual.fault, Message := 'ThermalTripManual#5 fault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbThermalTripManual.status.running,
                      Message := 'ThermalTripManual#5 status.running');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbThermalTripManual.status.fault,
                      Message := 'ThermalTripManual#5 status.fault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbThermalTripManual.status.autoMode,
                      Message := 'ThermalTripManual#5 status.autoMode');
    AssertEquals_INT(Expected := 3,
                     Actual := fbThermalTripManual.status.faultCode,
                     Message := 'ThermalTripManual#5 status.faultCode');
    AssertEquals_DINT(Expected := 1,
                      Actual := fbThermalTripManual.status.startCount,
                      Message := 'ThermalTripManual#5 status.startCount');

    // #6, t = 2000 мс — сброс при сработавшем реле не действует
    GVL_S7Clock.tSimNow := T#2000MS;
    fbThermalTripManual.reset := TRUE;
    fbThermalTripManual();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbThermalTripManual.runCmd, Message := 'ThermalTripManual#6 runCmd');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbThermalTripManual.fault, Message := 'ThermalTripManual#6 fault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbThermalTripManual.status.running,
                      Message := 'ThermalTripManual#6 status.running');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbThermalTripManual.status.fault,
                      Message := 'ThermalTripManual#6 status.fault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbThermalTripManual.status.autoMode,
                      Message := 'ThermalTripManual#6 status.autoMode');
    AssertEquals_INT(Expected := 3,
                     Actual := fbThermalTripManual.status.faultCode,
                     Message := 'ThermalTripManual#6 status.faultCode');
    AssertEquals_DINT(Expected := 1,
                      Actual := fbThermalTripManual.status.startCount,
                      Message := 'ThermalTripManual#6 status.startCount');

    // #7, t = 2500 мс — реле вернулось, авария держится до сброса
    GVL_S7Clock.tSimNow := T#2500MS;
    fbThermalTripManual.thermalOk := TRUE;
    fbThermalTripManual.reset := FALSE;
    fbThermalTripManual();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbThermalTripManual.runCmd, Message := 'ThermalTripManual#7 runCmd');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbThermalTripManual.fault, Message := 'ThermalTripManual#7 fault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbThermalTripManual.status.running,
                      Message := 'ThermalTripManual#7 status.running');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbThermalTripManual.status.fault,
                      Message := 'ThermalTripManual#7 status.fault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbThermalTripManual.status.autoMode,
                      Message := 'ThermalTripManual#7 status.autoMode');
    AssertEquals_INT(Expected := 3,
                     Actual := fbThermalTripManual.status.faultCode,
                     Message := 'ThermalTripManual#7 status.faultCode');
    AssertEquals_DINT(Expected := 1,
                      Actual := fbThermalTripManual.status.startCount,
                      Message := 'ThermalTripManual#7 status.startCount');

    // #8, t = 3000 мс — сброс: авария снята, насос не стартует сам
    GVL_S7Clock.tSimNow := T#3000MS;
    fbThermalTripManual.reset := TRUE;
    fbThermalTripManual();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbThermalTripManual.runCmd, Message := 'ThermalTripManual#8 runCmd');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbThermalTripManual.fault, Message := 'ThermalTripManual#8 fault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbThermalTripManual.status.running,
                      Message := 'ThermalTripManual#8 status.running');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbThermalTripManual.status.fault,
                      Message := 'ThermalTripManual#8 status.fault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbThermalTripManual.status.autoMode,
                      Message := 'ThermalTripManual#8 status.autoMode');
    AssertEquals_INT(Expected := 0,
                     Actual := fbThermalTripManual.status.faultCode,
                     Message := 'ThermalTripManual#8 status.faultCode');
    AssertEquals_DINT(Expected := 1,
                      Actual := fbThermalTripManual.status.startCount,
                      Message := 'ThermalTripManual#8 status.startCount');

    // #9, t = 3500 мс — новый пуск оператором: пуск №2
    GVL_S7Clock.tSimNow := T#3500MS;
    fbThermalTripManual.manStart := TRUE;
    fbThermalTripManual.reset := FALSE;
    fbThermalTripManual();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbThermalTripManual.runCmd, Message := 'ThermalTripManual#9 runCmd');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbThermalTripManual.fault, Message := 'ThermalTripManual#9 fault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbThermalTripManual.status.running,
                      Message := 'ThermalTripManual#9 status.running');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbThermalTripManual.status.fault,
                      Message := 'ThermalTripManual#9 status.fault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbThermalTripManual.status.autoMode,
                      Message := 'ThermalTripManual#9 status.autoMode');
    AssertEquals_INT(Expected := 0,
                     Actual := fbThermalTripManual.status.faultCode,
                     Message := 'ThermalTripManual#9 status.faultCode');
    AssertEquals_DINT(Expected := 2,
                      Actual := fbThermalTripManual.status.startCount,
                      Message := 'ThermalTripManual#9 status.startCount');

    // #10, t = 3600 мс — стоп и пуск одновременно: стоп приоритетнее
    GVL_S7Clock.tSimNow := T#3600MS;
    fbThermalTripManual.manStop := TRUE;
    fbThermalTripManual();
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbThermalTripManual.runCmd,
                      Message := 'ThermalTripManual#10 runCmd');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbThermalTripManual.fault, Message := 'ThermalTripManual#10 fault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbThermalTripManual.status.running,
                      Message := 'ThermalTripManual#10 status.running');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbThermalTripManual.status.fault,
                      Message := 'ThermalTripManual#10 status.fault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbThermalTripManual.status.autoMode,
                      Message := 'ThermalTripManual#10 status.autoMode');
    AssertEquals_INT(Expected := 0,
                     Actual := fbThermalTripManual.status.faultCode,
                     Message := 'ThermalTripManual#10 status.faultCode');
    AssertEquals_DINT(Expected := 2,
                      Actual := fbThermalTripManual.status.startCount,
                      Message := 'ThermalTripManual#10 status.startCount');

    // #11, t = 3700 мс — покой
    GVL_S7Clock.tSimNow := T#3700MS;
    fbThermalTripManual.manStart := FALSE;
    fbThermalTripManual.manStop := FALSE;
    fbThermalTripManual();
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbThermalTripManual.runCmd,
                      Message := 'ThermalTripManual#11 runCmd');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbThermalTripManual.fault, Message := 'ThermalTripManual#11 fault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbThermalTripManual.status.running,
                      Message := 'ThermalTripManual#11 status.running');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbThermalTripManual.status.fault,
                      Message := 'ThermalTripManual#11 status.fault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbThermalTripManual.status.autoMode,
                      Message := 'ThermalTripManual#11 status.autoMode');
    AssertEquals_INT(Expected := 0,
                     Actual := fbThermalTripManual.status.faultCode,
                     Message := 'ThermalTripManual#11 status.faultCode');
    AssertEquals_DINT(Expected := 2,
                      Actual := fbThermalTripManual.status.startCount,
                      Message := 'ThermalTripManual#11 status.startCount');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
