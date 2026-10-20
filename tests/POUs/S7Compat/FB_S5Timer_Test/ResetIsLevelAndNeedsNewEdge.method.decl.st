// SD + R, S5T#1S: R при RLO = 1 держит таймер сброшенным; после снятия сброса без нового фронта пуска таймер
// не идёт (Q = FALSE и через 2 с), новый фронт запускает его.
METHOD PRIVATE ResetIsLevelAndNeedsNewEdge
VAR
    stTimer : ST_S5Timer;   // проверяемый таймер
    wPreset : WORD;         // S5T#1S
END_VAR
