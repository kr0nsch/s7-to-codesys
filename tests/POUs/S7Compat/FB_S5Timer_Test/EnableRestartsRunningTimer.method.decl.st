// FR + SE, S5T#1S: фронт FR при RLO пуска = 1 перезапускает идущий таймер; спад FR ничего не делает; новый
// фронт FR снова даёт пуск без фронта RLO пуска (AWL_e.pdf §12.3).
METHOD PRIVATE EnableRestartsRunningTimer
VAR
    stTimer : ST_S5Timer;   // проверяемый таймер
    wPreset : WORD;         // S5T#1S
END_VAR
