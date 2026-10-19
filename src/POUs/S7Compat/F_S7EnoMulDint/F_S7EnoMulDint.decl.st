// Назначение: ENO инструкции S7 MUL (DInt) для кода, сконвертированного s7conv из LAD/FBD:
//             TRUE, если произведение помещается в DINT (-2147483648…2147483647), FALSE при
//             переполнении. У S7 ENO = EN AND NOT переполнение (справочник LAD S7-300/400, прил. C.1),
//             в CODESYS ENO = EN. Результат операции вычисляет вызывающий код; функцию вызывают до записи
//             результата.
// Автор:      kr0nsch
// Версия:     1.1.0
// Документ:   docs/MAPPING_LADFBD.md, правило lad.eno_error
FUNCTION F_S7EnoMulDint : BOOL
VAR_INPUT
    diIn1 : DINT;    // первый множитель (IN1)
    diIn2 : DINT;    // второй множитель (IN2)
END_VAR
VAR
    liResult : LINT;  // точный результат в LINT
END_VAR
VAR CONSTANT
    DINT_MIN : LINT := -2147483648;   // нижняя граница DINT
    DINT_MAX : LINT := 2147483647;   // верхняя граница DINT
END_VAR
