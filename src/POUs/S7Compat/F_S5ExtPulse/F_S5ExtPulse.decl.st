// Назначение: SE T n — таймер S5 «продлённый импульс» (S_PEXT). Фронт RLO 0 → 1 запускает таймер (идущий —
//             перезапускает), Q = TRUE, пока таймер идёт, независимо от RLO; по истечении Q = FALSE
//             (AWL_e.pdf §12.8, LAD §13.4). Возвращает Q после инструкции.
// Автор:      kr0nsch
// Версия:     1.2.0
// Документ:   docs/MAPPING_STL.md, правило s5.timebase
FUNCTION F_S5ExtPulse : BOOL
VAR_IN_OUT
    stTimer : ST_S5Timer;   // таймер (GVL_S5Timers.aTimer[n])
END_VAR
VAR_INPUT
    xRlo : BOOL;            // RLO перед инструкцией
    wS5Time : WORD;         // заданное время S5TIME (ACCU1-L)
END_VAR
