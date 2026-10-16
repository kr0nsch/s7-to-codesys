// PT = 0: Q = TRUE уже на вызове с фронтом IN (прошло 0 >= 0).
METHOD PRIVATE ZeroPtSwitchesImmediately
VAR
    fbDut : FB_S7Ton;       // проверяемый таймер (новый экземпляр на каждый вызов метода)
END_VAR
