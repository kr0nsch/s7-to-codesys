// TRUE -> FALSE: Q = TRUE ровно на одном вызове.
METHOD PRIVATE FallingEdgeOnce
VAR
    fbDut : FB_S7FTrig;     // проверяемый детектор (новый экземпляр на каждый вызов метода)
END_VAR
