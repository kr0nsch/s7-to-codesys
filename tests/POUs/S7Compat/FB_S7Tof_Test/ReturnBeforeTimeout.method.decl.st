// IN вернулся раньше PT: Q не падал, ET = 0; следующий спад — отсчёт заново.
METHOD PRIVATE ReturnBeforeTimeout
VAR
    fbDut : FB_S7Tof;       // проверяемый таймер (новый экземпляр на каждый вызов метода)
END_VAR
