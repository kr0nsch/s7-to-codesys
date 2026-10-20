// Назначение: LC T n — остаток таймера S5 в BCD со шкалой: биты 0–11 — значение (как F_S5Bin) в BCD, биты
//             12–13 — код шкалы последнего пуска (AWL_e.pdf §12.5).
// Автор:      kr0nsch
// Версия:     1.2.0
// Документ:   docs/MAPPING_STL.md, правило s5.timer
FUNCTION F_S5Bcd : WORD
VAR_IN_OUT
    stTimer : ST_S5Timer;   // таймер (GVL_S5Timers.aTimer[n])
END_VAR
VAR
    iUnits : INT;           // остаток в единицах шкалы
END_VAR
VAR CONSTANT
    BASE_SHIFT : INT := 12; // сдвиг кода шкалы
END_VAR
