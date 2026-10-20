// Назначение: R C n — сброс счётчика S5 по уровню: при RLO = 1 значение := 0 (AWL_e.pdf, гл. 4). Память
//             фронтов CU, CD и S не меняется. Возвращает значение после инструкции.
// Автор:      kr0nsch
// Версия:     1.2.0
// Документ:   docs/MAPPING_STL.md, правило s5.counter
FUNCTION F_S5CounterReset : INT
VAR_IN_OUT
    stCounter : ST_S5Counter;   // счётчик (GVL_S5Counters.aCounter[n])
END_VAR
VAR_INPUT
    xRlo : BOOL;                // RLO перед инструкцией
END_VAR
