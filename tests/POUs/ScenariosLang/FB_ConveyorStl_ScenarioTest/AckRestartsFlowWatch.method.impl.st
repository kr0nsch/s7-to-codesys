// AUTO-GENERATED — не редактировать: scenarios/lang/FB_ConveyorStl.csv, сценарий AckRestartsFlowWatch
coUnit.TEST('AckRestartsFlowWatch');
IF NOT xAckRestartsFlowWatchDone THEN
    xAckRestartsFlowWatchDone := TRUE;
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
    fbAckRestartsFlowWatch.xStart := TRUE;
    fbAckRestartsFlowWatch.xStop := FALSE;
    fbAckRestartsFlowWatch.xSensor := FALSE;
    fbAckRestartsFlowWatch.xAck := FALSE;
    fbAckRestartsFlowWatch.xCountReset := FALSE;
    fbAckRestartsFlowWatch();
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbAckRestartsFlowWatch.xHorn,
                      Message := 'AckRestartsFlowWatch#1 xHorn');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbAckRestartsFlowWatch.xMotor,
                      Message := 'AckRestartsFlowWatch#1 xMotor');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbAckRestartsFlowWatch.xFlowOk,
                      Message := 'AckRestartsFlowWatch#1 xFlowOk');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbAckRestartsFlowWatch.xJam,
                      Message := 'AckRestartsFlowWatch#1 xJam');
    AssertEquals_INT(Expected := 200,
                     Actual := fbAckRestartsFlowWatch.iDelayLeft,
                     Message := 'AckRestartsFlowWatch#1 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbAckRestartsFlowWatch.wRunOutBcd,
                      Message := 'AckRestartsFlowWatch#1 wRunOutBcd');
    AssertEquals_INT(Expected := 0,
                     Actual := fbAckRestartsFlowWatch.iCount,
                     Message := 'AckRestartsFlowWatch#1 iCount');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbAckRestartsFlowWatch.wCountBcd,
                      Message := 'AckRestartsFlowWatch#1 wCountBcd');

    // #2, t = 100 мс — кнопка отпущена
    GVL_S7Clock.tSimNow := T#100MS;
    fbAckRestartsFlowWatch.xStart := FALSE;
    fbAckRestartsFlowWatch();
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbAckRestartsFlowWatch.xHorn,
                      Message := 'AckRestartsFlowWatch#2 xHorn');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbAckRestartsFlowWatch.xMotor,
                      Message := 'AckRestartsFlowWatch#2 xMotor');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbAckRestartsFlowWatch.xFlowOk,
                      Message := 'AckRestartsFlowWatch#2 xFlowOk');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbAckRestartsFlowWatch.xJam,
                      Message := 'AckRestartsFlowWatch#2 xJam');
    AssertEquals_INT(Expected := 190,
                     Actual := fbAckRestartsFlowWatch.iDelayLeft,
                     Message := 'AckRestartsFlowWatch#2 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbAckRestartsFlowWatch.wRunOutBcd,
                      Message := 'AckRestartsFlowWatch#2 wRunOutBcd');
    AssertEquals_INT(Expected := 0,
                     Actual := fbAckRestartsFlowWatch.iCount,
                     Message := 'AckRestartsFlowWatch#2 iCount');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbAckRestartsFlowWatch.wCountBcd,
                      Message := 'AckRestartsFlowWatch#2 wCountBcd');

    // #3, t = 2000 мс, на пороге таймера — 2 с: задержка T2 истекла — двигатель (T3 = 1)
    GVL_S7Clock.tSimNow := T#2000MS;
    fbAckRestartsFlowWatch();
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbAckRestartsFlowWatch.xHorn,
                      Message := 'AckRestartsFlowWatch#3 xHorn');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbAckRestartsFlowWatch.xMotor,
                      Message := 'AckRestartsFlowWatch#3 xMotor');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbAckRestartsFlowWatch.xFlowOk,
                      Message := 'AckRestartsFlowWatch#3 xFlowOk');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbAckRestartsFlowWatch.xJam,
                      Message := 'AckRestartsFlowWatch#3 xJam');
    AssertEquals_INT(Expected := 0,
                     Actual := fbAckRestartsFlowWatch.iDelayLeft,
                     Message := 'AckRestartsFlowWatch#3 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbAckRestartsFlowWatch.wRunOutBcd,
                      Message := 'AckRestartsFlowWatch#3 wRunOutBcd');
    AssertEquals_INT(Expected := 0,
                     Actual := fbAckRestartsFlowWatch.iCount,
                     Message := 'AckRestartsFlowWatch#3 iCount');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbAckRestartsFlowWatch.wCountBcd,
                      Message := 'AckRestartsFlowWatch#3 wCountBcd');

    // #4, t = 2500 мс — датчик залип в 1: T4 пошёл один раз, изделие №1
    GVL_S7Clock.tSimNow := T#2500MS;
    fbAckRestartsFlowWatch.xSensor := TRUE;
    fbAckRestartsFlowWatch();
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbAckRestartsFlowWatch.xHorn,
                      Message := 'AckRestartsFlowWatch#4 xHorn');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbAckRestartsFlowWatch.xMotor,
                      Message := 'AckRestartsFlowWatch#4 xMotor');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbAckRestartsFlowWatch.xFlowOk,
                      Message := 'AckRestartsFlowWatch#4 xFlowOk');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbAckRestartsFlowWatch.xJam,
                      Message := 'AckRestartsFlowWatch#4 xJam');
    AssertEquals_INT(Expected := 0,
                     Actual := fbAckRestartsFlowWatch.iDelayLeft,
                     Message := 'AckRestartsFlowWatch#4 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbAckRestartsFlowWatch.wRunOutBcd,
                      Message := 'AckRestartsFlowWatch#4 wRunOutBcd');
    AssertEquals_INT(Expected := 1,
                     Actual := fbAckRestartsFlowWatch.iCount,
                     Message := 'AckRestartsFlowWatch#4 iCount');
    AssertEquals_WORD(Expected := 16#0001,
                      Actual := fbAckRestartsFlowWatch.wCountBcd,
                      Message := 'AckRestartsFlowWatch#4 wCountBcd');

    // #5, t = 6500 мс, на пороге таймера — 4 с: T4 истёк, фронтов нет
    GVL_S7Clock.tSimNow := T#6500MS;
    fbAckRestartsFlowWatch();
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbAckRestartsFlowWatch.xHorn,
                      Message := 'AckRestartsFlowWatch#5 xHorn');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbAckRestartsFlowWatch.xMotor,
                      Message := 'AckRestartsFlowWatch#5 xMotor');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbAckRestartsFlowWatch.xFlowOk,
                      Message := 'AckRestartsFlowWatch#5 xFlowOk');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbAckRestartsFlowWatch.xJam,
                      Message := 'AckRestartsFlowWatch#5 xJam');
    AssertEquals_INT(Expected := 0,
                     Actual := fbAckRestartsFlowWatch.iDelayLeft,
                     Message := 'AckRestartsFlowWatch#5 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbAckRestartsFlowWatch.wRunOutBcd,
                      Message := 'AckRestartsFlowWatch#5 wRunOutBcd');
    AssertEquals_INT(Expected := 1,
                     Actual := fbAckRestartsFlowWatch.iCount,
                     Message := 'AckRestartsFlowWatch#5 iCount');
    AssertEquals_WORD(Expected := 16#0001,
                      Actual := fbAckRestartsFlowWatch.wCountBcd,
                      Message := 'AckRestartsFlowWatch#5 wCountBcd');

    // #6, t = 7000 мс, на пороге таймера — контроль взведён: затор
    GVL_S7Clock.tSimNow := T#7000MS;
    fbAckRestartsFlowWatch();
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbAckRestartsFlowWatch.xHorn,
                      Message := 'AckRestartsFlowWatch#6 xHorn');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbAckRestartsFlowWatch.xMotor,
                      Message := 'AckRestartsFlowWatch#6 xMotor');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbAckRestartsFlowWatch.xFlowOk,
                      Message := 'AckRestartsFlowWatch#6 xFlowOk');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbAckRestartsFlowWatch.xJam,
                      Message := 'AckRestartsFlowWatch#6 xJam');
    AssertEquals_INT(Expected := 0,
                     Actual := fbAckRestartsFlowWatch.iDelayLeft,
                     Message := 'AckRestartsFlowWatch#6 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbAckRestartsFlowWatch.wRunOutBcd,
                      Message := 'AckRestartsFlowWatch#6 wRunOutBcd');
    AssertEquals_INT(Expected := 1,
                     Actual := fbAckRestartsFlowWatch.iCount,
                     Message := 'AckRestartsFlowWatch#6 iCount');
    AssertEquals_WORD(Expected := 16#0001,
                      Actual := fbAckRestartsFlowWatch.wCountBcd,
                      Message := 'AckRestartsFlowWatch#6 wCountBcd');

    // #7, t = 7100 мс — запрос снят: выбег
    GVL_S7Clock.tSimNow := T#7100MS;
    fbAckRestartsFlowWatch();
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbAckRestartsFlowWatch.xHorn,
                      Message := 'AckRestartsFlowWatch#7 xHorn');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbAckRestartsFlowWatch.xMotor,
                      Message := 'AckRestartsFlowWatch#7 xMotor');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbAckRestartsFlowWatch.xFlowOk,
                      Message := 'AckRestartsFlowWatch#7 xFlowOk');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbAckRestartsFlowWatch.xJam,
                      Message := 'AckRestartsFlowWatch#7 xJam');
    AssertEquals_INT(Expected := 0,
                     Actual := fbAckRestartsFlowWatch.iDelayLeft,
                     Message := 'AckRestartsFlowWatch#7 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0300,
                      Actual := fbAckRestartsFlowWatch.wRunOutBcd,
                      Message := 'AckRestartsFlowWatch#7 wRunOutBcd');
    AssertEquals_INT(Expected := 1,
                     Actual := fbAckRestartsFlowWatch.iCount,
                     Message := 'AckRestartsFlowWatch#7 iCount');
    AssertEquals_WORD(Expected := 16#0001,
                      Actual := fbAckRestartsFlowWatch.wCountBcd,
                      Message := 'AckRestartsFlowWatch#7 wCountBcd');

    // #8, t = 10100 мс, на пороге таймера — выбег закончен
    GVL_S7Clock.tSimNow := T#10100MS;
    fbAckRestartsFlowWatch();
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbAckRestartsFlowWatch.xHorn,
                      Message := 'AckRestartsFlowWatch#8 xHorn');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbAckRestartsFlowWatch.xMotor,
                      Message := 'AckRestartsFlowWatch#8 xMotor');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbAckRestartsFlowWatch.xFlowOk,
                      Message := 'AckRestartsFlowWatch#8 xFlowOk');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbAckRestartsFlowWatch.xJam,
                      Message := 'AckRestartsFlowWatch#8 xJam');
    AssertEquals_INT(Expected := 0,
                     Actual := fbAckRestartsFlowWatch.iDelayLeft,
                     Message := 'AckRestartsFlowWatch#8 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbAckRestartsFlowWatch.wRunOutBcd,
                      Message := 'AckRestartsFlowWatch#8 wRunOutBcd');
    AssertEquals_INT(Expected := 1,
                     Actual := fbAckRestartsFlowWatch.iCount,
                     Message := 'AckRestartsFlowWatch#8 iCount');
    AssertEquals_WORD(Expected := 16#0001,
                      Actual := fbAckRestartsFlowWatch.wCountBcd,
                      Message := 'AckRestartsFlowWatch#8 wCountBcd');

    // #9, t = 10500 мс — квитирование: затор снят, FR T4 (SE в этом вызове уже прошёл)
    GVL_S7Clock.tSimNow := T#10500MS;
    fbAckRestartsFlowWatch.xAck := TRUE;
    fbAckRestartsFlowWatch();
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbAckRestartsFlowWatch.xHorn,
                      Message := 'AckRestartsFlowWatch#9 xHorn');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbAckRestartsFlowWatch.xMotor,
                      Message := 'AckRestartsFlowWatch#9 xMotor');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbAckRestartsFlowWatch.xFlowOk,
                      Message := 'AckRestartsFlowWatch#9 xFlowOk');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbAckRestartsFlowWatch.xJam,
                      Message := 'AckRestartsFlowWatch#9 xJam');
    AssertEquals_INT(Expected := 0,
                     Actual := fbAckRestartsFlowWatch.iDelayLeft,
                     Message := 'AckRestartsFlowWatch#9 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbAckRestartsFlowWatch.wRunOutBcd,
                      Message := 'AckRestartsFlowWatch#9 wRunOutBcd');
    AssertEquals_INT(Expected := 1,
                     Actual := fbAckRestartsFlowWatch.iCount,
                     Message := 'AckRestartsFlowWatch#9 iCount');
    AssertEquals_WORD(Expected := 16#0001,
                      Actual := fbAckRestartsFlowWatch.wCountBcd,
                      Message := 'AckRestartsFlowWatch#9 wCountBcd');

    // #10, t = 10600 мс — следующий вызов: SE видит фронт — T4 перезапущен
    GVL_S7Clock.tSimNow := T#10600MS;
    fbAckRestartsFlowWatch.xAck := FALSE;
    fbAckRestartsFlowWatch();
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbAckRestartsFlowWatch.xHorn,
                      Message := 'AckRestartsFlowWatch#10 xHorn');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbAckRestartsFlowWatch.xMotor,
                      Message := 'AckRestartsFlowWatch#10 xMotor');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbAckRestartsFlowWatch.xFlowOk,
                      Message := 'AckRestartsFlowWatch#10 xFlowOk');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbAckRestartsFlowWatch.xJam,
                      Message := 'AckRestartsFlowWatch#10 xJam');
    AssertEquals_INT(Expected := 0,
                     Actual := fbAckRestartsFlowWatch.iDelayLeft,
                     Message := 'AckRestartsFlowWatch#10 iDelayLeft');
    AssertEquals_WORD(Expected := 16#0000,
                      Actual := fbAckRestartsFlowWatch.wRunOutBcd,
                      Message := 'AckRestartsFlowWatch#10 wRunOutBcd');
    AssertEquals_INT(Expected := 1,
                     Actual := fbAckRestartsFlowWatch.iCount,
                     Message := 'AckRestartsFlowWatch#10 iCount');
    AssertEquals_WORD(Expected := 16#0001,
                      Actual := fbAckRestartsFlowWatch.wCountBcd,
                      Message := 'AckRestartsFlowWatch#10 wCountBcd');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
