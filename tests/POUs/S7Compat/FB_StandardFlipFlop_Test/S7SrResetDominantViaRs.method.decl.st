// S7 SR (S, R1): «сначала S, потом R» — при S = R1 = 1 выход сброшен. Перевод s7conv: CODESYS RS
// (SET := S, RESET1 := R1, Q1 — выход Q).
METHOD PRIVATE S7SrResetDominantViaRs
VAR
    fbDut : RS;     // перевод экземпляра S7 SR (новый экземпляр на каждый вызов метода)
END_VAR
