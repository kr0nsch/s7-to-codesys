// Назначение: SS T n — таймер S5 «задержка включения с памятью» (S_ODTS). Фронт RLO 0 → 1 запускает таймер
//             (идущий — перезапускает), время истекает независимо от RLO; Q = TRUE по истечении и держится
//             до сброса R (AWL_e.pdf §12.10, LAD §13.6). Возвращает Q после инструкции.
// Автор:      kr0nsch
// Версия:     1.2.0
// Документ:   docs/MAPPING_STL.md, правило s5.timebase
FUNCTION F_S5RetOnDelay : BOOL
VAR_IN_OUT
    stTimer : ST_S5Timer;   // таймер (GVL_S5Timers.aTimer[n])
END_VAR
VAR_INPUT
    xRlo : BOOL;            // RLO перед инструкцией
    wS5Time : WORD;         // заданное время S5TIME (ACCU1-L)
END_VAR
