// Точный результат в LINT сравнивается с диапазоном DINT: вне диапазона S7 ставит OV и ENO = FALSE.
liResult := DINT_TO_LINT(diIn1) - DINT_TO_LINT(diIn2);
F_S7EnoSubDint := liResult >= DINT_MIN AND liResult <= DINT_MAX;
