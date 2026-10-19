// CTU: CV растёт только по фронту CU, Q = CV >= PV, RESET по уровню обнуляет CV.
METHOD PRIVATE CtuCountsRisingEdges
VAR
    fbDut : CTU;    // проверяемый счётчик (новый экземпляр на каждый вызов метода)
END_VAR
