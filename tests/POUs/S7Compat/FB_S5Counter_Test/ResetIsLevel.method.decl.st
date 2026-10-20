// R C при RLO = 1 обнуляет значение на каждом вызове (по уровню), память фронтов не трогает.
METHOD PRIVATE ResetIsLevel
VAR
    stCounter : ST_S5Counter;   // проверяемый счётчик
END_VAR
