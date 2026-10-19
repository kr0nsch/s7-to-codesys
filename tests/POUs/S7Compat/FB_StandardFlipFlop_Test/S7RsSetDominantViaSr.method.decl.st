// S7 RS (R, S1): «сначала R, потом S» — при R = S1 = 1 выход установлен. Перевод s7conv: CODESYS SR
// (SET1 := S1, RESET := R, Q1 — выход Q).
METHOD PRIVATE S7RsSetDominantViaSr
VAR
    fbDut : SR;     // перевод экземпляра S7 RS (новый экземпляр на каждый вызов метода)
END_VAR
