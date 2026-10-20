// SP, S5T#1S (шкала 10 мс): Q, пока таймер идёт и RLO = 1; по истечении Q = FALSE без перезапуска; RLO = 0
// останавливает таймер, остаток сохраняется (90 единиц через 100 мс после пуска).
METHOD PRIVATE PulseStopsWhenRloFalls
VAR
    stTimer : ST_S5Timer;   // проверяемый таймер (новый на каждый вызов метода)
    wPreset : WORD;         // S5T#1S
END_VAR
