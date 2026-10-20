// Контроль шага Drain: неисправность задвижки защёлкивает ошибку (ERR_FLT), переход заблокирован и после
// ухода неисправности; квитирование ACK_EF снимает ошибку, и переход проходит.
METHOD PRIVATE SupervisionHoldsUntilAck
VAR
    fbDut : FB_BackwashGraph;   // проверяемый блок
    iCycle : INT;               // вызов внутри шага теста
END_VAR
