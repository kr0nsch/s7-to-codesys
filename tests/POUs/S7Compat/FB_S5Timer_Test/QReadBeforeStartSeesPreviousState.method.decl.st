// Опрос до инструкции пуска в том же цикле: SD, S5T#1S, на 1000 мс время истекло — чтение до SD видит
// Q = TRUE, SD с RLO = 0 сбрасывает Q, чтение после — FALSE. В S7 таймер обновляет часовой процесс CPU, и
// опрос из любого места программы видит одно и то же слово таймера (GVL_S5Timers — общий для всех блоков).
METHOD PRIVATE QReadBeforeStartSeesPreviousState
VAR
    stTimer : ST_S5Timer;   // проверяемый таймер
    wPreset : WORD;         // S5T#1S
END_VAR
