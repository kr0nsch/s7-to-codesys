// Точный результат в DINT сравнивается с диапазоном INT: вне диапазона S7 ставит OV и ENO = FALSE.
diResult := INT_TO_DINT(iIn1) * INT_TO_DINT(iIn2);
F_S7EnoMulInt := diResult >= INT_MIN AND diResult <= INT_MAX;
