// Назначение: SF T n — таймер S5 «задержка выключения» (S_OFFDT). Фронт RLO 0 → 1: Q = TRUE, идущий таймер
//             останавливается; спад RLO 1 → 0 запускает таймер, Q = TRUE, пока он идёт; по истечении
//             Q = FALSE (AWL_e.pdf §12.11, LAD §13.7). Возвращает Q после инструкции.
// Автор:      kr0nsch
// Версия:     1.2.0
// Документ:   docs/MAPPING_STL.md, правило s5.timebase
FUNCTION F_S5OffDelay : BOOL
VAR_IN_OUT
    stTimer : ST_S5Timer;   // таймер (GVL_S5Timers.aTimer[n])
END_VAR
VAR_INPUT
    xRlo : BOOL;            // RLO перед инструкцией
    wS5Time : WORD;         // заданное время S5TIME (ACCU1-L)
END_VAR
