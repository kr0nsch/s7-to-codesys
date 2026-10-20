// Назначение: опрос A T n (AN, O, ON, X, XN) — состояние таймера S5 на момент чтения: перед чтением таймер
//             пересчитывается на F_S7Now() (истечение времени видно и до следующей инструкции пуска).
// Автор:      kr0nsch
// Версия:     1.2.0
// Документ:   docs/MAPPING_STL.md, правило s5.timer
FUNCTION F_S5Q : BOOL
VAR_IN_OUT
    stTimer : ST_S5Timer;   // таймер (GVL_S5Timers.aTimer[n])
END_VAR
