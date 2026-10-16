// до первого IN = TRUE выход FALSE: спада ещё не было.
METHOD PRIVATE NoOutputBeforeFirstTrue
VAR
    fbDut : FB_S7Tof;       // проверяемый таймер (новый экземпляр на каждый вызов метода)
END_VAR
