// AUTO-GENERATED — не редактировать: scenarios/lang/FB_ConveyorStl.csv, сценарий CountResetIsLevel
coUnit.TEST('CountResetIsLevel');
IF NOT xCountResetIsLevelDone THEN
    xCountResetIsLevelDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;
    // слова S5 — глобальные (GVL_S5Timers_Lang): сценарий начинается с чистых таймеров и счётчиков
    FOR iS5 := 0 TO 5 DO
        GVL_S5Timers_Lang.aTimer[iS5] := stTimerZero;
    END_FOR
    // слова S5 — глобальные (GVL_S5Counters_Lang): сценарий начинается с чистых таймеров и счётчиков
    FOR iS5 := 0 TO 1 DO
        GVL_S5Counters_Lang.aCounter[iS5] := stCounterZero;
    END_FOR

    // #1, t = 0 мс — изделие №1
    GVL_S7Clock.tSimNow := T#0MS;
    fbCountResetIsLevel.xStart := FALSE;
    fbCountResetIsLevel.xStop := FALSE;
    fbCountResetIsLevel.xSensor := TRUE;
    fbCountResetIsLevel.xAck := FALSE;
    fbCountResetIsLevel.xCountReset := FALSE;
    fbCountResetIsLevel();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCountResetIsLevel.xHorn, Message := 'CountResetIsLevel#1 xHorn');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCountResetIsLevel.xMotor, Message := 'CountResetIsLevel#1 xMotor');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbCountResetIsLevel.xFlowOk,
                      Message := 'CountResetIsLevel#1 xFlowOk');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCountResetIsLevel.xJam, Message := 'CountResetIsLevel#1 xJam');
    AssertEquals_INT(Expected := 0,
                     Actual := fbCountResetIsLevel.iDelayLeft,
                     Message := 'CountResetIsLevel#1 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbCountResetIsLevel.wRunOutBcd,
                      Message := 'CountResetIsLevel#1 wRunOutBcd');
    AssertEquals_INT(Expected := 1, Actual := fbCountResetIsLevel.iCount, Message := 'CountResetIsLevel#1 iCount');
    AssertEquals_WORD(Expected := 16#0001,
                      Actual := fbCountResetIsLevel.wCountBcd,
                      Message := 'CountResetIsLevel#1 wCountBcd');

    // #2, t = 100 мс — датчик свободен
    GVL_S7Clock.tSimNow := T#100MS;
    fbCountResetIsLevel.xSensor := FALSE;
    fbCountResetIsLevel();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCountResetIsLevel.xHorn, Message := 'CountResetIsLevel#2 xHorn');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCountResetIsLevel.xMotor, Message := 'CountResetIsLevel#2 xMotor');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbCountResetIsLevel.xFlowOk,
                      Message := 'CountResetIsLevel#2 xFlowOk');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCountResetIsLevel.xJam, Message := 'CountResetIsLevel#2 xJam');
    AssertEquals_INT(Expected := 0,
                     Actual := fbCountResetIsLevel.iDelayLeft,
                     Message := 'CountResetIsLevel#2 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbCountResetIsLevel.wRunOutBcd,
                      Message := 'CountResetIsLevel#2 wRunOutBcd');
    AssertEquals_INT(Expected := 1, Actual := fbCountResetIsLevel.iCount, Message := 'CountResetIsLevel#2 iCount');
    AssertEquals_WORD(Expected := 16#0001,
                      Actual := fbCountResetIsLevel.wCountBcd,
                      Message := 'CountResetIsLevel#2 wCountBcd');

    // #3, t = 200 мс — изделие №2
    GVL_S7Clock.tSimNow := T#200MS;
    fbCountResetIsLevel.xSensor := TRUE;
    fbCountResetIsLevel();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCountResetIsLevel.xHorn, Message := 'CountResetIsLevel#3 xHorn');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCountResetIsLevel.xMotor, Message := 'CountResetIsLevel#3 xMotor');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbCountResetIsLevel.xFlowOk,
                      Message := 'CountResetIsLevel#3 xFlowOk');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCountResetIsLevel.xJam, Message := 'CountResetIsLevel#3 xJam');
    AssertEquals_INT(Expected := 0,
                     Actual := fbCountResetIsLevel.iDelayLeft,
                     Message := 'CountResetIsLevel#3 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbCountResetIsLevel.wRunOutBcd,
                      Message := 'CountResetIsLevel#3 wRunOutBcd');
    AssertEquals_INT(Expected := 2, Actual := fbCountResetIsLevel.iCount, Message := 'CountResetIsLevel#3 iCount');
    AssertEquals_WORD(Expected := 16#0002,
                      Actual := fbCountResetIsLevel.wCountBcd,
                      Message := 'CountResetIsLevel#3 wCountBcd');

    // #4, t = 300 мс — датчик свободен
    GVL_S7Clock.tSimNow := T#300MS;
    fbCountResetIsLevel.xSensor := FALSE;
    fbCountResetIsLevel();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCountResetIsLevel.xHorn, Message := 'CountResetIsLevel#4 xHorn');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCountResetIsLevel.xMotor, Message := 'CountResetIsLevel#4 xMotor');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbCountResetIsLevel.xFlowOk,
                      Message := 'CountResetIsLevel#4 xFlowOk');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCountResetIsLevel.xJam, Message := 'CountResetIsLevel#4 xJam');
    AssertEquals_INT(Expected := 0,
                     Actual := fbCountResetIsLevel.iDelayLeft,
                     Message := 'CountResetIsLevel#4 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbCountResetIsLevel.wRunOutBcd,
                      Message := 'CountResetIsLevel#4 wRunOutBcd');
    AssertEquals_INT(Expected := 2, Actual := fbCountResetIsLevel.iCount, Message := 'CountResetIsLevel#4 iCount');
    AssertEquals_WORD(Expected := 16#0002,
                      Actual := fbCountResetIsLevel.wCountBcd,
                      Message := 'CountResetIsLevel#4 wCountBcd');

    // #5, t = 400 мс — сброс счётчика
    GVL_S7Clock.tSimNow := T#400MS;
    fbCountResetIsLevel.xCountReset := TRUE;
    fbCountResetIsLevel();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCountResetIsLevel.xHorn, Message := 'CountResetIsLevel#5 xHorn');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCountResetIsLevel.xMotor, Message := 'CountResetIsLevel#5 xMotor');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbCountResetIsLevel.xFlowOk,
                      Message := 'CountResetIsLevel#5 xFlowOk');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCountResetIsLevel.xJam, Message := 'CountResetIsLevel#5 xJam');
    AssertEquals_INT(Expected := 0,
                     Actual := fbCountResetIsLevel.iDelayLeft,
                     Message := 'CountResetIsLevel#5 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbCountResetIsLevel.wRunOutBcd,
                      Message := 'CountResetIsLevel#5 wRunOutBcd');
    AssertEquals_INT(Expected := 0, Actual := fbCountResetIsLevel.iCount, Message := 'CountResetIsLevel#5 iCount');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbCountResetIsLevel.wCountBcd,
                      Message := 'CountResetIsLevel#5 wCountBcd');

    // #6, t = 500 мс — изделие при нажатом сбросе: CU считает, R тут же обнуляет
    GVL_S7Clock.tSimNow := T#500MS;
    fbCountResetIsLevel.xSensor := TRUE;
    fbCountResetIsLevel();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCountResetIsLevel.xHorn, Message := 'CountResetIsLevel#6 xHorn');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCountResetIsLevel.xMotor, Message := 'CountResetIsLevel#6 xMotor');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbCountResetIsLevel.xFlowOk,
                      Message := 'CountResetIsLevel#6 xFlowOk');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCountResetIsLevel.xJam, Message := 'CountResetIsLevel#6 xJam');
    AssertEquals_INT(Expected := 0,
                     Actual := fbCountResetIsLevel.iDelayLeft,
                     Message := 'CountResetIsLevel#6 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbCountResetIsLevel.wRunOutBcd,
                      Message := 'CountResetIsLevel#6 wRunOutBcd');
    AssertEquals_INT(Expected := 0, Actual := fbCountResetIsLevel.iCount, Message := 'CountResetIsLevel#6 iCount');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbCountResetIsLevel.wCountBcd,
                      Message := 'CountResetIsLevel#6 wCountBcd');

    // #7, t = 600 мс — сброс отпущен
    GVL_S7Clock.tSimNow := T#600MS;
    fbCountResetIsLevel.xSensor := FALSE;
    fbCountResetIsLevel.xCountReset := FALSE;
    fbCountResetIsLevel();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCountResetIsLevel.xHorn, Message := 'CountResetIsLevel#7 xHorn');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCountResetIsLevel.xMotor, Message := 'CountResetIsLevel#7 xMotor');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbCountResetIsLevel.xFlowOk,
                      Message := 'CountResetIsLevel#7 xFlowOk');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCountResetIsLevel.xJam, Message := 'CountResetIsLevel#7 xJam');
    AssertEquals_INT(Expected := 0,
                     Actual := fbCountResetIsLevel.iDelayLeft,
                     Message := 'CountResetIsLevel#7 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbCountResetIsLevel.wRunOutBcd,
                      Message := 'CountResetIsLevel#7 wRunOutBcd');
    AssertEquals_INT(Expected := 0, Actual := fbCountResetIsLevel.iCount, Message := 'CountResetIsLevel#7 iCount');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbCountResetIsLevel.wCountBcd,
                      Message := 'CountResetIsLevel#7 wCountBcd');

    // #8, t = 700 мс — изделие №1 после сброса
    GVL_S7Clock.tSimNow := T#700MS;
    fbCountResetIsLevel.xSensor := TRUE;
    fbCountResetIsLevel();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCountResetIsLevel.xHorn, Message := 'CountResetIsLevel#8 xHorn');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCountResetIsLevel.xMotor, Message := 'CountResetIsLevel#8 xMotor');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbCountResetIsLevel.xFlowOk,
                      Message := 'CountResetIsLevel#8 xFlowOk');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCountResetIsLevel.xJam, Message := 'CountResetIsLevel#8 xJam');
    AssertEquals_INT(Expected := 0,
                     Actual := fbCountResetIsLevel.iDelayLeft,
                     Message := 'CountResetIsLevel#8 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbCountResetIsLevel.wRunOutBcd,
                      Message := 'CountResetIsLevel#8 wRunOutBcd');
    AssertEquals_INT(Expected := 1, Actual := fbCountResetIsLevel.iCount, Message := 'CountResetIsLevel#8 iCount');
    AssertEquals_WORD(Expected := 16#0001,
                      Actual := fbCountResetIsLevel.wCountBcd,
                      Message := 'CountResetIsLevel#8 wCountBcd');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
