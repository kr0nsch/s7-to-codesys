// Сеть 1: Значение по умолчанию
FC_ClampPctLad := iIn;
// Сеть 2: Выше максимума
IF iIn > iMax THEN
    FC_ClampPctLad := iMax;
END_IF
// Сеть 3: Ниже минимума
IF iIn < iMin THEN
    FC_ClampPctLad := iMin;
END_IF
