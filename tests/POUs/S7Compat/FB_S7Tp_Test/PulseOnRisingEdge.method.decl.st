// фронт IN на 0 мс, PT = 1 с: Q = TRUE до 999 мс, FALSE на 1000 мс; ET = PT, пока IN = TRUE; 0 при IN = FALSE.
METHOD PRIVATE PulseOnRisingEdge
VAR
    fbDut : FB_S7Tp;       // проверяемый таймер (новый экземпляр на каждый вызов метода)
END_VAR
