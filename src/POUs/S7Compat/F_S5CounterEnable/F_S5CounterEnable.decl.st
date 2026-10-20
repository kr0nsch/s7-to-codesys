// Назначение: FR C n — разрешение счётчика S5: фронт RLO 0 → 1 сбрасывает память фронтов CU, CD и S, и
//             следующая из этих инструкций с RLO = 1 срабатывает снова (AWL_e.pdf, гл. 4). Возвращает
//             значение счётчика.
// Автор:      kr0nsch
// Версия:     1.2.0
// Документ:   docs/MAPPING_STL.md, правило s5.counter
FUNCTION F_S5CounterEnable : INT
VAR_IN_OUT
    stCounter : ST_S5Counter;   // счётчик (GVL_S5Counters.aCounter[n])
END_VAR
VAR_INPUT
    xRlo : BOOL;                // RLO перед инструкцией
END_VAR
