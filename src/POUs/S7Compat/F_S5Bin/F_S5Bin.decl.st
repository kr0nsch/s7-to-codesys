// Назначение: L T n — остаток таймера S5 двоичным числом в единицах его шкалы, без шкалы (AWL_e.pdf §12.4).
//             Число единиц округляется вверх: значение падает на 1 через каждую единицу шкалы после пуска и
//             становится 0 в момент истечения (фаза часового процесса CPU не моделируется;
//             docs/ASSUMPTIONS.md, запись L13).
// Автор:      kr0nsch
// Версия:     1.2.0
// Документ:   docs/MAPPING_STL.md, правило s5.timer
FUNCTION F_S5Bin : WORD
VAR_IN_OUT
    stTimer : ST_S5Timer;   // таймер (GVL_S5Timers.aTimer[n])
END_VAR
VAR
    udiRest : UDINT;        // остаток, мс
    udiBase : UDINT;        // единица шкалы, мс
END_VAR
