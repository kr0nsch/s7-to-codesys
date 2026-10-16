// AUTO-GENERATED — не редактировать: scenarios/FB_Sequencer.csv, сценарий DrainTimeoutBoundary
coUnit.TEST('DrainTimeoutBoundary');
IF NOT xDrainTimeoutBoundaryDone THEN
    xDrainTimeoutBoundaryDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;

    // #1, t = 0 мс — пуск в первом вызове: опорожнение с 0 с
    GVL_S7Clock.tSimNow := T#0MS;
    fbDrainTimeoutBoundary.start := TRUE;
    fbDrainTimeoutBoundary.stop := FALSE;
    fbDrainTimeoutBoundary.permissive := TRUE;
    fbDrainTimeoutBoundary.levelLow := FALSE;
    fbDrainTimeoutBoundary.levelHigh := FALSE;
    fbDrainTimeoutBoundary.reset := FALSE;
    fbDrainTimeoutBoundary.drainTimeout := T#60000MS;
    fbDrainTimeoutBoundary.airTime := T#30000MS;
    fbDrainTimeoutBoundary.washTime := T#40000MS;
    fbDrainTimeoutBoundary.refillTimeout := T#90000MS;
    fbDrainTimeoutBoundary();
    AssertEquals_INT(Expected := 10,
                     Actual := fbDrainTimeoutBoundary.stepNo,
                     Message := 'DrainTimeoutBoundary#1 stepNo');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbDrainTimeoutBoundary.drainValve,
                      Message := 'DrainTimeoutBoundary#1 drainValve');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbDrainTimeoutBoundary.airBlower,
                      Message := 'DrainTimeoutBoundary#1 airBlower');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbDrainTimeoutBoundary.washPump,
                      Message := 'DrainTimeoutBoundary#1 washPump');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbDrainTimeoutBoundary.inletValve,
                      Message := 'DrainTimeoutBoundary#1 inletValve');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbDrainTimeoutBoundary.busy,
                      Message := 'DrainTimeoutBoundary#1 busy');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbDrainTimeoutBoundary.fault,
                      Message := 'DrainTimeoutBoundary#1 fault');
    AssertEquals_INT(Expected := 0,
                     Actual := fbDrainTimeoutBoundary.faultStep,
                     Message := 'DrainTimeoutBoundary#1 faultStep');
    AssertEquals_DINT(Expected := 0,
                      Actual := fbDrainTimeoutBoundary.cycleCount,
                      Message := 'DrainTimeoutBoundary#1 cycleCount');
    AssertEquals_STRING(Expected := 'DRAIN',
                        Actual := fbDrainTimeoutBoundary.stepText,
                        Message := 'DrainTimeoutBoundary#1 stepText');

    // #2, t = 59800 мс — 59.8 с: опорожнение
    GVL_S7Clock.tSimNow := T#59800MS;
    fbDrainTimeoutBoundary.start := FALSE;
    fbDrainTimeoutBoundary();
    AssertEquals_INT(Expected := 10,
                     Actual := fbDrainTimeoutBoundary.stepNo,
                     Message := 'DrainTimeoutBoundary#2 stepNo');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbDrainTimeoutBoundary.drainValve,
                      Message := 'DrainTimeoutBoundary#2 drainValve');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbDrainTimeoutBoundary.airBlower,
                      Message := 'DrainTimeoutBoundary#2 airBlower');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbDrainTimeoutBoundary.washPump,
                      Message := 'DrainTimeoutBoundary#2 washPump');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbDrainTimeoutBoundary.inletValve,
                      Message := 'DrainTimeoutBoundary#2 inletValve');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbDrainTimeoutBoundary.busy,
                      Message := 'DrainTimeoutBoundary#2 busy');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbDrainTimeoutBoundary.fault,
                      Message := 'DrainTimeoutBoundary#2 fault');
    AssertEquals_INT(Expected := 0,
                     Actual := fbDrainTimeoutBoundary.faultStep,
                     Message := 'DrainTimeoutBoundary#2 faultStep');
    AssertEquals_DINT(Expected := 0,
                      Actual := fbDrainTimeoutBoundary.cycleCount,
                      Message := 'DrainTimeoutBoundary#2 cycleCount');
    AssertEquals_STRING(Expected := 'DRAIN',
                        Actual := fbDrainTimeoutBoundary.stepText,
                        Message := 'DrainTimeoutBoundary#2 stepText');

    // #3, t = 60000 мс, на пороге таймера — 60.0 с = drainTimeout: авария
    GVL_S7Clock.tSimNow := T#60000MS;
    fbDrainTimeoutBoundary();
    AssertEquals_INT(Expected := 90,
                     Actual := fbDrainTimeoutBoundary.stepNo,
                     Message := 'DrainTimeoutBoundary#3 stepNo');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbDrainTimeoutBoundary.drainValve,
                      Message := 'DrainTimeoutBoundary#3 drainValve');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbDrainTimeoutBoundary.airBlower,
                      Message := 'DrainTimeoutBoundary#3 airBlower');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbDrainTimeoutBoundary.washPump,
                      Message := 'DrainTimeoutBoundary#3 washPump');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbDrainTimeoutBoundary.inletValve,
                      Message := 'DrainTimeoutBoundary#3 inletValve');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbDrainTimeoutBoundary.busy,
                      Message := 'DrainTimeoutBoundary#3 busy');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbDrainTimeoutBoundary.fault,
                      Message := 'DrainTimeoutBoundary#3 fault');
    AssertEquals_INT(Expected := 10,
                     Actual := fbDrainTimeoutBoundary.faultStep,
                     Message := 'DrainTimeoutBoundary#3 faultStep');
    AssertEquals_DINT(Expected := 0,
                      Actual := fbDrainTimeoutBoundary.cycleCount,
                      Message := 'DrainTimeoutBoundary#3 cycleCount');
    AssertEquals_STRING(Expected := 'FAULT',
                        Actual := fbDrainTimeoutBoundary.stepText,
                        Message := 'DrainTimeoutBoundary#3 stepText');

    // #4, t = 60200 мс — авария
    GVL_S7Clock.tSimNow := T#60200MS;
    fbDrainTimeoutBoundary();
    AssertEquals_INT(Expected := 90,
                     Actual := fbDrainTimeoutBoundary.stepNo,
                     Message := 'DrainTimeoutBoundary#4 stepNo');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbDrainTimeoutBoundary.drainValve,
                      Message := 'DrainTimeoutBoundary#4 drainValve');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbDrainTimeoutBoundary.airBlower,
                      Message := 'DrainTimeoutBoundary#4 airBlower');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbDrainTimeoutBoundary.washPump,
                      Message := 'DrainTimeoutBoundary#4 washPump');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbDrainTimeoutBoundary.inletValve,
                      Message := 'DrainTimeoutBoundary#4 inletValve');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbDrainTimeoutBoundary.busy,
                      Message := 'DrainTimeoutBoundary#4 busy');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbDrainTimeoutBoundary.fault,
                      Message := 'DrainTimeoutBoundary#4 fault');
    AssertEquals_INT(Expected := 10,
                     Actual := fbDrainTimeoutBoundary.faultStep,
                     Message := 'DrainTimeoutBoundary#4 faultStep');
    AssertEquals_DINT(Expected := 0,
                      Actual := fbDrainTimeoutBoundary.cycleCount,
                      Message := 'DrainTimeoutBoundary#4 cycleCount');
    AssertEquals_STRING(Expected := 'FAULT',
                        Actual := fbDrainTimeoutBoundary.stepText,
                        Message := 'DrainTimeoutBoundary#4 stepText');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
