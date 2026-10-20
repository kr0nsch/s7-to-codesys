// Сеть 1 (GRAPH): Промывка фильтра
tGraphNow := F_S7Now();
// Состояние шагов прошлого вызова: события S1/S0 — и от INIT_SQ, OFF_SQ
xIdle_Prev := Idle_X;
xDrain_Prev := Drain_X;
xAir_Prev := Air_X;
xRinse_Prev := Rinse_X;
xQuickRinse_Prev := QuickRinse_X;
xRefill_Prev := Refill_X;
xGraphHold := INIT_SQ OR NOT GraphInitDone OR OFF_SQ;
// Начальное состояние (INIT_SQ, первый вызов) и выключение (OFF_SQ)
IF INIT_SQ OR NOT GraphInitDone THEN
    GraphInitDone := TRUE;
    Idle_X := TRUE;
    Idle_Start := tGraphNow;
    Idle_T := T#0MS;
    Drain_X := FALSE;
    Air_X := FALSE;
    Rinse_X := FALSE;
    QuickRinse_X := FALSE;
    Refill_X := FALSE;
    Drain_SvErr := FALSE;
END_IF
IF OFF_SQ THEN
    Idle_X := FALSE;
    Drain_X := FALSE;
    Air_X := FALSE;
    Rinse_X := FALSE;
    QuickRinse_X := FALSE;
    Refill_X := FALSE;
END_IF
// Квитирование ошибок контроля (ACK_EF): в этом вызове переход возможен
IF ACK_EF THEN
    Drain_SvErr := FALSE;
END_IF
// Время активных шагов
IF Idle_X THEN
    Idle_T := F_S7TimeDiff(tGraphNow, Idle_Start);
END_IF
IF Drain_X THEN
    Drain_T := F_S7TimeDiff(tGraphNow, Drain_Start);
END_IF
IF Air_X THEN
    Air_T := F_S7TimeDiff(tGraphNow, Air_Start);
END_IF
IF Rinse_X THEN
    Rinse_T := F_S7TimeDiff(tGraphNow, Rinse_Start);
END_IF
IF QuickRinse_X THEN
    QuickRinse_T := F_S7TimeDiff(tGraphNow, QuickRinse_Start);
END_IF
IF Refill_X THEN
    Refill_T := F_S7TimeDiff(tGraphNow, Refill_Start);
END_IF
// Условия переходов (сети LAD/FBD)
// MIGRATION-CHECK: элемент «TrCoil»: имя и пины в SimaticML не подтверждены открытым экспортом
//                  (docs/MAPPING_LADFBD.md, уровень L) (FB_BackwashGraph.xml, сеть 1 (GRAPH), переход T1, UId 23)
xT1_Cond := xStart;
// MIGRATION-CHECK: элемент «TrCoil»: имя и пины в SimaticML не подтверждены открытым экспортом
//                  (docs/MAPPING_LADFBD.md, уровень L) (FB_BackwashGraph.xml, сеть 1 (GRAPH), переход T2, UId 25)
xT2_Cond := xLevelLow AND NOT xShortWash;
// MIGRATION-CHECK: элемент «TrCoil»: имя и пины в SimaticML не подтверждены открытым экспортом
//                  (docs/MAPPING_LADFBD.md, уровень L) (FB_BackwashGraph.xml, сеть 1 (GRAPH), переход T3, UId 25)
xT3_Cond := xLevelLow AND xShortWash;
// MIGRATION-CHECK: элемент «TrCoil»: имя и пины в SimaticML не подтверждены открытым экспортом
//                  (docs/MAPPING_LADFBD.md, уровень L) (FB_BackwashGraph.xml, сеть 1 (GRAPH), переход T4, UId 24)
xT4_Cond := Air_T >= T#10S;
// MIGRATION-CHECK: элемент «TrCoil»: имя и пины в SimaticML не подтверждены открытым экспортом
//                  (docs/MAPPING_LADFBD.md, уровень L) (FB_BackwashGraph.xml, сеть 1 (GRAPH), переход T5, UId 23)
xT5_Cond := xLevelHigh;
// MIGRATION-CHECK: элемент «TrCoil»: имя и пины в SimaticML не подтверждены открытым экспортом
//                  (docs/MAPPING_LADFBD.md, уровень L) (FB_BackwashGraph.xml, сеть 1 (GRAPH), переход T6, UId 23)
xT6_Cond := xLevelHigh;
// Срабатывание: предшественники активны, условие, нет ошибки контроля; альтернативы — слева направо
xT1_Fire := Idle_X AND xT1_Cond AND NOT xGraphHold;
xT2_Fire := Drain_X AND xT2_Cond AND NOT xGraphHold AND NOT Drain_SvErr;
// MIGRATION-CHECK: альтернативная ветвь: из одновременно истинных переходов срабатывает левый (первый); настройку
//                  блока S7-1500 сверить (FB_BackwashGraph.xml, сеть 1 (GRAPH), переход T3)
xT3_Fire := Drain_X AND xT3_Cond AND NOT xGraphHold AND NOT Drain_SvErr AND NOT xT2_Fire;
xT4_Fire := Air_X AND Rinse_X AND xT4_Cond AND NOT xGraphHold;
xT5_Fire := QuickRinse_X AND xT5_Cond AND NOT xGraphHold;
xT6_Fire := Refill_X AND xT6_Cond AND NOT xGraphHold;
// Переключение: сначала выключение предшественников, затем включение преемников
IF xT1_Fire THEN
    Idle_X := FALSE;
END_IF
IF xT2_Fire THEN
    Drain_X := FALSE;
END_IF
IF xT3_Fire THEN
    Drain_X := FALSE;
END_IF
IF xT4_Fire THEN
    Air_X := FALSE;
    Rinse_X := FALSE;
END_IF
IF xT5_Fire THEN
    QuickRinse_X := FALSE;
END_IF
IF xT6_Fire THEN
    Refill_X := FALSE;
END_IF
IF xT1_Fire THEN
    Drain_X := TRUE;
END_IF
IF xT2_Fire THEN
    Air_X := TRUE;
    Rinse_X := TRUE;
END_IF
IF xT3_Fire THEN
    QuickRinse_X := TRUE;
END_IF
IF xT4_Fire THEN
    Refill_X := TRUE;
END_IF
IF xT5_Fire THEN
    Refill_X := TRUE;
END_IF
IF xT6_Fire THEN
    Idle_X := TRUE;
END_IF
// События шагов S1/S0; активация — новый отсчёт времени
xIdle_S1 := Idle_X AND NOT xIdle_Prev;
xIdle_S0 := xIdle_Prev AND NOT Idle_X;
IF xIdle_S1 THEN
    Idle_Start := tGraphNow;
    Idle_T := T#0MS;
END_IF
xDrain_S1 := Drain_X AND NOT xDrain_Prev;
xDrain_S0 := xDrain_Prev AND NOT Drain_X;
IF xDrain_S1 THEN
    Drain_Start := tGraphNow;
    Drain_T := T#0MS;
END_IF
xAir_S1 := Air_X AND NOT xAir_Prev;
xAir_S0 := xAir_Prev AND NOT Air_X;
IF xAir_S1 THEN
    Air_Start := tGraphNow;
    Air_T := T#0MS;
END_IF
xRinse_S1 := Rinse_X AND NOT xRinse_Prev;
xRinse_S0 := xRinse_Prev AND NOT Rinse_X;
IF xRinse_S1 THEN
    Rinse_Start := tGraphNow;
    Rinse_T := T#0MS;
END_IF
xQuickRinse_S1 := QuickRinse_X AND NOT xQuickRinse_Prev;
xQuickRinse_S0 := xQuickRinse_Prev AND NOT QuickRinse_X;
IF xQuickRinse_S1 THEN
    QuickRinse_Start := tGraphNow;
    QuickRinse_T := T#0MS;
END_IF
xRefill_S1 := Refill_X AND NOT xRefill_Prev;
xRefill_S0 := xRefill_Prev AND NOT Refill_X;
IF xRefill_S1 THEN
    Refill_Start := tGraphNow;
    Refill_T := T#0MS;
END_IF
// Контроль шага S2 Drain
// MIGRATION-CHECK: элемент «SvCoil»: имя и пины в SimaticML не подтверждены открытым экспортом
//                  (docs/MAPPING_LADFBD.md, уровень L) (FB_BackwashGraph.xml, сеть 1 (GRAPH), шаг S2, контроль, UId
//                  23)
xDrain_Sv := xValveFault;
// MIGRATION-CHECK: контроль S2: ошибка защёлкивается и держит шаг до ACK_EF; Si.U и сообщения ProDiag не
//                  переносятся (FB_BackwashGraph.xml, сеть 1 (GRAPH), шаг S2, контроль)
IF Drain_X AND xDrain_Sv THEN
    Drain_SvErr := TRUE;
END_IF
// Блокировка шага S4 Rinse
// MIGRATION-CHECK: элемент «IlCoil»: имя и пины в SimaticML не подтверждены открытым экспортом
//                  (docs/MAPPING_LADFBD.md, уровень L) (FB_BackwashGraph.xml, сеть 1 (GRAPH), шаг S4, блокировка,
//                  UId 23)
xRinse_Il := xPumpOk;
// Действия шага S1 Idle
IF Idle_X OR xIdle_S0 THEN
    xReady := Idle_X;
END_IF
// Действия шага S2 Drain
IF Drain_X OR xDrain_S0 THEN
    xDrainValve := Drain_X;
END_IF
IF Drain_X THEN
    xWashActive := TRUE;
END_IF
IF xDrain_S1 THEN
    iWashCount := iWashCount + 1;
END_IF
// Действия шага S3 Air
IF Air_X OR xAir_S0 THEN
    xBlower := Air_X;
END_IF
// MIGRATION-CHECK: S3: D #xAirValve, T#2S — по времени шага #Air_T (F_S7Now); в SFC — IEC D по своему таймеру
//                  (FB_BackwashGraph.xml, сеть 1 (GRAPH), шаг S3, действие 2)
IF Air_X OR xAir_S0 THEN
    xAirValve := Air_X AND Air_T >= T#2S;
END_IF
// Действия шага S4 Rinse
IF Rinse_X OR xRinse_S0 THEN
    xWashPump := Rinse_X AND xRinse_Il;
END_IF
// Действия шага S5 QuickRinse
IF QuickRinse_X OR xQuickRinse_S0 THEN
    xWashPump := QuickRinse_X;
END_IF
// Действия шага S6 Refill
IF Refill_X OR xRefill_S0 THEN
    xInletValve := Refill_X;
END_IF
IF Refill_X THEN
    xWashActive := FALSE;
END_IF
ERR_FLT := Drain_SvErr;
// Постоперация 1
xValvesBusy := xDrainValve OR xInletValve;
