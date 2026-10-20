// Назначение: три тетрады BCD из значения 0…999 (LC T n без шкалы, LC C n). Тысячи отбрасываются: значения
//             таймера и счётчика S5 не больше 999.
// Автор:      kr0nsch
// Версия:     1.2.0
// Документ:   docs/MAPPING_STL.md, правила s5.timer и s5.counter
FUNCTION F_S5ToBcd : WORD
VAR_INPUT
    iValue : INT;   // значение 0…999
END_VAR
VAR
    wUnits : WORD;      // тетрада единиц
    wTens : WORD;       // тетрада десятков
    wHundreds : WORD;   // тетрада сотен
END_VAR
VAR CONSTANT
    TEN : INT := 10;            // основание
    HUNDRED : INT := 100;       // вес сотен
    TENS_SHIFT : INT := 4;      // сдвиг тетрады десятков
    HUNDREDS_SHIFT : INT := 8;  // сдвиг тетрады сотен
END_VAR
