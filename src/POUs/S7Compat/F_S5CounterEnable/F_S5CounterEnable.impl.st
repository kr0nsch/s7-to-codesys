IF xRlo AND NOT stCounter.xRloFree THEN
    stCounter.xRloUp := FALSE;
    stCounter.xRloDown := FALSE;
    stCounter.xRloSet := FALSE;
END_IF
stCounter.xRloFree := xRlo;
F_S5CounterEnable := stCounter.iValue;
