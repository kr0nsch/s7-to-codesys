// CD уменьшает значение по фронту, но не ниже 0; A C = (значение <> 0).
METHOD PRIVATE CountDownStopsAtZero
VAR
    stCounter : ST_S5Counter;   // проверяемый счётчик
END_VAR
