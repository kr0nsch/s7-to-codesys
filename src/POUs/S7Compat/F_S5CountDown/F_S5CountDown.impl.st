IF xRlo AND NOT stCounter.xRloDown AND stCounter.iValue > 0 THEN
    stCounter.iValue := stCounter.iValue - 1;
END_IF
stCounter.xRloDown := xRlo;
F_S5CountDown := stCounter.iValue;
