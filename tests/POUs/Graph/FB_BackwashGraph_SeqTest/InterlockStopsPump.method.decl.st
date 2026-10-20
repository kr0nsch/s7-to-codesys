// Блокировка шага Rinse (NC): при неисправном насосе (xPumpOk = FALSE) насос промывки выключен, воздуходувка
// параллельного шага работает; насос исправен — снова включён.
METHOD PRIVATE InterlockStopsPump
VAR
    fbDut : FB_BackwashGraph;   // проверяемый блок
    iCycle : INT;               // вызов внутри шага теста
END_VAR
