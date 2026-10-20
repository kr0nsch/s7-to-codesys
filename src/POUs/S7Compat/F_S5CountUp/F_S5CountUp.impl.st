IF xRlo AND NOT stCounter.xRloUp AND stCounter.iValue < MAX_VALUE THEN
    stCounter.iValue := stCounter.iValue + 1;
END_IF
stCounter.xRloUp := xRlo;
F_S5CountUp := stCounter.iValue;
