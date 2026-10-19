// Назначение: ENO инструкции S7 ADD (Int) для кода, сконвертированного s7conv из LAD/FBD:
//             TRUE, если сумма помещается в INT (-32768…32767), FALSE при переполнении. У S7 ENO = EN AND NOT
//             переполнение (справочник LAD S7-300/400, прил. C.1), в CODESYS ENO = EN. Результат операции
//             вычисляет вызывающий код; функцию вызывают до записи результата.
// Автор:      kr0nsch
// Версия:     1.1.0
// Документ:   docs/MAPPING_LADFBD.md, правило lad.eno_error
FUNCTION F_S7EnoAddInt : BOOL
VAR_INPUT
    iIn1 : INT;    // первое слагаемое (IN1)
    iIn2 : INT;    // второе слагаемое (IN2)
END_VAR
VAR
    diResult : DINT;  // точный результат в DINT
END_VAR
VAR CONSTANT
    INT_MIN : DINT := -32768;   // нижняя граница INT
    INT_MAX : DINT := 32767;   // верхняя граница INT
END_VAR
