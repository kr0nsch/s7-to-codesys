// AUTO-GENERATED — не редактировать: scenarios/lang/FB_ConveyorStl.csv, сценарий JamWithoutProducts
coUnit.TEST('JamWithoutProducts');
IF NOT xJamWithoutProductsDone THEN
    xJamWithoutProductsDone := TRUE;
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
    fbJamWithoutProducts.xStart := TRUE;
    fbJamWithoutProducts.xStop := FALSE;
    fbJamWithoutProducts.xSensor := FALSE;
    fbJamWithoutProducts.xAck := FALSE;
    fbJamWithoutProducts.xCountReset := FALSE;
    fbJamWithoutProducts();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbJamWithoutProducts.xHorn, Message := 'JamWithoutProducts#1 xHorn');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbJamWithoutProducts.xMotor,
                      Message := 'JamWithoutProducts#1 xMotor');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbJamWithoutProducts.xFlowOk,
                      Message := 'JamWithoutProducts#1 xFlowOk');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbJamWithoutProducts.xJam, Message := 'JamWithoutProducts#1 xJam');
    AssertEquals_INT(Expected := 200,
                     Actual := fbJamWithoutProducts.iDelayLeft,
                     Message := 'JamWithoutProducts#1 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbJamWithoutProducts.wRunOutBcd,
                      Message := 'JamWithoutProducts#1 wRunOutBcd');
    AssertEquals_INT(Expected := 0, Actual := fbJamWithoutProducts.iCount, Message := 'JamWithoutProducts#1 iCount');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbJamWithoutProducts.wCountBcd,
                      Message := 'JamWithoutProducts#1 wCountBcd');

    // #2, t = 100 мс — кнопка отпущена
    GVL_S7Clock.tSimNow := T#100MS;
    fbJamWithoutProducts.xStart := FALSE;
    fbJamWithoutProducts();
    AssertEquals_BOOL(Expected := TRUE, Actual := fbJamWithoutProducts.xHorn, Message := 'JamWithoutProducts#2 xHorn');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbJamWithoutProducts.xMotor,
                      Message := 'JamWithoutProducts#2 xMotor');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbJamWithoutProducts.xFlowOk,
                      Message := 'JamWithoutProducts#2 xFlowOk');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbJamWithoutProducts.xJam, Message := 'JamWithoutProducts#2 xJam');
    AssertEquals_INT(Expected := 190,
                     Actual := fbJamWithoutProducts.iDelayLeft,
                     Message := 'JamWithoutProducts#2 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbJamWithoutProducts.wRunOutBcd,
                      Message := 'JamWithoutProducts#2 wRunOutBcd');
    AssertEquals_INT(Expected := 0, Actual := fbJamWithoutProducts.iCount, Message := 'JamWithoutProducts#2 iCount');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbJamWithoutProducts.wCountBcd,
                      Message := 'JamWithoutProducts#2 wCountBcd');

    // #3, t = 2000 мс, на пороге таймера — 2 с: задержка T2 истекла — двигатель (T3 = 1)
    GVL_S7Clock.tSimNow := T#2000MS;
    fbJamWithoutProducts();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbJamWithoutProducts.xHorn, Message := 'JamWithoutProducts#3 xHorn');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbJamWithoutProducts.xMotor,
                      Message := 'JamWithoutProducts#3 xMotor');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbJamWithoutProducts.xFlowOk,
                      Message := 'JamWithoutProducts#3 xFlowOk');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbJamWithoutProducts.xJam, Message := 'JamWithoutProducts#3 xJam');
    AssertEquals_INT(Expected := 0,
                     Actual := fbJamWithoutProducts.iDelayLeft,
                     Message := 'JamWithoutProducts#3 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbJamWithoutProducts.wRunOutBcd,
                      Message := 'JamWithoutProducts#3 wRunOutBcd');
    AssertEquals_INT(Expected := 0, Actual := fbJamWithoutProducts.iCount, Message := 'JamWithoutProducts#3 iCount');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbJamWithoutProducts.wCountBcd,
                      Message := 'JamWithoutProducts#3 wCountBcd');

    // #4, t = 6700 мс — 4,7 с работы: контроль ещё не взведён
    GVL_S7Clock.tSimNow := T#6700MS;
    fbJamWithoutProducts();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbJamWithoutProducts.xHorn, Message := 'JamWithoutProducts#4 xHorn');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbJamWithoutProducts.xMotor,
                      Message := 'JamWithoutProducts#4 xMotor');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbJamWithoutProducts.xFlowOk,
                      Message := 'JamWithoutProducts#4 xFlowOk');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbJamWithoutProducts.xJam, Message := 'JamWithoutProducts#4 xJam');
    AssertEquals_INT(Expected := 0,
                     Actual := fbJamWithoutProducts.iDelayLeft,
                     Message := 'JamWithoutProducts#4 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbJamWithoutProducts.wRunOutBcd,
                      Message := 'JamWithoutProducts#4 wRunOutBcd');
    AssertEquals_INT(Expected := 0, Actual := fbJamWithoutProducts.iCount, Message := 'JamWithoutProducts#4 iCount');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbJamWithoutProducts.wCountBcd,
                      Message := 'JamWithoutProducts#4 wCountBcd');

    // #5, t = 7000 мс, на пороге таймера — 5 с работы: T5 взвёл контроль, T4 не идёт — затор
    GVL_S7Clock.tSimNow := T#7000MS;
    fbJamWithoutProducts();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbJamWithoutProducts.xHorn, Message := 'JamWithoutProducts#5 xHorn');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbJamWithoutProducts.xMotor,
                      Message := 'JamWithoutProducts#5 xMotor');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbJamWithoutProducts.xFlowOk,
                      Message := 'JamWithoutProducts#5 xFlowOk');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbJamWithoutProducts.xJam, Message := 'JamWithoutProducts#5 xJam');
    AssertEquals_INT(Expected := 0,
                     Actual := fbJamWithoutProducts.iDelayLeft,
                     Message := 'JamWithoutProducts#5 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbJamWithoutProducts.wRunOutBcd,
                      Message := 'JamWithoutProducts#5 wRunOutBcd');
    AssertEquals_INT(Expected := 0, Actual := fbJamWithoutProducts.iCount, Message := 'JamWithoutProducts#5 iCount');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbJamWithoutProducts.wCountBcd,
                      Message := 'JamWithoutProducts#5 wCountBcd');

    // #6, t = 7100 мс — затор сбросил запрос: выбег 3 с
    GVL_S7Clock.tSimNow := T#7100MS;
    fbJamWithoutProducts();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbJamWithoutProducts.xHorn, Message := 'JamWithoutProducts#6 xHorn');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbJamWithoutProducts.xMotor,
                      Message := 'JamWithoutProducts#6 xMotor');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbJamWithoutProducts.xFlowOk,
                      Message := 'JamWithoutProducts#6 xFlowOk');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbJamWithoutProducts.xJam, Message := 'JamWithoutProducts#6 xJam');
    AssertEquals_INT(Expected := 0,
                     Actual := fbJamWithoutProducts.iDelayLeft,
                     Message := 'JamWithoutProducts#6 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0300,
                      Actual := fbJamWithoutProducts.wRunOutBcd,
                      Message := 'JamWithoutProducts#6 wRunOutBcd');
    AssertEquals_INT(Expected := 0, Actual := fbJamWithoutProducts.iCount, Message := 'JamWithoutProducts#6 iCount');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbJamWithoutProducts.wCountBcd,
                      Message := 'JamWithoutProducts#6 wCountBcd');

    // #7, t = 10100 мс, на пороге таймера — выбег закончен: двигатель остановлен, T5 сброшен
    GVL_S7Clock.tSimNow := T#10100MS;
    fbJamWithoutProducts();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbJamWithoutProducts.xHorn, Message := 'JamWithoutProducts#7 xHorn');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbJamWithoutProducts.xMotor,
                      Message := 'JamWithoutProducts#7 xMotor');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbJamWithoutProducts.xFlowOk,
                      Message := 'JamWithoutProducts#7 xFlowOk');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbJamWithoutProducts.xJam, Message := 'JamWithoutProducts#7 xJam');
    AssertEquals_INT(Expected := 0,
                     Actual := fbJamWithoutProducts.iDelayLeft,
                     Message := 'JamWithoutProducts#7 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbJamWithoutProducts.wRunOutBcd,
                      Message := 'JamWithoutProducts#7 wRunOutBcd');
    AssertEquals_INT(Expected := 0, Actual := fbJamWithoutProducts.iCount, Message := 'JamWithoutProducts#7 iCount');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbJamWithoutProducts.wCountBcd,
                      Message := 'JamWithoutProducts#7 wCountBcd');

    // #8, t = 10500 мс — квитирование: затор снят
    GVL_S7Clock.tSimNow := T#10500MS;
    fbJamWithoutProducts.xAck := TRUE;
    fbJamWithoutProducts();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbJamWithoutProducts.xHorn, Message := 'JamWithoutProducts#8 xHorn');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbJamWithoutProducts.xMotor,
                      Message := 'JamWithoutProducts#8 xMotor');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbJamWithoutProducts.xFlowOk,
                      Message := 'JamWithoutProducts#8 xFlowOk');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbJamWithoutProducts.xJam, Message := 'JamWithoutProducts#8 xJam');
    AssertEquals_INT(Expected := 0,
                     Actual := fbJamWithoutProducts.iDelayLeft,
                     Message := 'JamWithoutProducts#8 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbJamWithoutProducts.wRunOutBcd,
                      Message := 'JamWithoutProducts#8 wRunOutBcd');
    AssertEquals_INT(Expected := 0, Actual := fbJamWithoutProducts.iCount, Message := 'JamWithoutProducts#8 iCount');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbJamWithoutProducts.wCountBcd,
                      Message := 'JamWithoutProducts#8 wCountBcd');

    // #9, t = 10600 мс — покой
    GVL_S7Clock.tSimNow := T#10600MS;
    fbJamWithoutProducts.xAck := FALSE;
    fbJamWithoutProducts();
    AssertEquals_BOOL(Expected := FALSE, Actual := fbJamWithoutProducts.xHorn, Message := 'JamWithoutProducts#9 xHorn');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbJamWithoutProducts.xMotor,
                      Message := 'JamWithoutProducts#9 xMotor');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbJamWithoutProducts.xFlowOk,
                      Message := 'JamWithoutProducts#9 xFlowOk');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbJamWithoutProducts.xJam, Message := 'JamWithoutProducts#9 xJam');
    AssertEquals_INT(Expected := 0,
                     Actual := fbJamWithoutProducts.iDelayLeft,
                     Message := 'JamWithoutProducts#9 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbJamWithoutProducts.wRunOutBcd,
                      Message := 'JamWithoutProducts#9 wRunOutBcd');
    AssertEquals_INT(Expected := 0, Actual := fbJamWithoutProducts.iCount, Message := 'JamWithoutProducts#9 iCount');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbJamWithoutProducts.wCountBcd,
                      Message := 'JamWithoutProducts#9 wCountBcd');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
