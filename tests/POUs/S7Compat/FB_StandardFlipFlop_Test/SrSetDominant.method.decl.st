// SR Standard: при SET1 = RESET = TRUE выход Q1 = TRUE (установка главнее); вход SET1 сброшен — Q1 держится.
METHOD PRIVATE SrSetDominant
VAR
    fbDut : SR;     // проверяемый элемент (новый экземпляр на каждый вызов метода)
END_VAR
