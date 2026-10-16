// AUTO-GENERATED — не редактировать: scenarios/FB_AlarmDelay.csv, сценарий AckHeldDuringActivation
coUnit.TEST('AckHeldDuringActivation');
IF NOT xAckHeldDuringActivationDone THEN
    xAckHeldDuringActivationDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;

    // #1, t = 0 мс — условие; кнопка нажата заранее — фронт ack до появления
    GVL_S7Clock.tSimNow := T#0MS;
    fbAckHeldDuringActivation.condition := TRUE;
    fbAckHeldDuringActivation.enable := TRUE;
    fbAckHeldDuringActivation.ack := TRUE;
    fbAckHeldDuringActivation.onDelay := T#5000MS;
    fbAckHeldDuringActivation.offDelay := T#2000MS;
    fbAckHeldDuringActivation();
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbAckHeldDuringActivation.active,
                      Message := 'AckHeldDuringActivation#1 active');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbAckHeldDuringActivation.unacked,
                      Message := 'AckHeldDuringActivation#1 unacked');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbAckHeldDuringActivation.alarm,
                      Message := 'AckHeldDuringActivation#1 alarm');
    AssertEquals_INT(Expected := 0,
                     Actual := fbAckHeldDuringActivation.state,
                     Message := 'AckHeldDuringActivation#1 state');
    AssertEquals_DINT(Expected := 0,
                      Actual := fbAckHeldDuringActivation.count,
                      Message := 'AckHeldDuringActivation#1 count');

    // #2, t = 5200 мс — появление №1 при удерживаемой кнопке: не квитирован
    GVL_S7Clock.tSimNow := T#5200MS;
    fbAckHeldDuringActivation();
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbAckHeldDuringActivation.active,
                      Message := 'AckHeldDuringActivation#2 active');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbAckHeldDuringActivation.unacked,
                      Message := 'AckHeldDuringActivation#2 unacked');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbAckHeldDuringActivation.alarm,
                      Message := 'AckHeldDuringActivation#2 alarm');
    AssertEquals_INT(Expected := 1,
                     Actual := fbAckHeldDuringActivation.state,
                     Message := 'AckHeldDuringActivation#2 state');
    AssertEquals_DINT(Expected := 1,
                      Actual := fbAckHeldDuringActivation.count,
                      Message := 'AckHeldDuringActivation#2 count');

    // #3, t = 5400 мс — кнопка всё ещё нажата, фронта нет: не квитирован
    GVL_S7Clock.tSimNow := T#5400MS;
    fbAckHeldDuringActivation();
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbAckHeldDuringActivation.active,
                      Message := 'AckHeldDuringActivation#3 active');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbAckHeldDuringActivation.unacked,
                      Message := 'AckHeldDuringActivation#3 unacked');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbAckHeldDuringActivation.alarm,
                      Message := 'AckHeldDuringActivation#3 alarm');
    AssertEquals_INT(Expected := 1,
                     Actual := fbAckHeldDuringActivation.state,
                     Message := 'AckHeldDuringActivation#3 state');
    AssertEquals_DINT(Expected := 1,
                      Actual := fbAckHeldDuringActivation.count,
                      Message := 'AckHeldDuringActivation#3 count');

    // #4, t = 5600 мс — кнопка отпущена
    GVL_S7Clock.tSimNow := T#5600MS;
    fbAckHeldDuringActivation.ack := FALSE;
    fbAckHeldDuringActivation();
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbAckHeldDuringActivation.active,
                      Message := 'AckHeldDuringActivation#4 active');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbAckHeldDuringActivation.unacked,
                      Message := 'AckHeldDuringActivation#4 unacked');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbAckHeldDuringActivation.alarm,
                      Message := 'AckHeldDuringActivation#4 alarm');
    AssertEquals_INT(Expected := 1,
                     Actual := fbAckHeldDuringActivation.state,
                     Message := 'AckHeldDuringActivation#4 state');
    AssertEquals_DINT(Expected := 1,
                      Actual := fbAckHeldDuringActivation.count,
                      Message := 'AckHeldDuringActivation#4 count');

    // #5, t = 5800 мс — новый фронт: квитирован
    GVL_S7Clock.tSimNow := T#5800MS;
    fbAckHeldDuringActivation.ack := TRUE;
    fbAckHeldDuringActivation();
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbAckHeldDuringActivation.active,
                      Message := 'AckHeldDuringActivation#5 active');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbAckHeldDuringActivation.unacked,
                      Message := 'AckHeldDuringActivation#5 unacked');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbAckHeldDuringActivation.alarm,
                      Message := 'AckHeldDuringActivation#5 alarm');
    AssertEquals_INT(Expected := 2,
                     Actual := fbAckHeldDuringActivation.state,
                     Message := 'AckHeldDuringActivation#5 state');
    AssertEquals_DINT(Expected := 1,
                      Actual := fbAckHeldDuringActivation.count,
                      Message := 'AckHeldDuringActivation#5 count');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
