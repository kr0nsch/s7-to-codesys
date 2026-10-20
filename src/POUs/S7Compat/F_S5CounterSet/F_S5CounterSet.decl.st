// Назначение: S C n — установка счётчика S5: по фронту RLO 0 → 1 значение := BCD из ACCU1-L (0…999)
//             (AWL_e.pdf, гл. 4). Возвращает значение после инструкции.
// Автор:      kr0nsch
// Версия:     1.2.0
// Документ:   docs/MAPPING_STL.md, правило s5.counter
FUNCTION F_S5CounterSet : INT
VAR_IN_OUT
    stCounter : ST_S5Counter;   // счётчик (GVL_S5Counters.aCounter[n])
END_VAR
VAR_INPUT
    xRlo : BOOL;                // RLO перед инструкцией
    wBcd : WORD;                // значение установки в BCD (ACCU1-L; литерал C#n)
END_VAR
