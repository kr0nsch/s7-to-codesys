// FB_S7Tof и Standard.TOF в реальном времени (xSimulation = FALSE): один IN, одни циклы. IN = TRUE 0–100 мс,
// FALSE 100–400 мс (дольше PT), TRUE 400–450 мс, FALSE 450–550 мс (короче PT), TRUE 550–600 мс, затем FALSE.
// Расхождение — цикл, где ET различаются больше допуска, или Q различается не на пороге PT (на пороге допустимо:
// TIME() двух таймеров может отличаться на 1 мс). Тест идёт около 700 мс.
METHOD PRIVATE MatchesStandardInRealTime
