// Назначение: слова таймеров S5 из STL (в S7 — глобальные объекты CPU, индекс — номер): T1, T2, T3, T4, T5
// Автор:      s7conv 0.1.0 (сгенерировано)
// Версия:     не указана
// Документ:   docs/MAPPING_STL.md, правила s5.timebase, s5.timer, s5.counter
{attribute 'qualified_only'}
VAR_GLOBAL
    aTimer : ARRAY[0..5] OF ST_S5Timer;  // используются: T1, T2, T3, T4, T5
END_VAR
