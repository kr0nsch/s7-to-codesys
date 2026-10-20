// Назначение: общая часть пуска таймера S5 (SP, SE, SD, SS, SF): шкала и заданное время из слова S5TIME
//             (ACCU1-L при пуске: значение BCD 0…999 и код шкалы, AWL_e.pdf §12.2), момент пуска —
//             F_S7Now(). Состояние Q и действие по истечении задаёт вызывающая функция пуска.
// Автор:      kr0nsch
// Версия:     1.2.0
// Документ:   docs/MAPPING_STL.md, правило s5.timebase
FUNCTION F_S5Start : BOOL
VAR_IN_OUT
    stTimer : ST_S5Timer;   // таймер
END_VAR
VAR_INPUT
    wS5Time : WORD;         // заданное время S5TIME (ACCU1-L)
END_VAR
VAR
    udiUnits : UDINT;       // значение в единицах шкалы
    udiBaseMs : UDINT;      // единица шкалы, мс
END_VAR
VAR CONSTANT
    BASE_SHIFT : INT := 12;     // биты 12–13 — код шкалы
    BASE_MASK : WORD := 16#3;   // маска кода шкалы
END_VAR
