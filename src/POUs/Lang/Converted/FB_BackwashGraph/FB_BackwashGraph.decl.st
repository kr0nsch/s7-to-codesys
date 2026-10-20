// Назначение: Промывка фильтра (GRAPH)
//             Промывка скорого фильтра (GRAPH S7-1500), шаги S1–S6. S1 Idle (начальный): N xReady.
//             T1 Start: xStart. S2 Drain: N xDrainValve, S xWashActive, событие S1 — iWashCount + 1;
//             контроль xValveFault держит шаг до квитирования ACK_EF (ERR_FLT = 1). После S2 альтернатива:
//             T2 LongWash (xLevelLow AND NOT xShortWash) — параллельно S3 Air (N xBlower, D xAirValve 2 с)
//             и S4 Rinse (NC xWashPump, блокировка xPumpOk), синхронизация T4 AirDone: Air.T >= 10 с;
//             T3 ShortWash (xLevelLow AND xShortWash) — S5 QuickRinse (N xWashPump), T5 QuickDone: xLevelHigh.
//             S6 Refill: N xInletValve, R xWashActive; T6 Full: xLevelHigh — прыжок к S1. Постоперация:
//             xValvesBusy := xDrainValve OR xInletValve. INIT_SQ — начальное состояние, OFF_SQ — шаги выключены.
// Автор:      WTP2 (исходный блок S7); перевод в ST — s7conv 0.1.0
// Версия:     0.1 (исходный блок S7)
// Документ:   docs/CONVERSION_REPORT.md, docs/MAPPING.md
// Источник:   samples/lang/FB_BackwashGraph.xml, GRAPH, SW.Blocks.FB "FB_BackwashGraph", пространство имён
//             Interface/v5, FAMILY Filters
// Сгенерировано s7conv: пометки MIGRATION-CHECK и MIGRATION-TODO требуют ручного разбора.
FUNCTION_BLOCK FB_BackwashGraph
VAR_INPUT
    OFF_SQ : BOOL;  // Выключить последовательность
    INIT_SQ : BOOL;  // Начальное состояние
    ACK_EF : BOOL;  // Квитирование ошибок контроля
    xStart : BOOL;  // Пуск промывки
    xLevelLow : BOOL;  // Уровень ниже сливного
    xLevelHigh : BOOL;  // Фильтр заполнен
    xShortWash : BOOL;  // Короткая промывка (без продувки)
    xPumpOk : BOOL := TRUE;  // Насос промывки исправен
    xValveFault : BOOL;  // Неисправность сливной задвижки
END_VAR
VAR_OUTPUT
    ERR_FLT : BOOL;  // Ошибка контроля (до квитирования)
    xReady : BOOL;  // Готов к промывке
    xDrainValve : BOOL;  // Сливная задвижка
    xBlower : BOOL;  // Воздуходувка
    xAirValve : BOOL;  // Задвижка воздуха
    xWashPump : BOOL;  // Насос промывки
    xInletValve : BOOL;  // Задвижка подачи
    xWashActive : BOOL;  // Промывка идёт
    xValvesBusy : BOOL;  // Задвижки в работе
    iWashCount : INT;  // Число промывок
END_VAR
VAR_TEMP
    tGraphNow : TIME;  // GRAPH: время вызова (F_S7Now)
    xIdle_Prev : BOOL;  // шаг S1: активен в прошлом вызове
    xIdle_S1 : BOOL;  // шаг S1: событие S1 (активирован)
    xIdle_S0 : BOOL;  // шаг S1: событие S0 (выключен)
    xDrain_Prev : BOOL;  // шаг S2: активен в прошлом вызове
    xDrain_S1 : BOOL;  // шаг S2: событие S1 (активирован)
    xDrain_S0 : BOOL;  // шаг S2: событие S0 (выключен)
    xAir_Prev : BOOL;  // шаг S3: активен в прошлом вызове
    xAir_S1 : BOOL;  // шаг S3: событие S1 (активирован)
    xAir_S0 : BOOL;  // шаг S3: событие S0 (выключен)
    xRinse_Prev : BOOL;  // шаг S4: активен в прошлом вызове
    xRinse_S1 : BOOL;  // шаг S4: событие S1 (активирован)
    xRinse_S0 : BOOL;  // шаг S4: событие S0 (выключен)
    xRinse_Il : BOOL;  // шаг S4: блокировка выполнена
    xQuickRinse_Prev : BOOL;  // шаг S5: активен в прошлом вызове
    xQuickRinse_S1 : BOOL;  // шаг S5: событие S1 (активирован)
    xQuickRinse_S0 : BOOL;  // шаг S5: событие S0 (выключен)
    xRefill_Prev : BOOL;  // шаг S6: активен в прошлом вызове
    xRefill_S1 : BOOL;  // шаг S6: событие S1 (активирован)
    xRefill_S0 : BOOL;  // шаг S6: событие S0 (выключен)
    xGraphHold : BOOL;  // GRAPH: INIT_SQ, OFF_SQ или первый вызов — переходы не срабатывают
    xT1_Cond : BOOL;  // переход T1 Start: условие
    xT1_Fire : BOOL;  // переход T1: срабатывает
    xT2_Cond : BOOL;  // переход T2 LongWash: условие
    xT2_Fire : BOOL;  // переход T2: срабатывает
    xT3_Cond : BOOL;  // переход T3 ShortWash: условие
    xT3_Fire : BOOL;  // переход T3: срабатывает
    xT4_Cond : BOOL;  // переход T4 AirDone: условие
    xT4_Fire : BOOL;  // переход T4: срабатывает
    xT5_Cond : BOOL;  // переход T5 QuickDone: условие
    xT5_Fire : BOOL;  // переход T5: срабатывает
    xT6_Cond : BOOL;  // переход T6 Full: условие
    xT6_Fire : BOOL;  // переход T6: срабатывает
    xDrain_Sv : BOOL;  // шаг S2: условие контроля
END_VAR
VAR
    GraphInitDone : BOOL;  // GRAPH: начальное состояние установлено
    Idle_X : BOOL;  // шаг S1 Idle активен
    Idle_T : TIME;  // шаг S1: время активности (последней)
    Idle_Start : TIME;  // шаг S1: момент активации
    Drain_X : BOOL;  // шаг S2 Drain активен
    Drain_T : TIME;  // шаг S2: время активности (последней)
    Drain_Start : TIME;  // шаг S2: момент активации
    Drain_SvErr : BOOL;  // шаг S2: ошибка контроля
    Air_X : BOOL;  // шаг S3 Air активен
    Air_T : TIME;  // шаг S3: время активности (последней)
    Air_Start : TIME;  // шаг S3: момент активации
    Rinse_X : BOOL;  // шаг S4 Rinse активен
    Rinse_T : TIME;  // шаг S4: время активности (последней)
    Rinse_Start : TIME;  // шаг S4: момент активации
    QuickRinse_X : BOOL;  // шаг S5 QuickRinse активен
    QuickRinse_T : TIME;  // шаг S5: время активности (последней)
    QuickRinse_Start : TIME;  // шаг S5: момент активации
    Refill_X : BOOL;  // шаг S6 Refill активен
    Refill_T : TIME;  // шаг S6: время активности (последней)
    Refill_Start : TIME;  // шаг S6: момент активации
END_VAR
