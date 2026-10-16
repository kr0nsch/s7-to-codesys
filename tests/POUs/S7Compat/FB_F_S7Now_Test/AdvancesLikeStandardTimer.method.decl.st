// xSimulation = FALSE: F_S7Now() идёт как время ПЛК — прирост за ~300 мс совпадает с ET
// Standard.TON, запущенного в том же вызове (допуск T_RT_TOL). Тест идёт несколько циклов.
METHOD PRIVATE AdvancesLikeStandardTimer
