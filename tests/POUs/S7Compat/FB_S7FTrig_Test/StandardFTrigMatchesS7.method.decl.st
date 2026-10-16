// Характеризация платформы: F_TRIG библиотеки Standard CODESYS на тех же входах, что и FB_S7FTrig
// (семантика S7): на первом вызове с CLK = FALSE спада нет, спад TRUE -> FALSE — ровно на одном вызове.
// Если тест упадёт на другой версии Standard, корпус собирают с --f-trig s7compat (docs/MAPPING.md, fb.f_trig).
METHOD PRIVATE StandardFTrigMatchesS7
VAR
    fbStandard : F_TRIG;    // F_TRIG библиотеки Standard (новый экземпляр на каждый вызов метода)
    fbCompat : FB_S7FTrig;  // эталон семантики S7
END_VAR
