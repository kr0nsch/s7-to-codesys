// AUTO-GENERATED — не редактировать: scenarios/lang/FB_ConveyorStl.csv, сценарий StopRunOut
coUnit.TEST('StopRunOut');
IF NOT xStopRunOutDone THEN
    xStopRunOutDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;
    // слова S5 — глобальные (GVL_S5Timers_Lang): сценарий начинается с чистых таймеров и счётчиков
    FOR iS5 := 0 TO 5 DO
        GVL_S5Timers_Lang.aTimer[iS5] := stTimerZero;
    END_FOR
    // слова S5 — глобальные (GVL_S5Counters_Lang): сценарий начинается с чистых таймеров и счётчиков
    FOR iS5 := 0 TO 1 DO
        GVL_S5Counters_Lang.aCounter[iS5] := stCounterZero;
    END_FOR

    // #1, t = 0 мс — пуск: запрос, сирена T1 и задержка T2 пошли
    GVL_S7Clock.tSimNow := T#0MS;
    fbStopRunOut.xStart := TRUE;
    fbStopRunOut.xStop := FALSE;
    fbStopRunOut.xSensor := FALSE;
    fbStopRunOut.xAck := FALSE;
    fbStopRunOut.xCountReset := FALSE;
    fbStopRunOut();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbStopRunOut.xHorn, Message := 'StopRunOut#1 xHorn');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStopRunOut.xMotor, Message := 'StopRunOut#1 xMotor');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStopRunOut.xFlowOk, Message := 'StopRunOut#1 xFlowOk');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStopRunOut.xJam, Message := 'StopRunOut#1 xJam');
    AssertEquals_INT(Expected := 200, Actual := fbStopRunOut.iDelayLeft, Message := 'StopRunOut#1 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0000, Actual := fbStopRunOut.wRunOutBcd, Message := 'StopRunOut#1 wRunOutBcd');
    AssertEquals_INT(Expected := 0, Actual := fbStopRunOut.iCount, Message := 'StopRunOut#1 iCount');
    AssertEquals_WORD(Expected := 16#0000, Actual := fbStopRunOut.wCountBcd, Message := 'StopRunOut#1 wCountBcd');

    // #2, t = 100 мс — кнопка отпущена
    GVL_S7Clock.tSimNow := T#100MS;
    fbStopRunOut.xStart := FALSE;
    fbStopRunOut();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbStopRunOut.xHorn, Message := 'StopRunOut#2 xHorn');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStopRunOut.xMotor, Message := 'StopRunOut#2 xMotor');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStopRunOut.xFlowOk, Message := 'StopRunOut#2 xFlowOk');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStopRunOut.xJam, Message := 'StopRunOut#2 xJam');
    AssertEquals_INT(Expected := 190, Actual := fbStopRunOut.iDelayLeft, Message := 'StopRunOut#2 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0000, Actual := fbStopRunOut.wRunOutBcd, Message := 'StopRunOut#2 wRunOutBcd');
    AssertEquals_INT(Expected := 0, Actual := fbStopRunOut.iCount, Message := 'StopRunOut#2 iCount');
    AssertEquals_WORD(Expected := 16#0000, Actual := fbStopRunOut.wCountBcd, Message := 'StopRunOut#2 wCountBcd');

    // #3, t = 2000 мс, на пороге таймера — 2 с: задержка T2 истекла — двигатель (T3 = 1)
    GVL_S7Clock.tSimNow := T#2000MS;
    fbStopRunOut();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStopRunOut.xHorn, Message := 'StopRunOut#3 xHorn');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbStopRunOut.xMotor, Message := 'StopRunOut#3 xMotor');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStopRunOut.xFlowOk, Message := 'StopRunOut#3 xFlowOk');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStopRunOut.xJam, Message := 'StopRunOut#3 xJam');
    AssertEquals_INT(Expected := 0, Actual := fbStopRunOut.iDelayLeft, Message := 'StopRunOut#3 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0000, Actual := fbStopRunOut.wRunOutBcd, Message := 'StopRunOut#3 wRunOutBcd');
    AssertEquals_INT(Expected := 0, Actual := fbStopRunOut.iCount, Message := 'StopRunOut#3 iCount');
    AssertEquals_WORD(Expected := 16#0000, Actual := fbStopRunOut.wCountBcd, Message := 'StopRunOut#3 wCountBcd');

    // #4, t = 3000 мс — стоп: запрос снят, выбег T3 пошёл, 16#0300
    GVL_S7Clock.tSimNow := T#3000MS;
    fbStopRunOut.xStop := TRUE;
    fbStopRunOut();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStopRunOut.xHorn, Message := 'StopRunOut#4 xHorn');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbStopRunOut.xMotor, Message := 'StopRunOut#4 xMotor');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStopRunOut.xFlowOk, Message := 'StopRunOut#4 xFlowOk');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStopRunOut.xJam, Message := 'StopRunOut#4 xJam');
    AssertEquals_INT(Expected := 0, Actual := fbStopRunOut.iDelayLeft, Message := 'StopRunOut#4 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0300, Actual := fbStopRunOut.wRunOutBcd, Message := 'StopRunOut#4 wRunOutBcd');
    AssertEquals_INT(Expected := 0, Actual := fbStopRunOut.iCount, Message := 'StopRunOut#4 iCount');
    AssertEquals_WORD(Expected := 16#0000, Actual := fbStopRunOut.wCountBcd, Message := 'StopRunOut#4 wCountBcd');

    // #5, t = 3100 мс — выбег: остаток 290 единиц
    GVL_S7Clock.tSimNow := T#3100MS;
    fbStopRunOut.xStop := FALSE;
    fbStopRunOut();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStopRunOut.xHorn, Message := 'StopRunOut#5 xHorn');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbStopRunOut.xMotor, Message := 'StopRunOut#5 xMotor');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStopRunOut.xFlowOk, Message := 'StopRunOut#5 xFlowOk');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStopRunOut.xJam, Message := 'StopRunOut#5 xJam');
    AssertEquals_INT(Expected := 0, Actual := fbStopRunOut.iDelayLeft, Message := 'StopRunOut#5 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0290, Actual := fbStopRunOut.wRunOutBcd, Message := 'StopRunOut#5 wRunOutBcd');
    AssertEquals_INT(Expected := 0, Actual := fbStopRunOut.iCount, Message := 'StopRunOut#5 iCount');
    AssertEquals_WORD(Expected := 16#0000, Actual := fbStopRunOut.wCountBcd, Message := 'StopRunOut#5 wCountBcd');

    // #6, t = 4500 мс — выбег: остаток 150 единиц
    GVL_S7Clock.tSimNow := T#4500MS;
    fbStopRunOut();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStopRunOut.xHorn, Message := 'StopRunOut#6 xHorn');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbStopRunOut.xMotor, Message := 'StopRunOut#6 xMotor');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStopRunOut.xFlowOk, Message := 'StopRunOut#6 xFlowOk');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStopRunOut.xJam, Message := 'StopRunOut#6 xJam');
    AssertEquals_INT(Expected := 0, Actual := fbStopRunOut.iDelayLeft, Message := 'StopRunOut#6 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0150, Actual := fbStopRunOut.wRunOutBcd, Message := 'StopRunOut#6 wRunOutBcd');
    AssertEquals_INT(Expected := 0, Actual := fbStopRunOut.iCount, Message := 'StopRunOut#6 iCount');
    AssertEquals_WORD(Expected := 16#0000, Actual := fbStopRunOut.wCountBcd, Message := 'StopRunOut#6 wCountBcd');

    // #7, t = 6000 мс, на пороге таймера — 3 с выбега: двигатель остановлен
    GVL_S7Clock.tSimNow := T#6000MS;
    fbStopRunOut();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStopRunOut.xHorn, Message := 'StopRunOut#7 xHorn');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStopRunOut.xMotor, Message := 'StopRunOut#7 xMotor');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStopRunOut.xFlowOk, Message := 'StopRunOut#7 xFlowOk');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStopRunOut.xJam, Message := 'StopRunOut#7 xJam');
    AssertEquals_INT(Expected := 0, Actual := fbStopRunOut.iDelayLeft, Message := 'StopRunOut#7 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0000, Actual := fbStopRunOut.wRunOutBcd, Message := 'StopRunOut#7 wRunOutBcd');
    AssertEquals_INT(Expected := 0, Actual := fbStopRunOut.iCount, Message := 'StopRunOut#7 iCount');
    AssertEquals_WORD(Expected := 16#0000, Actual := fbStopRunOut.wCountBcd, Message := 'StopRunOut#7 wCountBcd');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
