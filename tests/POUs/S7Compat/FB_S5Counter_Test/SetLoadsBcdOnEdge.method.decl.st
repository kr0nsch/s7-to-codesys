// S C загружает BCD из ACCU1-L только по фронту; L C — двоичное значение, LC C — BCD.
METHOD PRIVATE SetLoadsBcdOnEdge
VAR
    stCounter : ST_S5Counter;   // проверяемый счётчик
END_VAR
