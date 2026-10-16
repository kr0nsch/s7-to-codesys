// AUTO-GENERATED — не редактировать: scenarios/FB_AlarmDelay.csv, сценарий ChatterSuppressed
coUnit.TEST('ChatterSuppressed');
IF NOT xChatterSuppressedDone THEN
    xChatterSuppressedDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;

    // #1, t = 0 мс — условие
    GVL_S7Clock.tSimNow := T#0MS;
    fbChatterSuppressed.condition := TRUE;
    fbChatterSuppressed.enable := TRUE;
    fbChatterSuppressed.ack := FALSE;
    fbChatterSuppressed.onDelay := T#5000MS;
    fbChatterSuppressed.offDelay := T#2000MS;
    fbChatterSuppressed();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbChatterSuppressed.active, Message := 'ChatterSuppressed#1 active');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbChatterSuppressed.unacked,
                      Message := 'ChatterSuppressed#1 unacked');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbChatterSuppressed.alarm, Message := 'ChatterSuppressed#1 alarm');
    AssertEquals_INT(Expected := 0, Actual := fbChatterSuppressed.state, Message := 'ChatterSuppressed#1 state');
    AssertEquals_DINT(Expected := 0, Actual := fbChatterSuppressed.count, Message := 'ChatterSuppressed#1 count');

    // #2, t = 3000 мс — пропало через 3 с
    GVL_S7Clock.tSimNow := T#3000MS;
    fbChatterSuppressed.condition := FALSE;
    fbChatterSuppressed();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbChatterSuppressed.active, Message := 'ChatterSuppressed#2 active');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbChatterSuppressed.unacked,
                      Message := 'ChatterSuppressed#2 unacked');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbChatterSuppressed.alarm, Message := 'ChatterSuppressed#2 alarm');
    AssertEquals_INT(Expected := 0, Actual := fbChatterSuppressed.state, Message := 'ChatterSuppressed#2 state');
    AssertEquals_DINT(Expected := 0, Actual := fbChatterSuppressed.count, Message := 'ChatterSuppressed#2 count');

    // #3, t = 3500 мс — снова; отсчёт заново с 3.5 с
    GVL_S7Clock.tSimNow := T#3500MS;
    fbChatterSuppressed.condition := TRUE;
    fbChatterSuppressed();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbChatterSuppressed.active, Message := 'ChatterSuppressed#3 active');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbChatterSuppressed.unacked,
                      Message := 'ChatterSuppressed#3 unacked');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbChatterSuppressed.alarm, Message := 'ChatterSuppressed#3 alarm');
    AssertEquals_INT(Expected := 0, Actual := fbChatterSuppressed.state, Message := 'ChatterSuppressed#3 state');
    AssertEquals_DINT(Expected := 0, Actual := fbChatterSuppressed.count, Message := 'ChatterSuppressed#3 count');

    // #4, t = 8000 мс — 4.5 с < 5 с: не активен
    GVL_S7Clock.tSimNow := T#8000MS;
    fbChatterSuppressed();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbChatterSuppressed.active, Message := 'ChatterSuppressed#4 active');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbChatterSuppressed.unacked,
                      Message := 'ChatterSuppressed#4 unacked');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbChatterSuppressed.alarm, Message := 'ChatterSuppressed#4 alarm');
    AssertEquals_INT(Expected := 0, Actual := fbChatterSuppressed.state, Message := 'ChatterSuppressed#4 state');
    AssertEquals_DINT(Expected := 0, Actual := fbChatterSuppressed.count, Message := 'ChatterSuppressed#4 count');

    // #5, t = 8300 мс — пропало
    GVL_S7Clock.tSimNow := T#8300MS;
    fbChatterSuppressed.condition := FALSE;
    fbChatterSuppressed();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbChatterSuppressed.active, Message := 'ChatterSuppressed#5 active');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbChatterSuppressed.unacked,
                      Message := 'ChatterSuppressed#5 unacked');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbChatterSuppressed.alarm, Message := 'ChatterSuppressed#5 alarm');
    AssertEquals_INT(Expected := 0, Actual := fbChatterSuppressed.state, Message := 'ChatterSuppressed#5 state');
    AssertEquals_DINT(Expected := 0, Actual := fbChatterSuppressed.count, Message := 'ChatterSuppressed#5 count');

    // #6, t = 9000 мс — появлений нет
    GVL_S7Clock.tSimNow := T#9000MS;
    fbChatterSuppressed();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbChatterSuppressed.active, Message := 'ChatterSuppressed#6 active');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbChatterSuppressed.unacked,
                      Message := 'ChatterSuppressed#6 unacked');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbChatterSuppressed.alarm, Message := 'ChatterSuppressed#6 alarm');
    AssertEquals_INT(Expected := 0, Actual := fbChatterSuppressed.state, Message := 'ChatterSuppressed#6 state');
    AssertEquals_DINT(Expected := 0, Actual := fbChatterSuppressed.count, Message := 'ChatterSuppressed#6 count');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
