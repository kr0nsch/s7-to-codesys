// AUTO-GENERATED — не редактировать: scenarios/lang/FB_ConveyorStl.csv, сценарий StartSequence
coUnit.TEST('StartSequence');
IF NOT xStartSequenceDone THEN
    xStartSequenceDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;
    // слова S5 — глобальные (GVL_S5Timers_Lang): сценарий начинается с чистых таймеров и счётчиков
    FOR iS5 := 0 TO 5 DO
        GVL_S5Timers_Lang.aTimer[iS5] := stTimerZero;
    END_FOR
    // слова S5 — глобальные (GVL_S5Counters_Lang): сценарий начинается с чистых таймеров и счётчиков
    FOR iS5 := 0 TO 1 DO
        GVL_S5Counters_Lang.aCounter[iS5] := stCounterZero;
    END_FOR

    // #1, t = 0 мс — пуск: сирена и задержка, остаток 200 единиц
    GVL_S7Clock.tSimNow := T#0MS;
    fbStartSequence.xStart := TRUE;
    fbStartSequence.xStop := FALSE;
    fbStartSequence.xSensor := FALSE;
    fbStartSequence.xAck := FALSE;
    fbStartSequence.xCountReset := FALSE;
    fbStartSequence();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbStartSequence.xHorn, Message := 'StartSequence#1 xHorn');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStartSequence.xMotor, Message := 'StartSequence#1 xMotor');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStartSequence.xFlowOk, Message := 'StartSequence#1 xFlowOk');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStartSequence.xJam, Message := 'StartSequence#1 xJam');
    AssertEquals_INT(Expected := 200, Actual := fbStartSequence.iDelayLeft, Message := 'StartSequence#1 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbStartSequence.wRunOutBcd,
                      Message := 'StartSequence#1 wRunOutBcd');
    AssertEquals_INT(Expected := 0, Actual := fbStartSequence.iCount, Message := 'StartSequence#1 iCount');
    AssertEquals_WORD(Expected := 16#0000, Actual := fbStartSequence.wCountBcd, Message := 'StartSequence#1 wCountBcd');

    // #2, t = 300 мс — кнопка отпущена: сирена звучит, остаток 170
    GVL_S7Clock.tSimNow := T#300MS;
    fbStartSequence.xStart := FALSE;
    fbStartSequence();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbStartSequence.xHorn, Message := 'StartSequence#2 xHorn');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStartSequence.xMotor, Message := 'StartSequence#2 xMotor');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStartSequence.xFlowOk, Message := 'StartSequence#2 xFlowOk');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStartSequence.xJam, Message := 'StartSequence#2 xJam');
    AssertEquals_INT(Expected := 170, Actual := fbStartSequence.iDelayLeft, Message := 'StartSequence#2 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbStartSequence.wRunOutBcd,
                      Message := 'StartSequence#2 wRunOutBcd');
    AssertEquals_INT(Expected := 0, Actual := fbStartSequence.iCount, Message := 'StartSequence#2 iCount');
    AssertEquals_WORD(Expected := 16#0000, Actual := fbStartSequence.wCountBcd, Message := 'StartSequence#2 wCountBcd');

    // #3, t = 1000 мс, на пороге таймера — 1 с: сирена выключилась (T1 истёк), остаток 100
    GVL_S7Clock.tSimNow := T#1000MS;
    fbStartSequence();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStartSequence.xHorn, Message := 'StartSequence#3 xHorn');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStartSequence.xMotor, Message := 'StartSequence#3 xMotor');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStartSequence.xFlowOk, Message := 'StartSequence#3 xFlowOk');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStartSequence.xJam, Message := 'StartSequence#3 xJam');
    AssertEquals_INT(Expected := 100, Actual := fbStartSequence.iDelayLeft, Message := 'StartSequence#3 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbStartSequence.wRunOutBcd,
                      Message := 'StartSequence#3 wRunOutBcd');
    AssertEquals_INT(Expected := 0, Actual := fbStartSequence.iCount, Message := 'StartSequence#3 iCount');
    AssertEquals_WORD(Expected := 16#0000, Actual := fbStartSequence.wCountBcd, Message := 'StartSequence#3 wCountBcd');

    // #4, t = 1500 мс — остаток 50
    GVL_S7Clock.tSimNow := T#1500MS;
    fbStartSequence();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStartSequence.xHorn, Message := 'StartSequence#4 xHorn');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStartSequence.xMotor, Message := 'StartSequence#4 xMotor');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStartSequence.xFlowOk, Message := 'StartSequence#4 xFlowOk');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStartSequence.xJam, Message := 'StartSequence#4 xJam');
    AssertEquals_INT(Expected := 50, Actual := fbStartSequence.iDelayLeft, Message := 'StartSequence#4 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbStartSequence.wRunOutBcd,
                      Message := 'StartSequence#4 wRunOutBcd');
    AssertEquals_INT(Expected := 0, Actual := fbStartSequence.iCount, Message := 'StartSequence#4 iCount');
    AssertEquals_WORD(Expected := 16#0000, Actual := fbStartSequence.wCountBcd, Message := 'StartSequence#4 wCountBcd');

    // #5, t = 2000 мс, на пороге таймера — 2 с: задержка истекла — двигатель
    GVL_S7Clock.tSimNow := T#2000MS;
    fbStartSequence();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStartSequence.xHorn, Message := 'StartSequence#5 xHorn');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbStartSequence.xMotor, Message := 'StartSequence#5 xMotor');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStartSequence.xFlowOk, Message := 'StartSequence#5 xFlowOk');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStartSequence.xJam, Message := 'StartSequence#5 xJam');
    AssertEquals_INT(Expected := 0, Actual := fbStartSequence.iDelayLeft, Message := 'StartSequence#5 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbStartSequence.wRunOutBcd,
                      Message := 'StartSequence#5 wRunOutBcd');
    AssertEquals_INT(Expected := 0, Actual := fbStartSequence.iCount, Message := 'StartSequence#5 iCount');
    AssertEquals_WORD(Expected := 16#0000, Actual := fbStartSequence.wCountBcd, Message := 'StartSequence#5 wCountBcd');

    // #6, t = 2500 мс — работает
    GVL_S7Clock.tSimNow := T#2500MS;
    fbStartSequence();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStartSequence.xHorn, Message := 'StartSequence#6 xHorn');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbStartSequence.xMotor, Message := 'StartSequence#6 xMotor');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStartSequence.xFlowOk, Message := 'StartSequence#6 xFlowOk');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbStartSequence.xJam, Message := 'StartSequence#6 xJam');
    AssertEquals_INT(Expected := 0, Actual := fbStartSequence.iDelayLeft, Message := 'StartSequence#6 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbStartSequence.wRunOutBcd,
                      Message := 'StartSequence#6 wRunOutBcd');
    AssertEquals_INT(Expected := 0, Actual := fbStartSequence.iCount, Message := 'StartSequence#6 iCount');
    AssertEquals_WORD(Expected := 16#0000, Actual := fbStartSequence.wCountBcd, Message := 'StartSequence#6 wCountBcd');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
