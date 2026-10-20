// SF, S5T#1S: Q = TRUE при RLO = 1 и 1000 мс после спада; фронт RLO останавливает идущий таймер (остаток
// 50 единиц), следующий спад запускает его заново.
METHOD PRIVATE OffDelayHoldsAfterFall
VAR
    stTimer : ST_S5Timer;   // проверяемый таймер
    wPreset : WORD;         // S5T#1S
END_VAR
