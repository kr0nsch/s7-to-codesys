// первый вызов экземпляра уже с IN = TRUE (t = 500 мс) — начало отсчёта.
METHOD PRIVATE FirstCallWithInTrueStarts
VAR
    fbDut : FB_S7Ton;       // проверяемый таймер (новый экземпляр на каждый вызов метода)
END_VAR
