// CTD: LOAD по уровню ставит CV := PV, фронт CD уменьшает CV, но не ниже 0; Q = (CV = 0).
METHOD PRIVATE CtdStopsAtZero
VAR
    fbDut : CTD;    // проверяемый счётчик (новый экземпляр на каждый вызов метода)
END_VAR
