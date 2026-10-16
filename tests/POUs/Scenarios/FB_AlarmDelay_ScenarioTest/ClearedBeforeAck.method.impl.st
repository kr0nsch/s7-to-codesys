// AUTO-GENERATED — не редактировать: scenarios/FB_AlarmDelay.csv, сценарий ClearedBeforeAck
coUnit.TEST('ClearedBeforeAck');
IF NOT xClearedBeforeAckDone THEN
    xClearedBeforeAckDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;

    // #1, t = 0 мс — условие
    GVL_S7Clock.tSimNow := T#0MS;
    fbClearedBeforeAck.condition := TRUE;
    fbClearedBeforeAck.enable := TRUE;
    fbClearedBeforeAck.ack := FALSE;
    fbClearedBeforeAck.onDelay := T#5000MS;
    fbClearedBeforeAck.offDelay := T#2000MS;
    fbClearedBeforeAck();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbClearedBeforeAck.active, Message := 'ClearedBeforeAck#1 active');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbClearedBeforeAck.unacked, Message := 'ClearedBeforeAck#1 unacked');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbClearedBeforeAck.alarm, Message := 'ClearedBeforeAck#1 alarm');
    AssertEquals_INT(Expected := 0, Actual := fbClearedBeforeAck.state, Message := 'ClearedBeforeAck#1 state');
    AssertEquals_DINT(Expected := 0, Actual := fbClearedBeforeAck.count, Message := 'ClearedBeforeAck#1 count');

    // #2, t = 5200 мс — активен, появление №1
    GVL_S7Clock.tSimNow := T#5200MS;
    fbClearedBeforeAck();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbClearedBeforeAck.active, Message := 'ClearedBeforeAck#2 active');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbClearedBeforeAck.unacked, Message := 'ClearedBeforeAck#2 unacked');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbClearedBeforeAck.alarm, Message := 'ClearedBeforeAck#2 alarm');
    AssertEquals_INT(Expected := 1, Actual := fbClearedBeforeAck.state, Message := 'ClearedBeforeAck#2 state');
    AssertEquals_DINT(Expected := 1, Actual := fbClearedBeforeAck.count, Message := 'ClearedBeforeAck#2 count');

    // #3, t = 6000 мс — условие пропало
    GVL_S7Clock.tSimNow := T#6000MS;
    fbClearedBeforeAck.condition := FALSE;
    fbClearedBeforeAck();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbClearedBeforeAck.active, Message := 'ClearedBeforeAck#3 active');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbClearedBeforeAck.unacked, Message := 'ClearedBeforeAck#3 unacked');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbClearedBeforeAck.alarm, Message := 'ClearedBeforeAck#3 alarm');
    AssertEquals_INT(Expected := 1, Actual := fbClearedBeforeAck.state, Message := 'ClearedBeforeAck#3 state');
    AssertEquals_DINT(Expected := 1, Actual := fbClearedBeforeAck.count, Message := 'ClearedBeforeAck#3 count');

    // #4, t = 8200 мс — через 2.2 с снят, но не квитирован: состояние 3, индикация есть
    GVL_S7Clock.tSimNow := T#8200MS;
    fbClearedBeforeAck();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbClearedBeforeAck.active, Message := 'ClearedBeforeAck#4 active');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbClearedBeforeAck.unacked, Message := 'ClearedBeforeAck#4 unacked');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbClearedBeforeAck.alarm, Message := 'ClearedBeforeAck#4 alarm');
    AssertEquals_INT(Expected := 3, Actual := fbClearedBeforeAck.state, Message := 'ClearedBeforeAck#4 state');
    AssertEquals_DINT(Expected := 1, Actual := fbClearedBeforeAck.count, Message := 'ClearedBeforeAck#4 count');

    // #5, t = 9000 мс — квитирование: норма
    GVL_S7Clock.tSimNow := T#9000MS;
    fbClearedBeforeAck.ack := TRUE;
    fbClearedBeforeAck();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbClearedBeforeAck.active, Message := 'ClearedBeforeAck#5 active');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbClearedBeforeAck.unacked, Message := 'ClearedBeforeAck#5 unacked');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbClearedBeforeAck.alarm, Message := 'ClearedBeforeAck#5 alarm');
    AssertEquals_INT(Expected := 0, Actual := fbClearedBeforeAck.state, Message := 'ClearedBeforeAck#5 state');
    AssertEquals_DINT(Expected := 1, Actual := fbClearedBeforeAck.count, Message := 'ClearedBeforeAck#5 count');

    // #6, t = 9500 мс — норма
    GVL_S7Clock.tSimNow := T#9500MS;
    fbClearedBeforeAck.ack := FALSE;
    fbClearedBeforeAck();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbClearedBeforeAck.active, Message := 'ClearedBeforeAck#6 active');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbClearedBeforeAck.unacked, Message := 'ClearedBeforeAck#6 unacked');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbClearedBeforeAck.alarm, Message := 'ClearedBeforeAck#6 alarm');
    AssertEquals_INT(Expected := 0, Actual := fbClearedBeforeAck.state, Message := 'ClearedBeforeAck#6 state');
    AssertEquals_DINT(Expected := 1, Actual := fbClearedBeforeAck.count, Message := 'ClearedBeforeAck#6 count');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
