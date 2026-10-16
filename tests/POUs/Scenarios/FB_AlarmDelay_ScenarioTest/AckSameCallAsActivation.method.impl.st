// AUTO-GENERATED — не редактировать: scenarios/FB_AlarmDelay.csv, сценарий AckSameCallAsActivation
coUnit.TEST('AckSameCallAsActivation');
IF NOT xAckSameCallAsActivationDone THEN
    xAckSameCallAsActivationDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;

    // #1, t = 0 мс — условие
    GVL_S7Clock.tSimNow := T#0MS;
    fbAckSameCallAsActivation.condition := TRUE;
    fbAckSameCallAsActivation.enable := TRUE;
    fbAckSameCallAsActivation.ack := FALSE;
    fbAckSameCallAsActivation.onDelay := T#5000MS;
    fbAckSameCallAsActivation.offDelay := T#2000MS;
    fbAckSameCallAsActivation();
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbAckSameCallAsActivation.active,
                      Message := 'AckSameCallAsActivation#1 active');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbAckSameCallAsActivation.unacked,
                      Message := 'AckSameCallAsActivation#1 unacked');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbAckSameCallAsActivation.alarm,
                      Message := 'AckSameCallAsActivation#1 alarm');
    AssertEquals_INT(Expected := 0,
                     Actual := fbAckSameCallAsActivation.state,
                     Message := 'AckSameCallAsActivation#1 state');
    AssertEquals_DINT(Expected := 0,
                      Actual := fbAckSameCallAsActivation.count,
                      Message := 'AckSameCallAsActivation#1 count');

    // #2, t = 5200 мс — появление и фронт ack в одном вызове: не квитирован
    GVL_S7Clock.tSimNow := T#5200MS;
    fbAckSameCallAsActivation.ack := TRUE;
    fbAckSameCallAsActivation();
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbAckSameCallAsActivation.active,
                      Message := 'AckSameCallAsActivation#2 active');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbAckSameCallAsActivation.unacked,
                      Message := 'AckSameCallAsActivation#2 unacked');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbAckSameCallAsActivation.alarm,
                      Message := 'AckSameCallAsActivation#2 alarm');
    AssertEquals_INT(Expected := 1,
                     Actual := fbAckSameCallAsActivation.state,
                     Message := 'AckSameCallAsActivation#2 state');
    AssertEquals_DINT(Expected := 1,
                      Actual := fbAckSameCallAsActivation.count,
                      Message := 'AckSameCallAsActivation#2 count');

    // #3, t = 5400 мс — не квитирован
    GVL_S7Clock.tSimNow := T#5400MS;
    fbAckSameCallAsActivation.ack := FALSE;
    fbAckSameCallAsActivation();
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbAckSameCallAsActivation.active,
                      Message := 'AckSameCallAsActivation#3 active');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbAckSameCallAsActivation.unacked,
                      Message := 'AckSameCallAsActivation#3 unacked');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbAckSameCallAsActivation.alarm,
                      Message := 'AckSameCallAsActivation#3 alarm');
    AssertEquals_INT(Expected := 1,
                     Actual := fbAckSameCallAsActivation.state,
                     Message := 'AckSameCallAsActivation#3 state');
    AssertEquals_DINT(Expected := 1,
                      Actual := fbAckSameCallAsActivation.count,
                      Message := 'AckSameCallAsActivation#3 count');

    // #4, t = 5600 мс — квитирован
    GVL_S7Clock.tSimNow := T#5600MS;
    fbAckSameCallAsActivation.ack := TRUE;
    fbAckSameCallAsActivation();
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbAckSameCallAsActivation.active,
                      Message := 'AckSameCallAsActivation#4 active');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbAckSameCallAsActivation.unacked,
                      Message := 'AckSameCallAsActivation#4 unacked');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbAckSameCallAsActivation.alarm,
                      Message := 'AckSameCallAsActivation#4 alarm');
    AssertEquals_INT(Expected := 2,
                     Actual := fbAckSameCallAsActivation.state,
                     Message := 'AckSameCallAsActivation#4 state');
    AssertEquals_DINT(Expected := 1,
                      Actual := fbAckSameCallAsActivation.count,
                      Message := 'AckSameCallAsActivation#4 count');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
