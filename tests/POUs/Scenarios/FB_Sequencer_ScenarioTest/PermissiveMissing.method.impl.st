// AUTO-GENERATED — не редактировать: scenarios/FB_Sequencer.csv, сценарий PermissiveMissing
coUnit.TEST('PermissiveMissing');
IF NOT xPermissiveMissingDone THEN
    xPermissiveMissingDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;

    // #1, t = 0 мс — разрешения нет
    GVL_S7Clock.tSimNow := T#0MS;
    fbPermissiveMissing.start := FALSE;
    fbPermissiveMissing.stop := FALSE;
    fbPermissiveMissing.permissive := FALSE;
    fbPermissiveMissing.levelLow := FALSE;
    fbPermissiveMissing.levelHigh := FALSE;
    fbPermissiveMissing.reset := FALSE;
    fbPermissiveMissing.drainTimeout := T#60000MS;
    fbPermissiveMissing.airTime := T#30000MS;
    fbPermissiveMissing.washTime := T#40000MS;
    fbPermissiveMissing.refillTimeout := T#90000MS;
    fbPermissiveMissing();
    AssertEquals_INT(Expected := 0, Actual := fbPermissiveMissing.stepNo, Message := 'PermissiveMissing#1 stepNo');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbPermissiveMissing.drainValve,
                      Message := 'PermissiveMissing#1 drainValve');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbPermissiveMissing.airBlower,
                      Message := 'PermissiveMissing#1 airBlower');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbPermissiveMissing.washPump,
                      Message := 'PermissiveMissing#1 washPump');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbPermissiveMissing.inletValve,
                      Message := 'PermissiveMissing#1 inletValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbPermissiveMissing.busy, Message := 'PermissiveMissing#1 busy');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbPermissiveMissing.fault, Message := 'PermissiveMissing#1 fault');
    AssertEquals_INT(Expected := 0,
                     Actual := fbPermissiveMissing.faultStep,
                     Message := 'PermissiveMissing#1 faultStep');
    AssertEquals_DINT(Expected := 0,
                      Actual := fbPermissiveMissing.cycleCount,
                      Message := 'PermissiveMissing#1 cycleCount');
    AssertEquals_STRING(Expected := 'IDLE',
                        Actual := fbPermissiveMissing.stepText,
                        Message := 'PermissiveMissing#1 stepText');

    // #2, t = 1000 мс — фронт start без разрешения: ожидание
    GVL_S7Clock.tSimNow := T#1000MS;
    fbPermissiveMissing.start := TRUE;
    fbPermissiveMissing();
    AssertEquals_INT(Expected := 0, Actual := fbPermissiveMissing.stepNo, Message := 'PermissiveMissing#2 stepNo');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbPermissiveMissing.drainValve,
                      Message := 'PermissiveMissing#2 drainValve');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbPermissiveMissing.airBlower,
                      Message := 'PermissiveMissing#2 airBlower');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbPermissiveMissing.washPump,
                      Message := 'PermissiveMissing#2 washPump');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbPermissiveMissing.inletValve,
                      Message := 'PermissiveMissing#2 inletValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbPermissiveMissing.busy, Message := 'PermissiveMissing#2 busy');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbPermissiveMissing.fault, Message := 'PermissiveMissing#2 fault');
    AssertEquals_INT(Expected := 0,
                     Actual := fbPermissiveMissing.faultStep,
                     Message := 'PermissiveMissing#2 faultStep');
    AssertEquals_DINT(Expected := 0,
                      Actual := fbPermissiveMissing.cycleCount,
                      Message := 'PermissiveMissing#2 cycleCount');
    AssertEquals_STRING(Expected := 'IDLE',
                        Actual := fbPermissiveMissing.stepText,
                        Message := 'PermissiveMissing#2 stepText');

    // #3, t = 2000 мс — разрешение есть, start держится — фронта нет
    GVL_S7Clock.tSimNow := T#2000MS;
    fbPermissiveMissing.permissive := TRUE;
    fbPermissiveMissing();
    AssertEquals_INT(Expected := 0, Actual := fbPermissiveMissing.stepNo, Message := 'PermissiveMissing#3 stepNo');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbPermissiveMissing.drainValve,
                      Message := 'PermissiveMissing#3 drainValve');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbPermissiveMissing.airBlower,
                      Message := 'PermissiveMissing#3 airBlower');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbPermissiveMissing.washPump,
                      Message := 'PermissiveMissing#3 washPump');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbPermissiveMissing.inletValve,
                      Message := 'PermissiveMissing#3 inletValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbPermissiveMissing.busy, Message := 'PermissiveMissing#3 busy');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbPermissiveMissing.fault, Message := 'PermissiveMissing#3 fault');
    AssertEquals_INT(Expected := 0,
                     Actual := fbPermissiveMissing.faultStep,
                     Message := 'PermissiveMissing#3 faultStep');
    AssertEquals_DINT(Expected := 0,
                      Actual := fbPermissiveMissing.cycleCount,
                      Message := 'PermissiveMissing#3 cycleCount');
    AssertEquals_STRING(Expected := 'IDLE',
                        Actual := fbPermissiveMissing.stepText,
                        Message := 'PermissiveMissing#3 stepText');

    // #4, t = 3000 мс — start отпущен
    GVL_S7Clock.tSimNow := T#3000MS;
    fbPermissiveMissing.start := FALSE;
    fbPermissiveMissing();
    AssertEquals_INT(Expected := 0, Actual := fbPermissiveMissing.stepNo, Message := 'PermissiveMissing#4 stepNo');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbPermissiveMissing.drainValve,
                      Message := 'PermissiveMissing#4 drainValve');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbPermissiveMissing.airBlower,
                      Message := 'PermissiveMissing#4 airBlower');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbPermissiveMissing.washPump,
                      Message := 'PermissiveMissing#4 washPump');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbPermissiveMissing.inletValve,
                      Message := 'PermissiveMissing#4 inletValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbPermissiveMissing.busy, Message := 'PermissiveMissing#4 busy');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbPermissiveMissing.fault, Message := 'PermissiveMissing#4 fault');
    AssertEquals_INT(Expected := 0,
                     Actual := fbPermissiveMissing.faultStep,
                     Message := 'PermissiveMissing#4 faultStep');
    AssertEquals_DINT(Expected := 0,
                      Actual := fbPermissiveMissing.cycleCount,
                      Message := 'PermissiveMissing#4 cycleCount');
    AssertEquals_STRING(Expected := 'IDLE',
                        Actual := fbPermissiveMissing.stepText,
                        Message := 'PermissiveMissing#4 stepText');

    // #5, t = 4000 мс — новый фронт: опорожнение
    GVL_S7Clock.tSimNow := T#4000MS;
    fbPermissiveMissing.start := TRUE;
    fbPermissiveMissing();
    AssertEquals_INT(Expected := 10, Actual := fbPermissiveMissing.stepNo, Message := 'PermissiveMissing#5 stepNo');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbPermissiveMissing.drainValve,
                      Message := 'PermissiveMissing#5 drainValve');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbPermissiveMissing.airBlower,
                      Message := 'PermissiveMissing#5 airBlower');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbPermissiveMissing.washPump,
                      Message := 'PermissiveMissing#5 washPump');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbPermissiveMissing.inletValve,
                      Message := 'PermissiveMissing#5 inletValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbPermissiveMissing.busy, Message := 'PermissiveMissing#5 busy');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbPermissiveMissing.fault, Message := 'PermissiveMissing#5 fault');
    AssertEquals_INT(Expected := 0,
                     Actual := fbPermissiveMissing.faultStep,
                     Message := 'PermissiveMissing#5 faultStep');
    AssertEquals_DINT(Expected := 0,
                      Actual := fbPermissiveMissing.cycleCount,
                      Message := 'PermissiveMissing#5 cycleCount');
    AssertEquals_STRING(Expected := 'DRAIN',
                        Actual := fbPermissiveMissing.stepText,
                        Message := 'PermissiveMissing#5 stepText');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
