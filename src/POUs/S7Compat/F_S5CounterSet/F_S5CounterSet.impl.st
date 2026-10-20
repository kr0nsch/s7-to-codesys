IF xRlo AND NOT stCounter.xRloSet THEN
    stCounter.iValue := F_S5FromBcd(wBcd);
END_IF
stCounter.xRloSet := xRlo;
F_S5CounterSet := stCounter.iValue;
