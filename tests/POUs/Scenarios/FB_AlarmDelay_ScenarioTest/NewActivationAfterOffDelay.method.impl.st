// AUTO-GENERATED — не редактировать: scenarios/FB_AlarmDelay.csv, сценарий NewActivationAfterOffDelay
coUnit.TEST('NewActivationAfterOffDelay');
IF NOT xNewActivationAfterOffDelayDone THEN
    xNewActivationAfterOffDelayDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;

    // #1, t = 0 мс — условие
    GVL_S7Clock.tSimNow := T#0MS;
    fbNewActivationAfterOffDelay.condition := TRUE;
    fbNewActivationAfterOffDelay.enable := TRUE;
    fbNewActivationAfterOffDelay.ack := FALSE;
    fbNewActivationAfterOffDelay.onDelay := T#5000MS;
    fbNewActivationAfterOffDelay.offDelay := T#2000MS;
    fbNewActivationAfterOffDelay();
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbNewActivationAfterOffDelay.active,
                      Message := 'NewActivationAfterOffDelay#1 active');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbNewActivationAfterOffDelay.unacked,
                      Message := 'NewActivationAfterOffDelay#1 unacked');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbNewActivationAfterOffDelay.alarm,
                      Message := 'NewActivationAfterOffDelay#1 alarm');
    AssertEquals_INT(Expected := 0,
                     Actual := fbNewActivationAfterOffDelay.state,
                     Message := 'NewActivationAfterOffDelay#1 state');
    AssertEquals_DINT(Expected := 0,
                      Actual := fbNewActivationAfterOffDelay.count,
                      Message := 'NewActivationAfterOffDelay#1 count');

    // #2, t = 5200 мс — активен, появление №1
    GVL_S7Clock.tSimNow := T#5200MS;
    fbNewActivationAfterOffDelay();
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbNewActivationAfterOffDelay.active,
                      Message := 'NewActivationAfterOffDelay#2 active');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbNewActivationAfterOffDelay.unacked,
                      Message := 'NewActivationAfterOffDelay#2 unacked');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbNewActivationAfterOffDelay.alarm,
                      Message := 'NewActivationAfterOffDelay#2 alarm');
    AssertEquals_INT(Expected := 1,
                     Actual := fbNewActivationAfterOffDelay.state,
                     Message := 'NewActivationAfterOffDelay#2 state');
    AssertEquals_DINT(Expected := 1,
                      Actual := fbNewActivationAfterOffDelay.count,
                      Message := 'NewActivationAfterOffDelay#2 count');

    // #3, t = 6000 мс — условие пропало
    GVL_S7Clock.tSimNow := T#6000MS;
    fbNewActivationAfterOffDelay.condition := FALSE;
    fbNewActivationAfterOffDelay();
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbNewActivationAfterOffDelay.active,
                      Message := 'NewActivationAfterOffDelay#3 active');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbNewActivationAfterOffDelay.unacked,
                      Message := 'NewActivationAfterOffDelay#3 unacked');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbNewActivationAfterOffDelay.alarm,
                      Message := 'NewActivationAfterOffDelay#3 alarm');
    AssertEquals_INT(Expected := 1,
                     Actual := fbNewActivationAfterOffDelay.state,
                     Message := 'NewActivationAfterOffDelay#3 state');
    AssertEquals_DINT(Expected := 1,
                      Actual := fbNewActivationAfterOffDelay.count,
                      Message := 'NewActivationAfterOffDelay#3 count');

    // #4, t = 7000 мс — вернулось; onDelay с 7.0 с, offDelay ещё идёт
    GVL_S7Clock.tSimNow := T#7000MS;
    fbNewActivationAfterOffDelay.condition := TRUE;
    fbNewActivationAfterOffDelay();
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbNewActivationAfterOffDelay.active,
                      Message := 'NewActivationAfterOffDelay#4 active');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbNewActivationAfterOffDelay.unacked,
                      Message := 'NewActivationAfterOffDelay#4 unacked');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbNewActivationAfterOffDelay.alarm,
                      Message := 'NewActivationAfterOffDelay#4 alarm');
    AssertEquals_INT(Expected := 1,
                     Actual := fbNewActivationAfterOffDelay.state,
                     Message := 'NewActivationAfterOffDelay#4 state');
    AssertEquals_DINT(Expected := 1,
                      Actual := fbNewActivationAfterOffDelay.count,
                      Message := 'NewActivationAfterOffDelay#4 count');

    // #5, t = 8200 мс — offDelay 2.2 с истёк: снят, не квитирован — состояние 3
    GVL_S7Clock.tSimNow := T#8200MS;
    fbNewActivationAfterOffDelay();
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbNewActivationAfterOffDelay.active,
                      Message := 'NewActivationAfterOffDelay#5 active');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbNewActivationAfterOffDelay.unacked,
                      Message := 'NewActivationAfterOffDelay#5 unacked');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbNewActivationAfterOffDelay.alarm,
                      Message := 'NewActivationAfterOffDelay#5 alarm');
    AssertEquals_INT(Expected := 3,
                     Actual := fbNewActivationAfterOffDelay.state,
                     Message := 'NewActivationAfterOffDelay#5 state');
    AssertEquals_DINT(Expected := 1,
                      Actual := fbNewActivationAfterOffDelay.count,
                      Message := 'NewActivationAfterOffDelay#5 count');

    // #6, t = 12200 мс — onDelay 5.2 с: активен снова, появление №2
    GVL_S7Clock.tSimNow := T#12200MS;
    fbNewActivationAfterOffDelay();
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbNewActivationAfterOffDelay.active,
                      Message := 'NewActivationAfterOffDelay#6 active');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbNewActivationAfterOffDelay.unacked,
                      Message := 'NewActivationAfterOffDelay#6 unacked');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbNewActivationAfterOffDelay.alarm,
                      Message := 'NewActivationAfterOffDelay#6 alarm');
    AssertEquals_INT(Expected := 1,
                     Actual := fbNewActivationAfterOffDelay.state,
                     Message := 'NewActivationAfterOffDelay#6 state');
    AssertEquals_DINT(Expected := 2,
                      Actual := fbNewActivationAfterOffDelay.count,
                      Message := 'NewActivationAfterOffDelay#6 count');

    // #7, t = 13000 мс — квитирование
    GVL_S7Clock.tSimNow := T#13000MS;
    fbNewActivationAfterOffDelay.ack := TRUE;
    fbNewActivationAfterOffDelay();
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbNewActivationAfterOffDelay.active,
                      Message := 'NewActivationAfterOffDelay#7 active');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbNewActivationAfterOffDelay.unacked,
                      Message := 'NewActivationAfterOffDelay#7 unacked');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbNewActivationAfterOffDelay.alarm,
                      Message := 'NewActivationAfterOffDelay#7 alarm');
    AssertEquals_INT(Expected := 2,
                     Actual := fbNewActivationAfterOffDelay.state,
                     Message := 'NewActivationAfterOffDelay#7 state');
    AssertEquals_DINT(Expected := 2,
                      Actual := fbNewActivationAfterOffDelay.count,
                      Message := 'NewActivationAfterOffDelay#7 count');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
