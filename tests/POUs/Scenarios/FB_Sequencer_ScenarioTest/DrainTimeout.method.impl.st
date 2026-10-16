// AUTO-GENERATED — не редактировать: scenarios/FB_Sequencer.csv, сценарий DrainTimeout
coUnit.TEST('DrainTimeout');
IF NOT xDrainTimeoutDone THEN
    xDrainTimeoutDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;

    // #1, t = 0 мс — ожидание
    GVL_S7Clock.tSimNow := T#0MS;
    fbDrainTimeout.start := FALSE;
    fbDrainTimeout.stop := FALSE;
    fbDrainTimeout.permissive := TRUE;
    fbDrainTimeout.levelLow := FALSE;
    fbDrainTimeout.levelHigh := FALSE;
    fbDrainTimeout.reset := FALSE;
    fbDrainTimeout.drainTimeout := T#60000MS;
    fbDrainTimeout.airTime := T#30000MS;
    fbDrainTimeout.washTime := T#40000MS;
    fbDrainTimeout.refillTimeout := T#90000MS;
    fbDrainTimeout();
    AssertEquals_INT(Expected := 0, Actual := fbDrainTimeout.stepNo, Message := 'DrainTimeout#1 stepNo');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDrainTimeout.drainValve, Message := 'DrainTimeout#1 drainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDrainTimeout.airBlower, Message := 'DrainTimeout#1 airBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDrainTimeout.washPump, Message := 'DrainTimeout#1 washPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDrainTimeout.inletValve, Message := 'DrainTimeout#1 inletValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDrainTimeout.busy, Message := 'DrainTimeout#1 busy');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDrainTimeout.fault, Message := 'DrainTimeout#1 fault');
    AssertEquals_INT(Expected := 0, Actual := fbDrainTimeout.faultStep, Message := 'DrainTimeout#1 faultStep');
    AssertEquals_DINT(Expected := 0, Actual := fbDrainTimeout.cycleCount, Message := 'DrainTimeout#1 cycleCount');
    AssertEquals_STRING(Expected := 'IDLE', Actual := fbDrainTimeout.stepText, Message := 'DrainTimeout#1 stepText');

    // #2, t = 1000 мс — пуск: опорожнение с 1.0 с
    GVL_S7Clock.tSimNow := T#1000MS;
    fbDrainTimeout.start := TRUE;
    fbDrainTimeout();
    AssertEquals_INT(Expected := 10, Actual := fbDrainTimeout.stepNo, Message := 'DrainTimeout#2 stepNo');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbDrainTimeout.drainValve, Message := 'DrainTimeout#2 drainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDrainTimeout.airBlower, Message := 'DrainTimeout#2 airBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDrainTimeout.washPump, Message := 'DrainTimeout#2 washPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDrainTimeout.inletValve, Message := 'DrainTimeout#2 inletValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbDrainTimeout.busy, Message := 'DrainTimeout#2 busy');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDrainTimeout.fault, Message := 'DrainTimeout#2 fault');
    AssertEquals_INT(Expected := 0, Actual := fbDrainTimeout.faultStep, Message := 'DrainTimeout#2 faultStep');
    AssertEquals_DINT(Expected := 0, Actual := fbDrainTimeout.cycleCount, Message := 'DrainTimeout#2 cycleCount');
    AssertEquals_STRING(Expected := 'DRAIN', Actual := fbDrainTimeout.stepText, Message := 'DrainTimeout#2 stepText');

    // #3, t = 60800 мс — 59.8 с < 60 с: опорожнение
    GVL_S7Clock.tSimNow := T#60800MS;
    fbDrainTimeout.start := FALSE;
    fbDrainTimeout();
    AssertEquals_INT(Expected := 10, Actual := fbDrainTimeout.stepNo, Message := 'DrainTimeout#3 stepNo');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbDrainTimeout.drainValve, Message := 'DrainTimeout#3 drainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDrainTimeout.airBlower, Message := 'DrainTimeout#3 airBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDrainTimeout.washPump, Message := 'DrainTimeout#3 washPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDrainTimeout.inletValve, Message := 'DrainTimeout#3 inletValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbDrainTimeout.busy, Message := 'DrainTimeout#3 busy');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDrainTimeout.fault, Message := 'DrainTimeout#3 fault');
    AssertEquals_INT(Expected := 0, Actual := fbDrainTimeout.faultStep, Message := 'DrainTimeout#3 faultStep');
    AssertEquals_DINT(Expected := 0, Actual := fbDrainTimeout.cycleCount, Message := 'DrainTimeout#3 cycleCount');
    AssertEquals_STRING(Expected := 'DRAIN', Actual := fbDrainTimeout.stepText, Message := 'DrainTimeout#3 stepText');

    // #4, t = 61200 мс — 60.2 с: авария на шаге 10, всё закрыто
    GVL_S7Clock.tSimNow := T#61200MS;
    fbDrainTimeout();
    AssertEquals_INT(Expected := 90, Actual := fbDrainTimeout.stepNo, Message := 'DrainTimeout#4 stepNo');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDrainTimeout.drainValve, Message := 'DrainTimeout#4 drainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDrainTimeout.airBlower, Message := 'DrainTimeout#4 airBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDrainTimeout.washPump, Message := 'DrainTimeout#4 washPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDrainTimeout.inletValve, Message := 'DrainTimeout#4 inletValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDrainTimeout.busy, Message := 'DrainTimeout#4 busy');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbDrainTimeout.fault, Message := 'DrainTimeout#4 fault');
    AssertEquals_INT(Expected := 10, Actual := fbDrainTimeout.faultStep, Message := 'DrainTimeout#4 faultStep');
    AssertEquals_DINT(Expected := 0, Actual := fbDrainTimeout.cycleCount, Message := 'DrainTimeout#4 cycleCount');
    AssertEquals_STRING(Expected := 'FAULT', Actual := fbDrainTimeout.stepText, Message := 'DrainTimeout#4 stepText');

    // #5, t = 65000 мс — пуск во время аварии не действует
    GVL_S7Clock.tSimNow := T#65000MS;
    fbDrainTimeout.start := TRUE;
    fbDrainTimeout();
    AssertEquals_INT(Expected := 90, Actual := fbDrainTimeout.stepNo, Message := 'DrainTimeout#5 stepNo');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDrainTimeout.drainValve, Message := 'DrainTimeout#5 drainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDrainTimeout.airBlower, Message := 'DrainTimeout#5 airBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDrainTimeout.washPump, Message := 'DrainTimeout#5 washPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDrainTimeout.inletValve, Message := 'DrainTimeout#5 inletValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDrainTimeout.busy, Message := 'DrainTimeout#5 busy');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbDrainTimeout.fault, Message := 'DrainTimeout#5 fault');
    AssertEquals_INT(Expected := 10, Actual := fbDrainTimeout.faultStep, Message := 'DrainTimeout#5 faultStep');
    AssertEquals_DINT(Expected := 0, Actual := fbDrainTimeout.cycleCount, Message := 'DrainTimeout#5 cycleCount');
    AssertEquals_STRING(Expected := 'FAULT', Actual := fbDrainTimeout.stepText, Message := 'DrainTimeout#5 stepText');

    // #6, t = 70000 мс — сброс: ожидание, faultStep 0
    GVL_S7Clock.tSimNow := T#70000MS;
    fbDrainTimeout.start := FALSE;
    fbDrainTimeout.reset := TRUE;
    fbDrainTimeout();
    AssertEquals_INT(Expected := 0, Actual := fbDrainTimeout.stepNo, Message := 'DrainTimeout#6 stepNo');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDrainTimeout.drainValve, Message := 'DrainTimeout#6 drainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDrainTimeout.airBlower, Message := 'DrainTimeout#6 airBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDrainTimeout.washPump, Message := 'DrainTimeout#6 washPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDrainTimeout.inletValve, Message := 'DrainTimeout#6 inletValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDrainTimeout.busy, Message := 'DrainTimeout#6 busy');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDrainTimeout.fault, Message := 'DrainTimeout#6 fault');
    AssertEquals_INT(Expected := 0, Actual := fbDrainTimeout.faultStep, Message := 'DrainTimeout#6 faultStep');
    AssertEquals_DINT(Expected := 0, Actual := fbDrainTimeout.cycleCount, Message := 'DrainTimeout#6 cycleCount');
    AssertEquals_STRING(Expected := 'IDLE', Actual := fbDrainTimeout.stepText, Message := 'DrainTimeout#6 stepText');

    // #7, t = 71000 мс — ожидание
    GVL_S7Clock.tSimNow := T#71000MS;
    fbDrainTimeout.reset := FALSE;
    fbDrainTimeout();
    AssertEquals_INT(Expected := 0, Actual := fbDrainTimeout.stepNo, Message := 'DrainTimeout#7 stepNo');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDrainTimeout.drainValve, Message := 'DrainTimeout#7 drainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDrainTimeout.airBlower, Message := 'DrainTimeout#7 airBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDrainTimeout.washPump, Message := 'DrainTimeout#7 washPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDrainTimeout.inletValve, Message := 'DrainTimeout#7 inletValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDrainTimeout.busy, Message := 'DrainTimeout#7 busy');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbDrainTimeout.fault, Message := 'DrainTimeout#7 fault');
    AssertEquals_INT(Expected := 0, Actual := fbDrainTimeout.faultStep, Message := 'DrainTimeout#7 faultStep');
    AssertEquals_DINT(Expected := 0, Actual := fbDrainTimeout.cycleCount, Message := 'DrainTimeout#7 cycleCount');
    AssertEquals_STRING(Expected := 'IDLE', Actual := fbDrainTimeout.stepText, Message := 'DrainTimeout#7 stepText');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
