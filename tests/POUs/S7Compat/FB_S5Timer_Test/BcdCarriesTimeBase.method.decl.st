// SD, S5T#20S: шкала 100 мс, 200 единиц; LC T — BCD со шкалой (16#1200, через 5 с — 16#1150); L T
// округляет остаток вверх (через 5050 мс — 150 единиц).
METHOD PRIVATE BcdCarriesTimeBase
VAR
    stTimer : ST_S5Timer;   // проверяемый таймер
    wPreset : WORD;         // S5T#20S
END_VAR
