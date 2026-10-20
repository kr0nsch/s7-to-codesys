// SS, S5T#1S: время истекает и при RLO = 0, Q = TRUE держится до R; после сброса — новый пуск фронтом.
METHOD PRIVATE RetOnDelayHoldsQUntilReset
VAR
    stTimer : ST_S5Timer;   // проверяемый таймер
    wPreset : WORD;         // S5T#1S
END_VAR
