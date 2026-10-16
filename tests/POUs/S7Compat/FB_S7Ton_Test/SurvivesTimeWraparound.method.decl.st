// переход TIME через 2^32 мс (около 49,7 суток): разность моментов — по модулю 2^32.
METHOD PRIVATE SurvivesTimeWraparound
VAR
    fbDut : FB_S7Ton;       // проверяемый таймер (новый экземпляр на каждый вызов метода)
END_VAR
