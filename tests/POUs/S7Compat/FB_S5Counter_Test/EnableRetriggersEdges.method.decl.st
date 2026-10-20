// FR C по фронту сбрасывает память фронтов: CU при удерживаемом RLO = 1 срабатывает снова; спад FR и
// удержание FR = 1 ничего не дают.
METHOD PRIVATE EnableRetriggersEdges
VAR
    stCounter : ST_S5Counter;   // проверяемый счётчик
END_VAR
