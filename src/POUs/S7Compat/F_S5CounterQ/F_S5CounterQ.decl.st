// Назначение: опрос A C n (AN, O, ON, X, XN) — состояние счётчика S5: TRUE, если значение не 0.
// Автор:      kr0nsch
// Версия:     1.2.0
// Документ:   docs/MAPPING_STL.md, правило s5.counter
FUNCTION F_S5CounterQ : BOOL
VAR_INPUT
    stCounter : ST_S5Counter;   // счётчик (GVL_S5Counters.aCounter[n])
END_VAR
