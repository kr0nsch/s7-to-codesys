// AUTO-GENERATED — не редактировать: scenarios/FB_AlarmDelay.csv, сценарий ReturnDuringOffDelay
coUnit.TEST('ReturnDuringOffDelay');
IF NOT xReturnDuringOffDelayDone THEN
    xReturnDuringOffDelayDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;

    // #1, t = 0 мс — условие, offDelay 6 с
    GVL_S7Clock.tSimNow := T#0MS;
    fbReturnDuringOffDelay.condition := TRUE;
    fbReturnDuringOffDelay.enable := TRUE;
    fbReturnDuringOffDelay.ack := FALSE;
    fbReturnDuringOffDelay.onDelay := T#5000MS;
    fbReturnDuringOffDelay.offDelay := T#6000MS;
    fbReturnDuringOffDelay();
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbReturnDuringOffDelay.active,
                      Message := 'ReturnDuringOffDelay#1 active');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbReturnDuringOffDelay.unacked,
                      Message := 'ReturnDuringOffDelay#1 unacked');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbReturnDuringOffDelay.alarm,
                      Message := 'ReturnDuringOffDelay#1 alarm');
    AssertEquals_INT(Expected := 0, Actual := fbReturnDuringOffDelay.state, Message := 'ReturnDuringOffDelay#1 state');
    AssertEquals_DINT(Expected := 0, Actual := fbReturnDuringOffDelay.count, Message := 'ReturnDuringOffDelay#1 count');

    // #2, t = 5200 мс — активен, появление №1
    GVL_S7Clock.tSimNow := T#5200MS;
    fbReturnDuringOffDelay();
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbReturnDuringOffDelay.active,
                      Message := 'ReturnDuringOffDelay#2 active');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbReturnDuringOffDelay.unacked,
                      Message := 'ReturnDuringOffDelay#2 unacked');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbReturnDuringOffDelay.alarm,
                      Message := 'ReturnDuringOffDelay#2 alarm');
    AssertEquals_INT(Expected := 1, Actual := fbReturnDuringOffDelay.state, Message := 'ReturnDuringOffDelay#2 state');
    AssertEquals_DINT(Expected := 1, Actual := fbReturnDuringOffDelay.count, Message := 'ReturnDuringOffDelay#2 count');

    // #3, t = 5500 мс — квитирован
    GVL_S7Clock.tSimNow := T#5500MS;
    fbReturnDuringOffDelay.ack := TRUE;
    fbReturnDuringOffDelay();
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbReturnDuringOffDelay.active,
                      Message := 'ReturnDuringOffDelay#3 active');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbReturnDuringOffDelay.unacked,
                      Message := 'ReturnDuringOffDelay#3 unacked');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbReturnDuringOffDelay.alarm,
                      Message := 'ReturnDuringOffDelay#3 alarm');
    AssertEquals_INT(Expected := 2, Actual := fbReturnDuringOffDelay.state, Message := 'ReturnDuringOffDelay#3 state');
    AssertEquals_DINT(Expected := 1, Actual := fbReturnDuringOffDelay.count, Message := 'ReturnDuringOffDelay#3 count');

    // #4, t = 6000 мс — условие пропало; offDelay с 6.0 с
    GVL_S7Clock.tSimNow := T#6000MS;
    fbReturnDuringOffDelay.condition := FALSE;
    fbReturnDuringOffDelay.ack := FALSE;
    fbReturnDuringOffDelay();
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbReturnDuringOffDelay.active,
                      Message := 'ReturnDuringOffDelay#4 active');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbReturnDuringOffDelay.unacked,
                      Message := 'ReturnDuringOffDelay#4 unacked');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbReturnDuringOffDelay.alarm,
                      Message := 'ReturnDuringOffDelay#4 alarm');
    AssertEquals_INT(Expected := 2, Actual := fbReturnDuringOffDelay.state, Message := 'ReturnDuringOffDelay#4 state');
    AssertEquals_DINT(Expected := 1, Actual := fbReturnDuringOffDelay.count, Message := 'ReturnDuringOffDelay#4 count');

    // #5, t = 7000 мс — условие вернулось; onDelay заново с 7.0 с
    GVL_S7Clock.tSimNow := T#7000MS;
    fbReturnDuringOffDelay.condition := TRUE;
    fbReturnDuringOffDelay();
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbReturnDuringOffDelay.active,
                      Message := 'ReturnDuringOffDelay#5 active');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbReturnDuringOffDelay.unacked,
                      Message := 'ReturnDuringOffDelay#5 unacked');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbReturnDuringOffDelay.alarm,
                      Message := 'ReturnDuringOffDelay#5 alarm');
    AssertEquals_INT(Expected := 2, Actual := fbReturnDuringOffDelay.state, Message := 'ReturnDuringOffDelay#5 state');
    AssertEquals_DINT(Expected := 1, Actual := fbReturnDuringOffDelay.count, Message := 'ReturnDuringOffDelay#5 count');

    // #6, t = 11800 мс — onDelay 4.8 с, offDelay 5.8 с: ещё активен по задержке снятия
    GVL_S7Clock.tSimNow := T#11800MS;
    fbReturnDuringOffDelay();
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbReturnDuringOffDelay.active,
                      Message := 'ReturnDuringOffDelay#6 active');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbReturnDuringOffDelay.unacked,
                      Message := 'ReturnDuringOffDelay#6 unacked');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbReturnDuringOffDelay.alarm,
                      Message := 'ReturnDuringOffDelay#6 alarm');
    AssertEquals_INT(Expected := 2, Actual := fbReturnDuringOffDelay.state, Message := 'ReturnDuringOffDelay#6 state');
    AssertEquals_DINT(Expected := 1, Actual := fbReturnDuringOffDelay.count, Message := 'ReturnDuringOffDelay#6 count');

    // #7, t = 12200 мс — onDelay истёк раньше offDelay: активен без перерыва, счёт не растёт
    GVL_S7Clock.tSimNow := T#12200MS;
    fbReturnDuringOffDelay();
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbReturnDuringOffDelay.active,
                      Message := 'ReturnDuringOffDelay#7 active');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbReturnDuringOffDelay.unacked,
                      Message := 'ReturnDuringOffDelay#7 unacked');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbReturnDuringOffDelay.alarm,
                      Message := 'ReturnDuringOffDelay#7 alarm');
    AssertEquals_INT(Expected := 2, Actual := fbReturnDuringOffDelay.state, Message := 'ReturnDuringOffDelay#7 state');
    AssertEquals_DINT(Expected := 1, Actual := fbReturnDuringOffDelay.count, Message := 'ReturnDuringOffDelay#7 count');

    // #8, t = 13000 мс — условие пропало; offDelay с 13.0 с
    GVL_S7Clock.tSimNow := T#13000MS;
    fbReturnDuringOffDelay.condition := FALSE;
    fbReturnDuringOffDelay();
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbReturnDuringOffDelay.active,
                      Message := 'ReturnDuringOffDelay#8 active');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbReturnDuringOffDelay.unacked,
                      Message := 'ReturnDuringOffDelay#8 unacked');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbReturnDuringOffDelay.alarm,
                      Message := 'ReturnDuringOffDelay#8 alarm');
    AssertEquals_INT(Expected := 2, Actual := fbReturnDuringOffDelay.state, Message := 'ReturnDuringOffDelay#8 state');
    AssertEquals_DINT(Expected := 1, Actual := fbReturnDuringOffDelay.count, Message := 'ReturnDuringOffDelay#8 count');

    // #9, t = 19200 мс — 6.2 с: снят — норма
    GVL_S7Clock.tSimNow := T#19200MS;
    fbReturnDuringOffDelay();
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbReturnDuringOffDelay.active,
                      Message := 'ReturnDuringOffDelay#9 active');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbReturnDuringOffDelay.unacked,
                      Message := 'ReturnDuringOffDelay#9 unacked');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbReturnDuringOffDelay.alarm,
                      Message := 'ReturnDuringOffDelay#9 alarm');
    AssertEquals_INT(Expected := 0, Actual := fbReturnDuringOffDelay.state, Message := 'ReturnDuringOffDelay#9 state');
    AssertEquals_DINT(Expected := 1, Actual := fbReturnDuringOffDelay.count, Message := 'ReturnDuringOffDelay#9 count');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
