// CU считает только фронты RLO; после установки 999 фронт CU значение не меняет.
METHOD PRIVATE CountUpOnEdgeUpTo999
VAR
    stCounter : ST_S5Counter;   // проверяемый счётчик (новый на каждый вызов метода)
END_VAR
