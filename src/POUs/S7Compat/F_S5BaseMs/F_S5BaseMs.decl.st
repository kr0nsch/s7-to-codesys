// Назначение: длительность единицы шкалы времени S5 в мс по коду шкалы (биты 12–13 слова S5TIME):
//             0 — 10 мс, 1 — 100 мс, 2 — 1 с, 3 — 10 с (AWL_e.pdf, §12.2).
// Автор:      kr0nsch
// Версия:     1.2.0
// Документ:   docs/MAPPING_STL.md, правило s5.timebase
FUNCTION F_S5BaseMs : UDINT
VAR_INPUT
    wBase : WORD;   // код шкалы 0…3
END_VAR
VAR CONSTANT
    BASE_100MS : WORD := 1;     // код шкалы 100 мс
    BASE_1S : WORD := 2;        // код шкалы 1 с
    MS_10 : UDINT := 10;        // 10 мс
    MS_100 : UDINT := 100;      // 100 мс
    MS_1000 : UDINT := 1000;    // 1 с
    MS_10000 : UDINT := 10000;  // 10 с
END_VAR
