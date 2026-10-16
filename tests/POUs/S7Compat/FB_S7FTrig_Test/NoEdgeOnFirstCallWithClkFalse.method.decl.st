// семантика S7: на первом вызове с CLK = FALSE спада нет.
METHOD PRIVATE NoEdgeOnFirstCallWithClkFalse
VAR
    fbDut : FB_S7FTrig;     // проверяемый детектор (новый экземпляр на каждый вызов метода)
END_VAR
