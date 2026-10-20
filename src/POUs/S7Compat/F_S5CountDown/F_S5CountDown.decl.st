// Назначение: CD C n — счёт вниз счётчика S5: по фронту RLO 0 → 1 значение −1, не меньше 0 (AWL_e.pdf,
//             гл. 4). Возвращает значение после инструкции.
// Автор:      kr0nsch
// Версия:     1.2.0
// Документ:   docs/MAPPING_STL.md, правило s5.counter
FUNCTION F_S5CountDown : INT
VAR_IN_OUT
    stCounter : ST_S5Counter;   // счётчик (GVL_S5Counters.aCounter[n])
END_VAR
VAR_INPUT
    xRlo : BOOL;                // RLO перед инструкцией
END_VAR
