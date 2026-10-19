// Справка Standard пишет о входах «Rising edge», модель stsim — по уровню (МЭК 61131-3). Тест различает:
// SET держится TRUE, RESET1 импульсом сбрасывает Q1; после снятия RESET1 по уровню Q1 снова TRUE,
// по фронту осталась бы FALSE.
METHOD PRIVATE RsSetHeldReappliesAfterReset
VAR
    fbDut : RS;     // проверяемый элемент (новый экземпляр на каждый вызов метода)
END_VAR
