// FB_S7Ton и Standard.TON в реальном времени (xSimulation = FALSE): один IN, одни циклы. IN = TRUE 0–300 мс
// (дольше PT), FALSE 300–400 мс, TRUE 400–520 мс (короче PT), затем FALSE. Расхождение — цикл, где ET
// различаются больше допуска, или Q различается не на пороге PT (на пороге допустимо: TIME() двух таймеров может
// отличаться на 1 мс). Тест идёт около 700 мс.
METHOD PRIVATE MatchesStandardInRealTime
