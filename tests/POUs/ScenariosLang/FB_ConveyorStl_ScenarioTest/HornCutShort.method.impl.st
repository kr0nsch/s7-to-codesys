// AUTO-GENERATED — не редактировать: scenarios/lang/FB_ConveyorStl.csv, сценарий HornCutShort
coUnit.TEST('HornCutShort');
IF NOT xHornCutShortDone THEN
    xHornCutShortDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;
    // слова S5 — глобальные (GVL_S5Timers_Lang): сценарий начинается с чистых таймеров и счётчиков
    FOR iS5 := 0 TO 5 DO
        GVL_S5Timers_Lang.aTimer[iS5] := stTimerZero;
    END_FOR
    // слова S5 — глобальные (GVL_S5Counters_Lang): сценарий начинается с чистых таймеров и счётчиков
    FOR iS5 := 0 TO 1 DO
        GVL_S5Counters_Lang.aCounter[iS5] := stCounterZero;
    END_FOR

    // #1, t = 0 мс — пуск: сирена, остаток 200
    GVL_S7Clock.tSimNow := T#0MS;
    fbHornCutShort.xStart := TRUE;
    fbHornCutShort.xStop := FALSE;
    fbHornCutShort.xSensor := FALSE;
    fbHornCutShort.xAck := FALSE;
    fbHornCutShort.xCountReset := FALSE;
    fbHornCutShort();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbHornCutShort.xHorn, Message := 'HornCutShort#1 xHorn');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbHornCutShort.xMotor, Message := 'HornCutShort#1 xMotor');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbHornCutShort.xFlowOk, Message := 'HornCutShort#1 xFlowOk');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbHornCutShort.xJam, Message := 'HornCutShort#1 xJam');
    AssertEquals_INT(Expected := 200, Actual := fbHornCutShort.iDelayLeft, Message := 'HornCutShort#1 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0000, Actual := fbHornCutShort.wRunOutBcd, Message := 'HornCutShort#1 wRunOutBcd');
    AssertEquals_INT(Expected := 0, Actual := fbHornCutShort.iCount, Message := 'HornCutShort#1 iCount');
    AssertEquals_WORD(Expected := 16#0000, Actual := fbHornCutShort.wCountBcd, Message := 'HornCutShort#1 wCountBcd');

    // #2, t = 300 мс — стоп: сирена оборвана, T2 остановлен с остатком 170
    GVL_S7Clock.tSimNow := T#300MS;
    fbHornCutShort.xStart := FALSE;
    fbHornCutShort.xStop := TRUE;
    fbHornCutShort();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbHornCutShort.xHorn, Message := 'HornCutShort#2 xHorn');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbHornCutShort.xMotor, Message := 'HornCutShort#2 xMotor');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbHornCutShort.xFlowOk, Message := 'HornCutShort#2 xFlowOk');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbHornCutShort.xJam, Message := 'HornCutShort#2 xJam');
    AssertEquals_INT(Expected := 170, Actual := fbHornCutShort.iDelayLeft, Message := 'HornCutShort#2 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0000, Actual := fbHornCutShort.wRunOutBcd, Message := 'HornCutShort#2 wRunOutBcd');
    AssertEquals_INT(Expected := 0, Actual := fbHornCutShort.iCount, Message := 'HornCutShort#2 iCount');
    AssertEquals_WORD(Expected := 16#0000, Actual := fbHornCutShort.wCountBcd, Message := 'HornCutShort#2 wCountBcd');

    // #3, t = 400 мс — остаток 170 сохраняется
    GVL_S7Clock.tSimNow := T#400MS;
    fbHornCutShort.xStop := FALSE;
    fbHornCutShort();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbHornCutShort.xHorn, Message := 'HornCutShort#3 xHorn');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbHornCutShort.xMotor, Message := 'HornCutShort#3 xMotor');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbHornCutShort.xFlowOk, Message := 'HornCutShort#3 xFlowOk');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbHornCutShort.xJam, Message := 'HornCutShort#3 xJam');
    AssertEquals_INT(Expected := 170, Actual := fbHornCutShort.iDelayLeft, Message := 'HornCutShort#3 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0000, Actual := fbHornCutShort.wRunOutBcd, Message := 'HornCutShort#3 wRunOutBcd');
    AssertEquals_INT(Expected := 0, Actual := fbHornCutShort.iCount, Message := 'HornCutShort#3 iCount');
    AssertEquals_WORD(Expected := 16#0000, Actual := fbHornCutShort.wCountBcd, Message := 'HornCutShort#3 wCountBcd');

    // #4, t = 5000 мс — остаток 170 сохраняется
    GVL_S7Clock.tSimNow := T#5000MS;
    fbHornCutShort();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbHornCutShort.xHorn, Message := 'HornCutShort#4 xHorn');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbHornCutShort.xMotor, Message := 'HornCutShort#4 xMotor');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbHornCutShort.xFlowOk, Message := 'HornCutShort#4 xFlowOk');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbHornCutShort.xJam, Message := 'HornCutShort#4 xJam');
    AssertEquals_INT(Expected := 170, Actual := fbHornCutShort.iDelayLeft, Message := 'HornCutShort#4 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0000, Actual := fbHornCutShort.wRunOutBcd, Message := 'HornCutShort#4 wRunOutBcd');
    AssertEquals_INT(Expected := 0, Actual := fbHornCutShort.iCount, Message := 'HornCutShort#4 iCount');
    AssertEquals_WORD(Expected := 16#0000, Actual := fbHornCutShort.wCountBcd, Message := 'HornCutShort#4 wCountBcd');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
