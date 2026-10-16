// AUTO-GENERATED — не редактировать: scenarios/FB_Sequencer.csv, сценарий FullCycle
coUnit.TEST('FullCycle');
IF NOT xFullCycleDone THEN
    xFullCycleDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;

    // #1, t = 0 мс — ожидание
    GVL_S7Clock.tSimNow := T#0MS;
    fbFullCycle.start := FALSE;
    fbFullCycle.stop := FALSE;
    fbFullCycle.permissive := TRUE;
    fbFullCycle.levelLow := FALSE;
    fbFullCycle.levelHigh := FALSE;
    fbFullCycle.reset := FALSE;
    fbFullCycle.drainTimeout := T#60000MS;
    fbFullCycle.airTime := T#30000MS;
    fbFullCycle.washTime := T#40000MS;
    fbFullCycle.refillTimeout := T#90000MS;
    fbFullCycle();
    AssertEquals_INT(Expected := 0, Actual := fbFullCycle.stepNo, Message := 'FullCycle#1 stepNo');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFullCycle.drainValve, Message := 'FullCycle#1 drainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFullCycle.airBlower, Message := 'FullCycle#1 airBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFullCycle.washPump, Message := 'FullCycle#1 washPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFullCycle.inletValve, Message := 'FullCycle#1 inletValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFullCycle.busy, Message := 'FullCycle#1 busy');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFullCycle.fault, Message := 'FullCycle#1 fault');
    AssertEquals_INT(Expected := 0, Actual := fbFullCycle.faultStep, Message := 'FullCycle#1 faultStep');
    AssertEquals_DINT(Expected := 0, Actual := fbFullCycle.cycleCount, Message := 'FullCycle#1 cycleCount');
    AssertEquals_STRING(Expected := 'IDLE', Actual := fbFullCycle.stepText, Message := 'FullCycle#1 stepText');

    // #2, t = 1000 мс — пуск: опорожнение, шаг 10 с 1.0 с
    GVL_S7Clock.tSimNow := T#1000MS;
    fbFullCycle.start := TRUE;
    fbFullCycle();
    AssertEquals_INT(Expected := 10, Actual := fbFullCycle.stepNo, Message := 'FullCycle#2 stepNo');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbFullCycle.drainValve, Message := 'FullCycle#2 drainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFullCycle.airBlower, Message := 'FullCycle#2 airBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFullCycle.washPump, Message := 'FullCycle#2 washPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFullCycle.inletValve, Message := 'FullCycle#2 inletValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbFullCycle.busy, Message := 'FullCycle#2 busy');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFullCycle.fault, Message := 'FullCycle#2 fault');
    AssertEquals_INT(Expected := 0, Actual := fbFullCycle.faultStep, Message := 'FullCycle#2 faultStep');
    AssertEquals_DINT(Expected := 0, Actual := fbFullCycle.cycleCount, Message := 'FullCycle#2 cycleCount');
    AssertEquals_STRING(Expected := 'DRAIN', Actual := fbFullCycle.stepText, Message := 'FullCycle#2 stepText');

    // #3, t = 1500 мс — опорожнение
    GVL_S7Clock.tSimNow := T#1500MS;
    fbFullCycle.start := FALSE;
    fbFullCycle();
    AssertEquals_INT(Expected := 10, Actual := fbFullCycle.stepNo, Message := 'FullCycle#3 stepNo');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbFullCycle.drainValve, Message := 'FullCycle#3 drainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFullCycle.airBlower, Message := 'FullCycle#3 airBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFullCycle.washPump, Message := 'FullCycle#3 washPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFullCycle.inletValve, Message := 'FullCycle#3 inletValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbFullCycle.busy, Message := 'FullCycle#3 busy');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFullCycle.fault, Message := 'FullCycle#3 fault');
    AssertEquals_INT(Expected := 0, Actual := fbFullCycle.faultStep, Message := 'FullCycle#3 faultStep');
    AssertEquals_DINT(Expected := 0, Actual := fbFullCycle.cycleCount, Message := 'FullCycle#3 cycleCount');
    AssertEquals_STRING(Expected := 'DRAIN', Actual := fbFullCycle.stepText, Message := 'FullCycle#3 stepText');

    // #4, t = 21000 мс — фильтр опорожнён: продувка, шаг 20 с 21.0 с
    GVL_S7Clock.tSimNow := T#21000MS;
    fbFullCycle.levelLow := TRUE;
    fbFullCycle();
    AssertEquals_INT(Expected := 20, Actual := fbFullCycle.stepNo, Message := 'FullCycle#4 stepNo');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFullCycle.drainValve, Message := 'FullCycle#4 drainValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbFullCycle.airBlower, Message := 'FullCycle#4 airBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFullCycle.washPump, Message := 'FullCycle#4 washPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFullCycle.inletValve, Message := 'FullCycle#4 inletValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbFullCycle.busy, Message := 'FullCycle#4 busy');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFullCycle.fault, Message := 'FullCycle#4 fault');
    AssertEquals_INT(Expected := 0, Actual := fbFullCycle.faultStep, Message := 'FullCycle#4 faultStep');
    AssertEquals_DINT(Expected := 0, Actual := fbFullCycle.cycleCount, Message := 'FullCycle#4 cycleCount');
    AssertEquals_STRING(Expected := 'AIR SCOUR', Actual := fbFullCycle.stepText, Message := 'FullCycle#4 stepText');

    // #5, t = 50800 мс — продувка 29.8 с < 30 с
    GVL_S7Clock.tSimNow := T#50800MS;
    fbFullCycle();
    AssertEquals_INT(Expected := 20, Actual := fbFullCycle.stepNo, Message := 'FullCycle#5 stepNo');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFullCycle.drainValve, Message := 'FullCycle#5 drainValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbFullCycle.airBlower, Message := 'FullCycle#5 airBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFullCycle.washPump, Message := 'FullCycle#5 washPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFullCycle.inletValve, Message := 'FullCycle#5 inletValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbFullCycle.busy, Message := 'FullCycle#5 busy');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFullCycle.fault, Message := 'FullCycle#5 fault');
    AssertEquals_INT(Expected := 0, Actual := fbFullCycle.faultStep, Message := 'FullCycle#5 faultStep');
    AssertEquals_DINT(Expected := 0, Actual := fbFullCycle.cycleCount, Message := 'FullCycle#5 cycleCount');
    AssertEquals_STRING(Expected := 'AIR SCOUR', Actual := fbFullCycle.stepText, Message := 'FullCycle#5 stepText');

    // #6, t = 51200 мс — 30.2 с: промывка, шаг 30 с 51.2 с
    GVL_S7Clock.tSimNow := T#51200MS;
    fbFullCycle();
    AssertEquals_INT(Expected := 30, Actual := fbFullCycle.stepNo, Message := 'FullCycle#6 stepNo');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbFullCycle.drainValve, Message := 'FullCycle#6 drainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFullCycle.airBlower, Message := 'FullCycle#6 airBlower');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbFullCycle.washPump, Message := 'FullCycle#6 washPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFullCycle.inletValve, Message := 'FullCycle#6 inletValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbFullCycle.busy, Message := 'FullCycle#6 busy');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFullCycle.fault, Message := 'FullCycle#6 fault');
    AssertEquals_INT(Expected := 0, Actual := fbFullCycle.faultStep, Message := 'FullCycle#6 faultStep');
    AssertEquals_DINT(Expected := 0, Actual := fbFullCycle.cycleCount, Message := 'FullCycle#6 cycleCount');
    AssertEquals_STRING(Expected := 'BACKWASH', Actual := fbFullCycle.stepText, Message := 'FullCycle#6 stepText');

    // #7, t = 91000 мс — промывка 39.8 с < 40 с
    GVL_S7Clock.tSimNow := T#91000MS;
    fbFullCycle.levelLow := FALSE;
    fbFullCycle();
    AssertEquals_INT(Expected := 30, Actual := fbFullCycle.stepNo, Message := 'FullCycle#7 stepNo');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbFullCycle.drainValve, Message := 'FullCycle#7 drainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFullCycle.airBlower, Message := 'FullCycle#7 airBlower');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbFullCycle.washPump, Message := 'FullCycle#7 washPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFullCycle.inletValve, Message := 'FullCycle#7 inletValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbFullCycle.busy, Message := 'FullCycle#7 busy');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFullCycle.fault, Message := 'FullCycle#7 fault');
    AssertEquals_INT(Expected := 0, Actual := fbFullCycle.faultStep, Message := 'FullCycle#7 faultStep');
    AssertEquals_DINT(Expected := 0, Actual := fbFullCycle.cycleCount, Message := 'FullCycle#7 cycleCount');
    AssertEquals_STRING(Expected := 'BACKWASH', Actual := fbFullCycle.stepText, Message := 'FullCycle#7 stepText');

    // #8, t = 91400 мс — 40.2 с: заполнение, шаг 40 с 91.4 с
    GVL_S7Clock.tSimNow := T#91400MS;
    fbFullCycle();
    AssertEquals_INT(Expected := 40, Actual := fbFullCycle.stepNo, Message := 'FullCycle#8 stepNo');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFullCycle.drainValve, Message := 'FullCycle#8 drainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFullCycle.airBlower, Message := 'FullCycle#8 airBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFullCycle.washPump, Message := 'FullCycle#8 washPump');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbFullCycle.inletValve, Message := 'FullCycle#8 inletValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbFullCycle.busy, Message := 'FullCycle#8 busy');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFullCycle.fault, Message := 'FullCycle#8 fault');
    AssertEquals_INT(Expected := 0, Actual := fbFullCycle.faultStep, Message := 'FullCycle#8 faultStep');
    AssertEquals_DINT(Expected := 0, Actual := fbFullCycle.cycleCount, Message := 'FullCycle#8 cycleCount');
    AssertEquals_STRING(Expected := 'REFILL', Actual := fbFullCycle.stepText, Message := 'FullCycle#8 stepText');

    // #9, t = 150000 мс — заполнение 58.6 с, уровня нет
    GVL_S7Clock.tSimNow := T#150000MS;
    fbFullCycle();
    AssertEquals_INT(Expected := 40, Actual := fbFullCycle.stepNo, Message := 'FullCycle#9 stepNo');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFullCycle.drainValve, Message := 'FullCycle#9 drainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFullCycle.airBlower, Message := 'FullCycle#9 airBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFullCycle.washPump, Message := 'FullCycle#9 washPump');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbFullCycle.inletValve, Message := 'FullCycle#9 inletValve');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbFullCycle.busy, Message := 'FullCycle#9 busy');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFullCycle.fault, Message := 'FullCycle#9 fault');
    AssertEquals_INT(Expected := 0, Actual := fbFullCycle.faultStep, Message := 'FullCycle#9 faultStep');
    AssertEquals_DINT(Expected := 0, Actual := fbFullCycle.cycleCount, Message := 'FullCycle#9 cycleCount');
    AssertEquals_STRING(Expected := 'REFILL', Actual := fbFullCycle.stepText, Message := 'FullCycle#9 stepText');

    // #10, t = 160000 мс — фильтр заполнен: цикл №1 завершён
    GVL_S7Clock.tSimNow := T#160000MS;
    fbFullCycle.levelHigh := TRUE;
    fbFullCycle();
    AssertEquals_INT(Expected := 0, Actual := fbFullCycle.stepNo, Message := 'FullCycle#10 stepNo');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFullCycle.drainValve, Message := 'FullCycle#10 drainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFullCycle.airBlower, Message := 'FullCycle#10 airBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFullCycle.washPump, Message := 'FullCycle#10 washPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFullCycle.inletValve, Message := 'FullCycle#10 inletValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFullCycle.busy, Message := 'FullCycle#10 busy');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFullCycle.fault, Message := 'FullCycle#10 fault');
    AssertEquals_INT(Expected := 0, Actual := fbFullCycle.faultStep, Message := 'FullCycle#10 faultStep');
    AssertEquals_DINT(Expected := 1, Actual := fbFullCycle.cycleCount, Message := 'FullCycle#10 cycleCount');
    AssertEquals_STRING(Expected := 'IDLE', Actual := fbFullCycle.stepText, Message := 'FullCycle#10 stepText');

    // #11, t = 161000 мс — ожидание, повторного пуска без фронта start нет
    GVL_S7Clock.tSimNow := T#161000MS;
    fbFullCycle();
    AssertEquals_INT(Expected := 0, Actual := fbFullCycle.stepNo, Message := 'FullCycle#11 stepNo');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFullCycle.drainValve, Message := 'FullCycle#11 drainValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFullCycle.airBlower, Message := 'FullCycle#11 airBlower');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFullCycle.washPump, Message := 'FullCycle#11 washPump');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFullCycle.inletValve, Message := 'FullCycle#11 inletValve');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFullCycle.busy, Message := 'FullCycle#11 busy');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbFullCycle.fault, Message := 'FullCycle#11 fault');
    AssertEquals_INT(Expected := 0, Actual := fbFullCycle.faultStep, Message := 'FullCycle#11 faultStep');
    AssertEquals_DINT(Expected := 1, Actual := fbFullCycle.cycleCount, Message := 'FullCycle#11 cycleCount');
    AssertEquals_STRING(Expected := 'IDLE', Actual := fbFullCycle.stepText, Message := 'FullCycle#11 stepText');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
