// Назначение: слова счётчиков S5 из STL (в S7 — глобальные объекты CPU, индекс — номер): C1
// Автор:      s7conv 0.1.0 (сгенерировано)
// Версия:     не указана
// Документ:   docs/MAPPING_STL.md, правила s5.timebase, s5.timer, s5.counter
{attribute 'qualified_only'}
VAR_GLOBAL
    aCounter : ARRAY[0..1] OF ST_S5Counter;  // используются: C1
END_VAR
