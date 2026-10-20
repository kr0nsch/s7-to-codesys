// Назначение: LC C n — значение счётчика S5 в BCD (три тетрады, 0…999).
// Автор:      kr0nsch
// Версия:     1.2.0
// Документ:   docs/MAPPING_STL.md, правило s5.counter
FUNCTION F_S5CounterBcd : WORD
VAR_INPUT
    stCounter : ST_S5Counter;   // счётчик (GVL_S5Counters.aCounter[n])
END_VAR
