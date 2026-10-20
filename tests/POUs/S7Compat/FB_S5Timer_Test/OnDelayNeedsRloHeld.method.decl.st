// SD, S5T#1S: Q = TRUE ровно через 1000 мс при RLO = 1; RLO = 0 сбрасывает Q и останавливает таймер с
// остатком (70 единиц через 300 мс после повторного пуска) — и через 1 с остаток тот же, Q = FALSE.
METHOD PRIVATE OnDelayNeedsRloHeld
VAR
    stTimer : ST_S5Timer;   // проверяемый таймер
    wPreset : WORD;         // S5T#1S
END_VAR
