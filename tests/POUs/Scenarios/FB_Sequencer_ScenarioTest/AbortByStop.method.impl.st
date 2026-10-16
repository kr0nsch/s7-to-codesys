// AUTO-GENERATED — не редактировать: scenarios/FB_Sequencer.csv, сценарий AbortByStop
coUnit.TEST('AbortByStop');
IF NOT xAbortByStopDone THEN
    xAbortByStopDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;

    // #1, t = 0 мс — ожидание
    GVL_S7Clock.tSimNow := T#0MS;
    fbAbortByStop.start := FALSE;
    fbAbortByStop.stop := FALSE;
    fbAbortByStop.permissive := TRUE;
    fbAbortByStop.levelLow := FALSE;
    fbAbortByStop.levelHigh := FALSE;
    fbAbortByStop.reset := FALSE;
    fbAbortByStop.drainTimeout := T#60000MS;
    fbAbortByStop.airTime := T#30000MS;
    fbAbortByStop.washTime := T#40000MS;
    fbAbortByStop.refillTimeout := T#90000MS;
    fbAbortByStop();
    AssertEquals_INT(Expected := 0, Actual := fbAbortByStop.stepNo, Message := 'AbortByStop#1 stepNo');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAbortByStop.drainValve, Message := 'AbortByStop#1 drainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAbortByStop.airBlower, Message := 'AbortByStop#1 airBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAbortByStop.washPump, Message := 'AbortByStop#1 washPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAbortByStop.inletValve, Message := 'AbortByStop#1 inletValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAbortByStop.busy, Message := 'AbortByStop#1 busy');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAbortByStop.fault, Message := 'AbortByStop#1 fault');
    AssertEquals_INT(Expected := 0, Actual := fbAbortByStop.faultStep, Message := 'AbortByStop#1 faultStep');
    AssertEquals_DINT(Expected := 0, Actual := fbAbortByStop.cycleCount, Message := 'AbortByStop#1 cycleCount');
    AssertEquals_STRING(Expected := 'IDLE', Actual := fbAbortByStop.stepText, Message := 'AbortByStop#1 stepText');

    // #2, t = 1000 мс — пуск: опорожнение
    GVL_S7Clock.tSimNow := T#1000MS;
    fbAbortByStop.start := TRUE;
    fbAbortByStop();
    AssertEquals_INT(Expected := 10, Actual := fbAbortByStop.stepNo, Message := 'AbortByStop#2 stepNo');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbAbortByStop.drainValve, Message := 'AbortByStop#2 drainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAbortByStop.airBlower, Message := 'AbortByStop#2 airBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAbortByStop.washPump, Message := 'AbortByStop#2 washPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAbortByStop.inletValve, Message := 'AbortByStop#2 inletValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbAbortByStop.busy, Message := 'AbortByStop#2 busy');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAbortByStop.fault, Message := 'AbortByStop#2 fault');
    AssertEquals_INT(Expected := 0, Actual := fbAbortByStop.faultStep, Message := 'AbortByStop#2 faultStep');
    AssertEquals_DINT(Expected := 0, Actual := fbAbortByStop.cycleCount, Message := 'AbortByStop#2 cycleCount');
    AssertEquals_STRING(Expected := 'DRAIN', Actual := fbAbortByStop.stepText, Message := 'AbortByStop#2 stepText');

    // #3, t = 5000 мс — продувка с 5.0 с
    GVL_S7Clock.tSimNow := T#5000MS;
    fbAbortByStop.start := FALSE;
    fbAbortByStop.levelLow := TRUE;
    fbAbortByStop();
    AssertEquals_INT(Expected := 20, Actual := fbAbortByStop.stepNo, Message := 'AbortByStop#3 stepNo');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAbortByStop.drainValve, Message := 'AbortByStop#3 drainValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbAbortByStop.airBlower, Message := 'AbortByStop#3 airBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAbortByStop.washPump, Message := 'AbortByStop#3 washPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAbortByStop.inletValve, Message := 'AbortByStop#3 inletValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbAbortByStop.busy, Message := 'AbortByStop#3 busy');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAbortByStop.fault, Message := 'AbortByStop#3 fault');
    AssertEquals_INT(Expected := 0, Actual := fbAbortByStop.faultStep, Message := 'AbortByStop#3 faultStep');
    AssertEquals_DINT(Expected := 0, Actual := fbAbortByStop.cycleCount, Message := 'AbortByStop#3 cycleCount');
    AssertEquals_STRING(Expected := 'AIR SCOUR', Actual := fbAbortByStop.stepText, Message := 'AbortByStop#3 stepText');

    // #4, t = 10000 мс — прерывание: ожидание, без аварии и без счёта
    GVL_S7Clock.tSimNow := T#10000MS;
    fbAbortByStop.stop := TRUE;
    fbAbortByStop();
    AssertEquals_INT(Expected := 0, Actual := fbAbortByStop.stepNo, Message := 'AbortByStop#4 stepNo');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAbortByStop.drainValve, Message := 'AbortByStop#4 drainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAbortByStop.airBlower, Message := 'AbortByStop#4 airBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAbortByStop.washPump, Message := 'AbortByStop#4 washPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAbortByStop.inletValve, Message := 'AbortByStop#4 inletValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAbortByStop.busy, Message := 'AbortByStop#4 busy');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAbortByStop.fault, Message := 'AbortByStop#4 fault');
    AssertEquals_INT(Expected := 0, Actual := fbAbortByStop.faultStep, Message := 'AbortByStop#4 faultStep');
    AssertEquals_DINT(Expected := 0, Actual := fbAbortByStop.cycleCount, Message := 'AbortByStop#4 cycleCount');
    AssertEquals_STRING(Expected := 'IDLE', Actual := fbAbortByStop.stepText, Message := 'AbortByStop#4 stepText');

    // #5, t = 11000 мс — фронт start при stop: не запускается
    GVL_S7Clock.tSimNow := T#11000MS;
    fbAbortByStop.start := TRUE;
    fbAbortByStop();
    AssertEquals_INT(Expected := 0, Actual := fbAbortByStop.stepNo, Message := 'AbortByStop#5 stepNo');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAbortByStop.drainValve, Message := 'AbortByStop#5 drainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAbortByStop.airBlower, Message := 'AbortByStop#5 airBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAbortByStop.washPump, Message := 'AbortByStop#5 washPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAbortByStop.inletValve, Message := 'AbortByStop#5 inletValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAbortByStop.busy, Message := 'AbortByStop#5 busy');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAbortByStop.fault, Message := 'AbortByStop#5 fault');
    AssertEquals_INT(Expected := 0, Actual := fbAbortByStop.faultStep, Message := 'AbortByStop#5 faultStep');
    AssertEquals_DINT(Expected := 0, Actual := fbAbortByStop.cycleCount, Message := 'AbortByStop#5 cycleCount');
    AssertEquals_STRING(Expected := 'IDLE', Actual := fbAbortByStop.stepText, Message := 'AbortByStop#5 stepText');

    // #6, t = 12000 мс — stop снят
    GVL_S7Clock.tSimNow := T#12000MS;
    fbAbortByStop.start := FALSE;
    fbAbortByStop.stop := FALSE;
    fbAbortByStop();
    AssertEquals_INT(Expected := 0, Actual := fbAbortByStop.stepNo, Message := 'AbortByStop#6 stepNo');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAbortByStop.drainValve, Message := 'AbortByStop#6 drainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAbortByStop.airBlower, Message := 'AbortByStop#6 airBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAbortByStop.washPump, Message := 'AbortByStop#6 washPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAbortByStop.inletValve, Message := 'AbortByStop#6 inletValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAbortByStop.busy, Message := 'AbortByStop#6 busy');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAbortByStop.fault, Message := 'AbortByStop#6 fault');
    AssertEquals_INT(Expected := 0, Actual := fbAbortByStop.faultStep, Message := 'AbortByStop#6 faultStep');
    AssertEquals_DINT(Expected := 0, Actual := fbAbortByStop.cycleCount, Message := 'AbortByStop#6 cycleCount');
    AssertEquals_STRING(Expected := 'IDLE', Actual := fbAbortByStop.stepText, Message := 'AbortByStop#6 stepText');

    // #7, t = 13000 мс — новый фронт start: опорожнение
    GVL_S7Clock.tSimNow := T#13000MS;
    fbAbortByStop.start := TRUE;
    fbAbortByStop();
    AssertEquals_INT(Expected := 10, Actual := fbAbortByStop.stepNo, Message := 'AbortByStop#7 stepNo');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbAbortByStop.drainValve, Message := 'AbortByStop#7 drainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAbortByStop.airBlower, Message := 'AbortByStop#7 airBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAbortByStop.washPump, Message := 'AbortByStop#7 washPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAbortByStop.inletValve, Message := 'AbortByStop#7 inletValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbAbortByStop.busy, Message := 'AbortByStop#7 busy');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbAbortByStop.fault, Message := 'AbortByStop#7 fault');
    AssertEquals_INT(Expected := 0, Actual := fbAbortByStop.faultStep, Message := 'AbortByStop#7 faultStep');
    AssertEquals_DINT(Expected := 0, Actual := fbAbortByStop.cycleCount, Message := 'AbortByStop#7 cycleCount');
    AssertEquals_STRING(Expected := 'DRAIN', Actual := fbAbortByStop.stepText, Message := 'AbortByStop#7 stepText');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
