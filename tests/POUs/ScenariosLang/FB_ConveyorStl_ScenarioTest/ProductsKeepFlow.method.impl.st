// AUTO-GENERATED — не редактировать: scenarios/lang/FB_ConveyorStl.csv, сценарий ProductsKeepFlow
coUnit.TEST('ProductsKeepFlow');
IF NOT xProductsKeepFlowDone THEN
    xProductsKeepFlowDone := TRUE;
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
    fbProductsKeepFlow.xStart := TRUE;
    fbProductsKeepFlow.xStop := FALSE;
    fbProductsKeepFlow.xSensor := FALSE;
    fbProductsKeepFlow.xAck := FALSE;
    fbProductsKeepFlow.xCountReset := FALSE;
    fbProductsKeepFlow();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbProductsKeepFlow.xHorn, Message := 'ProductsKeepFlow#1 xHorn');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbProductsKeepFlow.xMotor, Message := 'ProductsKeepFlow#1 xMotor');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbProductsKeepFlow.xFlowOk, Message := 'ProductsKeepFlow#1 xFlowOk');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbProductsKeepFlow.xJam, Message := 'ProductsKeepFlow#1 xJam');
    AssertEquals_INT(Expected := 200,
                     Actual := fbProductsKeepFlow.iDelayLeft,
                     Message := 'ProductsKeepFlow#1 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbProductsKeepFlow.wRunOutBcd,
                      Message := 'ProductsKeepFlow#1 wRunOutBcd');
    AssertEquals_INT(Expected := 0, Actual := fbProductsKeepFlow.iCount, Message := 'ProductsKeepFlow#1 iCount');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbProductsKeepFlow.wCountBcd,
                      Message := 'ProductsKeepFlow#1 wCountBcd');

    // #2, t = 100 мс — кнопка отпущена
    GVL_S7Clock.tSimNow := T#100MS;
    fbProductsKeepFlow.xStart := FALSE;
    fbProductsKeepFlow();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbProductsKeepFlow.xHorn, Message := 'ProductsKeepFlow#2 xHorn');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbProductsKeepFlow.xMotor, Message := 'ProductsKeepFlow#2 xMotor');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbProductsKeepFlow.xFlowOk, Message := 'ProductsKeepFlow#2 xFlowOk');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbProductsKeepFlow.xJam, Message := 'ProductsKeepFlow#2 xJam');
    AssertEquals_INT(Expected := 190,
                     Actual := fbProductsKeepFlow.iDelayLeft,
                     Message := 'ProductsKeepFlow#2 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbProductsKeepFlow.wRunOutBcd,
                      Message := 'ProductsKeepFlow#2 wRunOutBcd');
    AssertEquals_INT(Expected := 0, Actual := fbProductsKeepFlow.iCount, Message := 'ProductsKeepFlow#2 iCount');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbProductsKeepFlow.wCountBcd,
                      Message := 'ProductsKeepFlow#2 wCountBcd');

    // #3, t = 2000 мс, на пороге таймера — 2 с: задержка T2 истекла — двигатель (T3 = 1)
    GVL_S7Clock.tSimNow := T#2000MS;
    fbProductsKeepFlow();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbProductsKeepFlow.xHorn, Message := 'ProductsKeepFlow#3 xHorn');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbProductsKeepFlow.xMotor, Message := 'ProductsKeepFlow#3 xMotor');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbProductsKeepFlow.xFlowOk, Message := 'ProductsKeepFlow#3 xFlowOk');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbProductsKeepFlow.xJam, Message := 'ProductsKeepFlow#3 xJam');
    AssertEquals_INT(Expected := 0,
                     Actual := fbProductsKeepFlow.iDelayLeft,
                     Message := 'ProductsKeepFlow#3 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbProductsKeepFlow.wRunOutBcd,
                      Message := 'ProductsKeepFlow#3 wRunOutBcd');
    AssertEquals_INT(Expected := 0, Actual := fbProductsKeepFlow.iCount, Message := 'ProductsKeepFlow#3 iCount');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbProductsKeepFlow.wCountBcd,
                      Message := 'ProductsKeepFlow#3 wCountBcd');

    // #4, t = 2500 мс — изделие №1: T4 пошёл
    GVL_S7Clock.tSimNow := T#2500MS;
    fbProductsKeepFlow.xSensor := TRUE;
    fbProductsKeepFlow();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbProductsKeepFlow.xHorn, Message := 'ProductsKeepFlow#4 xHorn');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbProductsKeepFlow.xMotor, Message := 'ProductsKeepFlow#4 xMotor');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbProductsKeepFlow.xFlowOk, Message := 'ProductsKeepFlow#4 xFlowOk');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbProductsKeepFlow.xJam, Message := 'ProductsKeepFlow#4 xJam');
    AssertEquals_INT(Expected := 0,
                     Actual := fbProductsKeepFlow.iDelayLeft,
                     Message := 'ProductsKeepFlow#4 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbProductsKeepFlow.wRunOutBcd,
                      Message := 'ProductsKeepFlow#4 wRunOutBcd');
    AssertEquals_INT(Expected := 1, Actual := fbProductsKeepFlow.iCount, Message := 'ProductsKeepFlow#4 iCount');
    AssertEquals_WORD(Expected := 16#0001,
                      Actual := fbProductsKeepFlow.wCountBcd,
                      Message := 'ProductsKeepFlow#4 wCountBcd');

    // #5, t = 2600 мс — датчик свободен
    GVL_S7Clock.tSimNow := T#2600MS;
    fbProductsKeepFlow.xSensor := FALSE;
    fbProductsKeepFlow();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbProductsKeepFlow.xHorn, Message := 'ProductsKeepFlow#5 xHorn');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbProductsKeepFlow.xMotor, Message := 'ProductsKeepFlow#5 xMotor');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbProductsKeepFlow.xFlowOk, Message := 'ProductsKeepFlow#5 xFlowOk');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbProductsKeepFlow.xJam, Message := 'ProductsKeepFlow#5 xJam');
    AssertEquals_INT(Expected := 0,
                     Actual := fbProductsKeepFlow.iDelayLeft,
                     Message := 'ProductsKeepFlow#5 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbProductsKeepFlow.wRunOutBcd,
                      Message := 'ProductsKeepFlow#5 wRunOutBcd');
    AssertEquals_INT(Expected := 1, Actual := fbProductsKeepFlow.iCount, Message := 'ProductsKeepFlow#5 iCount');
    AssertEquals_WORD(Expected := 16#0001,
                      Actual := fbProductsKeepFlow.wCountBcd,
                      Message := 'ProductsKeepFlow#5 wCountBcd');

    // #6, t = 4500 мс — изделие №2: T4 перезапущен
    GVL_S7Clock.tSimNow := T#4500MS;
    fbProductsKeepFlow.xSensor := TRUE;
    fbProductsKeepFlow();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbProductsKeepFlow.xHorn, Message := 'ProductsKeepFlow#6 xHorn');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbProductsKeepFlow.xMotor, Message := 'ProductsKeepFlow#6 xMotor');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbProductsKeepFlow.xFlowOk, Message := 'ProductsKeepFlow#6 xFlowOk');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbProductsKeepFlow.xJam, Message := 'ProductsKeepFlow#6 xJam');
    AssertEquals_INT(Expected := 0,
                     Actual := fbProductsKeepFlow.iDelayLeft,
                     Message := 'ProductsKeepFlow#6 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbProductsKeepFlow.wRunOutBcd,
                      Message := 'ProductsKeepFlow#6 wRunOutBcd');
    AssertEquals_INT(Expected := 2, Actual := fbProductsKeepFlow.iCount, Message := 'ProductsKeepFlow#6 iCount');
    AssertEquals_WORD(Expected := 16#0002,
                      Actual := fbProductsKeepFlow.wCountBcd,
                      Message := 'ProductsKeepFlow#6 wCountBcd');

    // #7, t = 4600 мс — датчик свободен
    GVL_S7Clock.tSimNow := T#4600MS;
    fbProductsKeepFlow.xSensor := FALSE;
    fbProductsKeepFlow();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbProductsKeepFlow.xHorn, Message := 'ProductsKeepFlow#7 xHorn');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbProductsKeepFlow.xMotor, Message := 'ProductsKeepFlow#7 xMotor');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbProductsKeepFlow.xFlowOk, Message := 'ProductsKeepFlow#7 xFlowOk');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbProductsKeepFlow.xJam, Message := 'ProductsKeepFlow#7 xJam');
    AssertEquals_INT(Expected := 0,
                     Actual := fbProductsKeepFlow.iDelayLeft,
                     Message := 'ProductsKeepFlow#7 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbProductsKeepFlow.wRunOutBcd,
                      Message := 'ProductsKeepFlow#7 wRunOutBcd');
    AssertEquals_INT(Expected := 2, Actual := fbProductsKeepFlow.iCount, Message := 'ProductsKeepFlow#7 iCount');
    AssertEquals_WORD(Expected := 16#0002,
                      Actual := fbProductsKeepFlow.wCountBcd,
                      Message := 'ProductsKeepFlow#7 wCountBcd');

    // #8, t = 6500 мс — изделие №3
    GVL_S7Clock.tSimNow := T#6500MS;
    fbProductsKeepFlow.xSensor := TRUE;
    fbProductsKeepFlow();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbProductsKeepFlow.xHorn, Message := 'ProductsKeepFlow#8 xHorn');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbProductsKeepFlow.xMotor, Message := 'ProductsKeepFlow#8 xMotor');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbProductsKeepFlow.xFlowOk, Message := 'ProductsKeepFlow#8 xFlowOk');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbProductsKeepFlow.xJam, Message := 'ProductsKeepFlow#8 xJam');
    AssertEquals_INT(Expected := 0,
                     Actual := fbProductsKeepFlow.iDelayLeft,
                     Message := 'ProductsKeepFlow#8 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbProductsKeepFlow.wRunOutBcd,
                      Message := 'ProductsKeepFlow#8 wRunOutBcd');
    AssertEquals_INT(Expected := 3, Actual := fbProductsKeepFlow.iCount, Message := 'ProductsKeepFlow#8 iCount');
    AssertEquals_WORD(Expected := 16#0003,
                      Actual := fbProductsKeepFlow.wCountBcd,
                      Message := 'ProductsKeepFlow#8 wCountBcd');

    // #9, t = 6600 мс — датчик свободен
    GVL_S7Clock.tSimNow := T#6600MS;
    fbProductsKeepFlow.xSensor := FALSE;
    fbProductsKeepFlow();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbProductsKeepFlow.xHorn, Message := 'ProductsKeepFlow#9 xHorn');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbProductsKeepFlow.xMotor, Message := 'ProductsKeepFlow#9 xMotor');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbProductsKeepFlow.xFlowOk, Message := 'ProductsKeepFlow#9 xFlowOk');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbProductsKeepFlow.xJam, Message := 'ProductsKeepFlow#9 xJam');
    AssertEquals_INT(Expected := 0,
                     Actual := fbProductsKeepFlow.iDelayLeft,
                     Message := 'ProductsKeepFlow#9 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbProductsKeepFlow.wRunOutBcd,
                      Message := 'ProductsKeepFlow#9 wRunOutBcd');
    AssertEquals_INT(Expected := 3, Actual := fbProductsKeepFlow.iCount, Message := 'ProductsKeepFlow#9 iCount');
    AssertEquals_WORD(Expected := 16#0003,
                      Actual := fbProductsKeepFlow.wCountBcd,
                      Message := 'ProductsKeepFlow#9 wCountBcd');

    // #10, t = 7000 мс, на пороге таймера — 5 с работы: контроль взведён, T4 идёт — затора нет
    GVL_S7Clock.tSimNow := T#7000MS;
    fbProductsKeepFlow();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbProductsKeepFlow.xHorn, Message := 'ProductsKeepFlow#10 xHorn');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbProductsKeepFlow.xMotor, Message := 'ProductsKeepFlow#10 xMotor');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbProductsKeepFlow.xFlowOk, Message := 'ProductsKeepFlow#10 xFlowOk');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbProductsKeepFlow.xJam, Message := 'ProductsKeepFlow#10 xJam');
    AssertEquals_INT(Expected := 0,
                     Actual := fbProductsKeepFlow.iDelayLeft,
                     Message := 'ProductsKeepFlow#10 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbProductsKeepFlow.wRunOutBcd,
                      Message := 'ProductsKeepFlow#10 wRunOutBcd');
    AssertEquals_INT(Expected := 3, Actual := fbProductsKeepFlow.iCount, Message := 'ProductsKeepFlow#10 iCount');
    AssertEquals_WORD(Expected := 16#0003,
                      Actual := fbProductsKeepFlow.wCountBcd,
                      Message := 'ProductsKeepFlow#10 wCountBcd');

    // #11, t = 8500 мс — изделие №4
    GVL_S7Clock.tSimNow := T#8500MS;
    fbProductsKeepFlow.xSensor := TRUE;
    fbProductsKeepFlow();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbProductsKeepFlow.xHorn, Message := 'ProductsKeepFlow#11 xHorn');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbProductsKeepFlow.xMotor, Message := 'ProductsKeepFlow#11 xMotor');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbProductsKeepFlow.xFlowOk, Message := 'ProductsKeepFlow#11 xFlowOk');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbProductsKeepFlow.xJam, Message := 'ProductsKeepFlow#11 xJam');
    AssertEquals_INT(Expected := 0,
                     Actual := fbProductsKeepFlow.iDelayLeft,
                     Message := 'ProductsKeepFlow#11 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbProductsKeepFlow.wRunOutBcd,
                      Message := 'ProductsKeepFlow#11 wRunOutBcd');
    AssertEquals_INT(Expected := 4, Actual := fbProductsKeepFlow.iCount, Message := 'ProductsKeepFlow#11 iCount');
    AssertEquals_WORD(Expected := 16#0004,
                      Actual := fbProductsKeepFlow.wCountBcd,
                      Message := 'ProductsKeepFlow#11 wCountBcd');

    // #12, t = 8600 мс — датчик свободен
    GVL_S7Clock.tSimNow := T#8600MS;
    fbProductsKeepFlow.xSensor := FALSE;
    fbProductsKeepFlow();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbProductsKeepFlow.xHorn, Message := 'ProductsKeepFlow#12 xHorn');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbProductsKeepFlow.xMotor, Message := 'ProductsKeepFlow#12 xMotor');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbProductsKeepFlow.xFlowOk, Message := 'ProductsKeepFlow#12 xFlowOk');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbProductsKeepFlow.xJam, Message := 'ProductsKeepFlow#12 xJam');
    AssertEquals_INT(Expected := 0,
                     Actual := fbProductsKeepFlow.iDelayLeft,
                     Message := 'ProductsKeepFlow#12 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbProductsKeepFlow.wRunOutBcd,
                      Message := 'ProductsKeepFlow#12 wRunOutBcd');
    AssertEquals_INT(Expected := 4, Actual := fbProductsKeepFlow.iCount, Message := 'ProductsKeepFlow#12 iCount');
    AssertEquals_WORD(Expected := 16#0004,
                      Actual := fbProductsKeepFlow.wCountBcd,
                      Message := 'ProductsKeepFlow#12 wCountBcd');

    // #13, t = 10600 мс — 2,1 с без изделий
    GVL_S7Clock.tSimNow := T#10600MS;
    fbProductsKeepFlow();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbProductsKeepFlow.xHorn, Message := 'ProductsKeepFlow#13 xHorn');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbProductsKeepFlow.xMotor, Message := 'ProductsKeepFlow#13 xMotor');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbProductsKeepFlow.xFlowOk, Message := 'ProductsKeepFlow#13 xFlowOk');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbProductsKeepFlow.xJam, Message := 'ProductsKeepFlow#13 xJam');
    AssertEquals_INT(Expected := 0,
                     Actual := fbProductsKeepFlow.iDelayLeft,
                     Message := 'ProductsKeepFlow#13 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbProductsKeepFlow.wRunOutBcd,
                      Message := 'ProductsKeepFlow#13 wRunOutBcd');
    AssertEquals_INT(Expected := 4, Actual := fbProductsKeepFlow.iCount, Message := 'ProductsKeepFlow#13 iCount');
    AssertEquals_WORD(Expected := 16#0004,
                      Actual := fbProductsKeepFlow.wCountBcd,
                      Message := 'ProductsKeepFlow#13 wCountBcd');

    // #14, t = 12500 мс, на пороге таймера — 4 с без изделий: T4 истёк — затор
    GVL_S7Clock.tSimNow := T#12500MS;
    fbProductsKeepFlow();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbProductsKeepFlow.xHorn, Message := 'ProductsKeepFlow#14 xHorn');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbProductsKeepFlow.xMotor, Message := 'ProductsKeepFlow#14 xMotor');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbProductsKeepFlow.xFlowOk,
                      Message := 'ProductsKeepFlow#14 xFlowOk');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbProductsKeepFlow.xJam, Message := 'ProductsKeepFlow#14 xJam');
    AssertEquals_INT(Expected := 0,
                     Actual := fbProductsKeepFlow.iDelayLeft,
                     Message := 'ProductsKeepFlow#14 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbProductsKeepFlow.wRunOutBcd,
                      Message := 'ProductsKeepFlow#14 wRunOutBcd');
    AssertEquals_INT(Expected := 4, Actual := fbProductsKeepFlow.iCount, Message := 'ProductsKeepFlow#14 iCount');
    AssertEquals_WORD(Expected := 16#0004,
                      Actual := fbProductsKeepFlow.wCountBcd,
                      Message := 'ProductsKeepFlow#14 wCountBcd');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
