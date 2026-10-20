// SE, S5T#1S: Q держится после спада RLO; фронт на 600 мс перезапускает таймер — истечение на 1600 мс.
METHOD PRIVATE ExtPulseRunsOutAndRetriggers
VAR
    stTimer : ST_S5Timer;   // проверяемый таймер
    wPreset : WORD;         // S5T#1S
END_VAR
