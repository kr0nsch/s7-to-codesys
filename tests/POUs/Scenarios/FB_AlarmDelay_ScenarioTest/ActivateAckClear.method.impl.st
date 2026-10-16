// AUTO-GENERATED — не редактировать: scenarios/FB_AlarmDelay.csv, сценарий ActivateAckClear
coUnit.TEST('ActivateAckClear');
IF NOT xActivateAckClearDone THEN
    xActivateAckClearDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;

    // #1, t = 0 мс — норма
    GVL_S7Clock.tSimNow := T#0MS;
    fbActivateAckClear.condition := FALSE;
    fbActivateAckClear.enable := TRUE;
    fbActivateAckClear.ack := FALSE;
    fbActivateAckClear.onDelay := T#5000MS;
    fbActivateAckClear.offDelay := T#2000MS;
    fbActivateAckClear();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbActivateAckClear.active, Message := 'ActivateAckClear#1 active');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbActivateAckClear.unacked, Message := 'ActivateAckClear#1 unacked');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbActivateAckClear.alarm, Message := 'ActivateAckClear#1 alarm');
    AssertEquals_INT(Expected := 0, Actual := fbActivateAckClear.state, Message := 'ActivateAckClear#1 state');
    AssertEquals_DINT(Expected := 0, Actual := fbActivateAckClear.count, Message := 'ActivateAckClear#1 count');

    // #2, t = 1000 мс — условие появилось; отсчёт onDelay с 1.0 с
    GVL_S7Clock.tSimNow := T#1000MS;
    fbActivateAckClear.condition := TRUE;
    fbActivateAckClear();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbActivateAckClear.active, Message := 'ActivateAckClear#2 active');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbActivateAckClear.unacked, Message := 'ActivateAckClear#2 unacked');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbActivateAckClear.alarm, Message := 'ActivateAckClear#2 alarm');
    AssertEquals_INT(Expected := 0, Actual := fbActivateAckClear.state, Message := 'ActivateAckClear#2 state');
    AssertEquals_DINT(Expected := 0, Actual := fbActivateAckClear.count, Message := 'ActivateAckClear#2 count');

    // #3, t = 5800 мс — 4.8 с < 5 с: ещё не активен
    GVL_S7Clock.tSimNow := T#5800MS;
    fbActivateAckClear();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbActivateAckClear.active, Message := 'ActivateAckClear#3 active');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbActivateAckClear.unacked, Message := 'ActivateAckClear#3 unacked');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbActivateAckClear.alarm, Message := 'ActivateAckClear#3 alarm');
    AssertEquals_INT(Expected := 0, Actual := fbActivateAckClear.state, Message := 'ActivateAckClear#3 state');
    AssertEquals_DINT(Expected := 0, Actual := fbActivateAckClear.count, Message := 'ActivateAckClear#3 count');

    // #4, t = 6000 мс, на пороге таймера — 5.0 с = onDelay: активен, не квитирован, появление №1
    GVL_S7Clock.tSimNow := T#6000MS;
    fbActivateAckClear();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbActivateAckClear.active, Message := 'ActivateAckClear#4 active');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbActivateAckClear.unacked, Message := 'ActivateAckClear#4 unacked');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbActivateAckClear.alarm, Message := 'ActivateAckClear#4 alarm');
    AssertEquals_INT(Expected := 1, Actual := fbActivateAckClear.state, Message := 'ActivateAckClear#4 state');
    AssertEquals_DINT(Expected := 1, Actual := fbActivateAckClear.count, Message := 'ActivateAckClear#4 count');

    // #5, t = 6200 мс — активен, не квитирован
    GVL_S7Clock.tSimNow := T#6200MS;
    fbActivateAckClear();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbActivateAckClear.active, Message := 'ActivateAckClear#5 active');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbActivateAckClear.unacked, Message := 'ActivateAckClear#5 unacked');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbActivateAckClear.alarm, Message := 'ActivateAckClear#5 alarm');
    AssertEquals_INT(Expected := 1, Actual := fbActivateAckClear.state, Message := 'ActivateAckClear#5 state');
    AssertEquals_DINT(Expected := 1, Actual := fbActivateAckClear.count, Message := 'ActivateAckClear#5 count');

    // #6, t = 7000 мс — квитирование: активен, квитирован
    GVL_S7Clock.tSimNow := T#7000MS;
    fbActivateAckClear.ack := TRUE;
    fbActivateAckClear();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbActivateAckClear.active, Message := 'ActivateAckClear#6 active');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbActivateAckClear.unacked, Message := 'ActivateAckClear#6 unacked');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbActivateAckClear.alarm, Message := 'ActivateAckClear#6 alarm');
    AssertEquals_INT(Expected := 2, Actual := fbActivateAckClear.state, Message := 'ActivateAckClear#6 state');
    AssertEquals_DINT(Expected := 1, Actual := fbActivateAckClear.count, Message := 'ActivateAckClear#6 count');

    // #7, t = 7500 мс — кнопка отпущена
    GVL_S7Clock.tSimNow := T#7500MS;
    fbActivateAckClear.ack := FALSE;
    fbActivateAckClear();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbActivateAckClear.active, Message := 'ActivateAckClear#7 active');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbActivateAckClear.unacked, Message := 'ActivateAckClear#7 unacked');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbActivateAckClear.alarm, Message := 'ActivateAckClear#7 alarm');
    AssertEquals_INT(Expected := 2, Actual := fbActivateAckClear.state, Message := 'ActivateAckClear#7 state');
    AssertEquals_DINT(Expected := 1, Actual := fbActivateAckClear.count, Message := 'ActivateAckClear#7 count');

    // #8, t = 9000 мс — условие пропало; отсчёт offDelay с 9.0 с, сигнал держится
    GVL_S7Clock.tSimNow := T#9000MS;
    fbActivateAckClear.condition := FALSE;
    fbActivateAckClear();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbActivateAckClear.active, Message := 'ActivateAckClear#8 active');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbActivateAckClear.unacked, Message := 'ActivateAckClear#8 unacked');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbActivateAckClear.alarm, Message := 'ActivateAckClear#8 alarm');
    AssertEquals_INT(Expected := 2, Actual := fbActivateAckClear.state, Message := 'ActivateAckClear#8 state');
    AssertEquals_DINT(Expected := 1, Actual := fbActivateAckClear.count, Message := 'ActivateAckClear#8 count');

    // #9, t = 10800 мс — 1.8 с < 2 с: ещё активен
    GVL_S7Clock.tSimNow := T#10800MS;
    fbActivateAckClear();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbActivateAckClear.active, Message := 'ActivateAckClear#9 active');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbActivateAckClear.unacked, Message := 'ActivateAckClear#9 unacked');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbActivateAckClear.alarm, Message := 'ActivateAckClear#9 alarm');
    AssertEquals_INT(Expected := 2, Actual := fbActivateAckClear.state, Message := 'ActivateAckClear#9 state');
    AssertEquals_DINT(Expected := 1, Actual := fbActivateAckClear.count, Message := 'ActivateAckClear#9 count');

    // #10, t = 11000 мс, на пороге таймера — 2.0 с = offDelay: снят, квитирован — норма
    GVL_S7Clock.tSimNow := T#11000MS;
    fbActivateAckClear();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbActivateAckClear.active, Message := 'ActivateAckClear#10 active');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbActivateAckClear.unacked,
                      Message := 'ActivateAckClear#10 unacked');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbActivateAckClear.alarm, Message := 'ActivateAckClear#10 alarm');
    AssertEquals_INT(Expected := 0, Actual := fbActivateAckClear.state, Message := 'ActivateAckClear#10 state');
    AssertEquals_DINT(Expected := 1, Actual := fbActivateAckClear.count, Message := 'ActivateAckClear#10 count');

    // #11, t = 11200 мс — норма
    GVL_S7Clock.tSimNow := T#11200MS;
    fbActivateAckClear();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbActivateAckClear.active, Message := 'ActivateAckClear#11 active');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbActivateAckClear.unacked,
                      Message := 'ActivateAckClear#11 unacked');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbActivateAckClear.alarm, Message := 'ActivateAckClear#11 alarm');
    AssertEquals_INT(Expected := 0, Actual := fbActivateAckClear.state, Message := 'ActivateAckClear#11 state');
    AssertEquals_DINT(Expected := 1, Actual := fbActivateAckClear.count, Message := 'ActivateAckClear#11 count');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
