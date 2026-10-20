// Сеть 1: Запрос работы
IF xStart THEN
    xReq := TRUE;
END_IF
IF xStop OR xJam THEN
    xReq := FALSE;
END_IF
// Сеть 2: Сирена 1 с при запросе (SP)
// MIGRATION-CHECK: SP T1 → F_S5Pulse (S7Compat): время — F_S7Now(), остаток пересчитывается при обращении к
//                  таймеру; фаза часового процесса CPU (точность ±1 единица шкалы) не моделируется
//                  (FB_ConveyorStl.xml, сеть 2, строка 3)
F_S5Pulse(stTimer := GVL_S5Timers_Lang.aTimer[1], xRlo := xReq, wS5Time := F_S5TimeWord(T#1S));
xHorn := F_S5Q(stTimer := GVL_S5Timers_Lang.aTimer[1]);
// Сеть 3: Задержка пуска 2 с (SD)
// MIGRATION-CHECK: SD T2 → F_S5OnDelay (S7Compat): время — F_S7Now(), остаток пересчитывается при обращении к
//                  таймеру; фаза часового процесса CPU (точность ±1 единица шкалы) не моделируется
//                  (FB_ConveyorStl.xml, сеть 3, строка 3)
F_S5OnDelay(stTimer := GVL_S5Timers_Lang.aTimer[2], xRlo := xReq, wS5Time := F_S5TimeWord(T#2S));
// Сеть 4: Выбег 3 с после снятия запроса (SF)
// MIGRATION-CHECK: SF T3 → F_S5OffDelay (S7Compat): время — F_S7Now(), остаток пересчитывается при обращении к
//                  таймеру; фаза часового процесса CPU (точность ±1 единица шкалы) не моделируется
//                  (FB_ConveyorStl.xml, сеть 4, строка 3)
F_S5OffDelay(stTimer := GVL_S5Timers_Lang.aTimer[3],
             xRlo := F_S5Q(stTimer := GVL_S5Timers_Lang.aTimer[2]),
             wS5Time := F_S5TimeWord(T#3S));
xMotor := F_S5Q(stTimer := GVL_S5Timers_Lang.aTimer[3]);
// Сеть 5: Контроль потока (SE) и затор (SS)
// MIGRATION-CHECK: SE T4 → F_S5ExtPulse (S7Compat): время — F_S7Now(), остаток пересчитывается при обращении к
//                  таймеру; фаза часового процесса CPU (точность ±1 единица шкалы) не моделируется
//                  (FB_ConveyorStl.xml, сеть 5, строка 3)
F_S5ExtPulse(stTimer := GVL_S5Timers_Lang.aTimer[4], xRlo := xSensor, wS5Time := F_S5TimeWord(T#4S));
xFlowOk := F_S5Q(stTimer := GVL_S5Timers_Lang.aTimer[4]);
// MIGRATION-CHECK: SS T5 → F_S5RetOnDelay (S7Compat): время — F_S7Now(), остаток пересчитывается при обращении к
//                  таймеру; фаза часового процесса CPU (точность ±1 единица шкалы) не моделируется
//                  (FB_ConveyorStl.xml, сеть 5, строка 8)
F_S5RetOnDelay(stTimer := GVL_S5Timers_Lang.aTimer[5], xRlo := xMotor, wS5Time := F_S5TimeWord(T#5S));
F_S5Reset(stTimer := GVL_S5Timers_Lang.aTimer[5], xRlo := NOT xMotor);
IF F_S5Q(stTimer := GVL_S5Timers_Lang.aTimer[5]) AND NOT F_S5Q(stTimer := GVL_S5Timers_Lang.aTimer[4]) THEN
    xJam := TRUE;
END_IF
F_S5Enable(stTimer := GVL_S5Timers_Lang.aTimer[4], xRlo := xAck);
IF xAck THEN
    xJam := FALSE;
END_IF
// Сеть 6: Диагностика: остатки таймеров
iDelayLeft := WORD_TO_INT(F_S5Bin(stTimer := GVL_S5Timers_Lang.aTimer[2]));
wRunOutBcd := F_S5Bcd(stTimer := GVL_S5Timers_Lang.aTimer[3]);
// Сеть 7: Счётчик изделий (C1)
F_S5CountUp(stCounter := GVL_S5Counters_Lang.aCounter[1], xRlo := xSensor);
F_S5CounterReset(stCounter := GVL_S5Counters_Lang.aCounter[1], xRlo := xCountReset);
iCount := WORD_TO_INT(F_S5CounterBin(stCounter := GVL_S5Counters_Lang.aCounter[1]));
wCountBcd := F_S5CounterBcd(stCounter := GVL_S5Counters_Lang.aCounter[1]);
