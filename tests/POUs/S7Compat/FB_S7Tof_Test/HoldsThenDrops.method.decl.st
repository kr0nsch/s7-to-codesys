// спад IN на 100 мс, PT = 1 с: Q = TRUE до 1099 мс, FALSE ровно на 1100 мс; ET растёт до PT и стоит.
METHOD PRIVATE HoldsThenDrops
VAR
    fbDut : FB_S7Tof;       // проверяемый таймер (новый экземпляр на каждый вызов метода)
END_VAR
