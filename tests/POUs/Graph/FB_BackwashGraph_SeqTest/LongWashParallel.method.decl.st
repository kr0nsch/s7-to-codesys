// Длинная промывка: после слива параллельно Air (воздуходувка) и Rinse (насос); задвижка воздуха (D 2 с) без
// времени закрыта.
METHOD PRIVATE LongWashParallel
VAR
    fbDut : FB_BackwashGraph;   // проверяемый блок
    iCycle : INT;               // вызов внутри шага теста
END_VAR
