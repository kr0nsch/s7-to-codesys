// Назначение: SP T n — таймер S5 «импульс» (S_PULSE). Фронт RLO 0 → 1 запускает таймер, Q = TRUE, пока
//             таймер идёт; RLO = 0 до истечения останавливает его (Q = FALSE, остаток сохраняется); по
//             истечении Q = FALSE (AWL_e.pdf §12.7, LAD §13.3). Фронт — по памяти таймера xRloStart, её
//             сбрасывает FR. Возвращает Q после инструкции.
// Автор:      kr0nsch
// Версия:     1.2.0
// Документ:   docs/MAPPING_STL.md, правило s5.timebase
FUNCTION F_S5Pulse : BOOL
VAR_IN_OUT
    stTimer : ST_S5Timer;   // таймер (GVL_S5Timers.aTimer[n])
END_VAR
VAR_INPUT
    xRlo : BOOL;            // RLO перед инструкцией
    wS5Time : WORD;         // заданное время S5TIME (ACCU1-L)
END_VAR
