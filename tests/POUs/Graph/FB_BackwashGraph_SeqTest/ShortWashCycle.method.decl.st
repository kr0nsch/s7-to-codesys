// Короткая промывка целиком: Idle → Drain (S1: промывка №1) → QuickRinse → Refill → Idle.
METHOD PRIVATE ShortWashCycle
VAR
    fbDut : FB_BackwashGraph;   // проверяемый блок (новый экземпляр на каждый вызов метода)
    iCycle : INT;               // вызов внутри шага теста
END_VAR
