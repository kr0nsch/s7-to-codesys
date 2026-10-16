// AUTO-GENERATED — не редактировать: scenarios/FB_AlarmDelay.csv, сценарий Disabled
coUnit.TEST('Disabled');
IF NOT xDisabledDone THEN
    xDisabledDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;

    // #1, t = 0 мс — условие
    GVL_S7Clock.tSimNow := T#0MS;
    fbDisabled.condition := TRUE;
    fbDisabled.enable := TRUE;
    fbDisabled.ack := FALSE;
    fbDisabled.onDelay := T#5000MS;
    fbDisabled.offDelay := T#2000MS;
    fbDisabled();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDisabled.active, Message := 'Disabled#1 active');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDisabled.unacked, Message := 'Disabled#1 unacked');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDisabled.alarm, Message := 'Disabled#1 alarm');
    AssertEquals_INT(Expected := 0, Actual := fbDisabled.state, Message := 'Disabled#1 state');
    AssertEquals_DINT(Expected := 0, Actual := fbDisabled.count, Message := 'Disabled#1 count');

    // #2, t = 5200 мс — активен, появление №1
    GVL_S7Clock.tSimNow := T#5200MS;
    fbDisabled();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbDisabled.active, Message := 'Disabled#2 active');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbDisabled.unacked, Message := 'Disabled#2 unacked');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbDisabled.alarm, Message := 'Disabled#2 alarm');
    AssertEquals_INT(Expected := 1, Actual := fbDisabled.state, Message := 'Disabled#2 state');
    AssertEquals_DINT(Expected := 1, Actual := fbDisabled.count, Message := 'Disabled#2 count');

    // #3, t = 6000 мс — выведен из работы: active и unacked сброшены сразу
    GVL_S7Clock.tSimNow := T#6000MS;
    fbDisabled.enable := FALSE;
    fbDisabled();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDisabled.active, Message := 'Disabled#3 active');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDisabled.unacked, Message := 'Disabled#3 unacked');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDisabled.alarm, Message := 'Disabled#3 alarm');
    AssertEquals_INT(Expected := 0, Actual := fbDisabled.state, Message := 'Disabled#3 state');
    AssertEquals_DINT(Expected := 1, Actual := fbDisabled.count, Message := 'Disabled#3 count');

    // #4, t = 7000 мс — выведен
    GVL_S7Clock.tSimNow := T#7000MS;
    fbDisabled();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDisabled.active, Message := 'Disabled#4 active');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDisabled.unacked, Message := 'Disabled#4 unacked');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDisabled.alarm, Message := 'Disabled#4 alarm');
    AssertEquals_INT(Expected := 0, Actual := fbDisabled.state, Message := 'Disabled#4 state');
    AssertEquals_DINT(Expected := 1, Actual := fbDisabled.count, Message := 'Disabled#4 count');

    // #5, t = 8500 мс — выведен (задержка снятия внутри уже истекла)
    GVL_S7Clock.tSimNow := T#8500MS;
    fbDisabled();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDisabled.active, Message := 'Disabled#5 active');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDisabled.unacked, Message := 'Disabled#5 unacked');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDisabled.alarm, Message := 'Disabled#5 alarm');
    AssertEquals_INT(Expected := 0, Actual := fbDisabled.state, Message := 'Disabled#5 state');
    AssertEquals_DINT(Expected := 1, Actual := fbDisabled.count, Message := 'Disabled#5 count');

    // #6, t = 9000 мс — введён: условие есть, onDelay с 9.0 с
    GVL_S7Clock.tSimNow := T#9000MS;
    fbDisabled.enable := TRUE;
    fbDisabled();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDisabled.active, Message := 'Disabled#6 active');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDisabled.unacked, Message := 'Disabled#6 unacked');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDisabled.alarm, Message := 'Disabled#6 alarm');
    AssertEquals_INT(Expected := 0, Actual := fbDisabled.state, Message := 'Disabled#6 state');
    AssertEquals_DINT(Expected := 1, Actual := fbDisabled.count, Message := 'Disabled#6 count');

    // #7, t = 14200 мс — 5.2 с: активен, появление №2
    GVL_S7Clock.tSimNow := T#14200MS;
    fbDisabled();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbDisabled.active, Message := 'Disabled#7 active');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbDisabled.unacked, Message := 'Disabled#7 unacked');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbDisabled.alarm, Message := 'Disabled#7 alarm');
    AssertEquals_INT(Expected := 1, Actual := fbDisabled.state, Message := 'Disabled#7 state');
    AssertEquals_DINT(Expected := 2, Actual := fbDisabled.count, Message := 'Disabled#7 count');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
