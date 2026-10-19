// CTUD: RESET и LOAD одновременно — RESET главнее (CV = 0); QU = CV >= PV, QD = (CV = 0).
METHOD PRIVATE CtudResetBeatsLoad
VAR
    fbDut : CTUD;   // проверяемый счётчик (новый экземпляр на каждый вызов метода)
END_VAR
