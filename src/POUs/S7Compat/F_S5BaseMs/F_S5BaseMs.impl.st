IF wBase = 0 THEN
    F_S5BaseMs := MS_10;
ELSIF wBase = BASE_100MS THEN
    F_S5BaseMs := MS_100;
ELSIF wBase = BASE_1S THEN
    F_S5BaseMs := MS_1000;
ELSE
    F_S5BaseMs := MS_10000;
END_IF
