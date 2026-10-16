// IN = TRUE с t = 1000 мс, PT = 2 с: Q = FALSE до 2999 мс, TRUE ровно на 3000 мс; ET растёт до PT и стоит.
METHOD PRIVATE CountsFromRisingEdge
VAR
    fbDut : FB_S7Ton;       // проверяемый таймер (новый экземпляр на каждый вызов метода)
END_VAR
