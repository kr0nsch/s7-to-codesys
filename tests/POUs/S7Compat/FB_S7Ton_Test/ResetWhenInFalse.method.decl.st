// IN = FALSE сбрасывает Q и ET; новый фронт — отсчёт заново.
METHOD PRIVATE ResetWhenInFalse
VAR
    fbDut : FB_S7Ton;       // проверяемый таймер (новый экземпляр на каждый вызов метода)
END_VAR
