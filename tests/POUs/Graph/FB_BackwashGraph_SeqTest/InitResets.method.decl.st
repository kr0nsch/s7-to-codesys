// INIT_SQ возвращает начальный шаг (действия Drain выключены) и держит его; после снятия — новый пуск,
// промывка №2 (событие S1 — один раз).
METHOD PRIVATE InitResets
VAR
    fbDut : FB_BackwashGraph;   // проверяемый блок
    iCycle : INT;               // вызов внутри шага теста
END_VAR
