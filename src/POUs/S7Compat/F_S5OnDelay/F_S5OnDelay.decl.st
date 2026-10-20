// Назначение: SD T n — таймер S5 «задержка включения» (S_ODT). Фронт RLO 0 → 1 запускает таймер; Q = TRUE,
//             когда время истекло, а RLO всё ещё 1; RLO = 0 останавливает таймер (Q = FALSE, остаток
//             сохраняется) (AWL_e.pdf §12.9, LAD §13.5). Пуск не меняет Q: после перезапуска через FR при
//             RLO = 1 Q остаётся прежним до истечения (как awlsim; docs/ASSUMPTIONS.md, запись L14).
//             Возвращает Q после инструкции.
// Автор:      kr0nsch
// Версия:     1.2.0
// Документ:   docs/MAPPING_STL.md, правило s5.timebase
FUNCTION F_S5OnDelay : BOOL
VAR_IN_OUT
    stTimer : ST_S5Timer;   // таймер (GVL_S5Timers.aTimer[n])
END_VAR
VAR_INPUT
    xRlo : BOOL;            // RLO перед инструкцией
    wS5Time : WORD;         // заданное время S5TIME (ACCU1-L)
END_VAR
