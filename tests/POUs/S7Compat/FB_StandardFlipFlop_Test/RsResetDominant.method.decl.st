// RS Standard: при SET = RESET1 = TRUE выход Q1 = FALSE (сброс главнее).
METHOD PRIVATE RsResetDominant
VAR
    fbDut : RS;     // проверяемый элемент (новый экземпляр на каждый вызов метода)
END_VAR
