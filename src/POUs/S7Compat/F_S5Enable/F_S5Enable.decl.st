// Назначение: FR T n — разрешение таймера S5: фронт RLO 0 → 1 сбрасывает память фронта пуска, и следующая
//             инструкция пуска с RLO = 1 запускает таймер заново (перезапуск идущего таймера). Спад RLO
//             ничего не делает (AWL_e.pdf §12.3). Возвращает Q таймера.
// Автор:      kr0nsch
// Версия:     1.2.0
// Документ:   docs/MAPPING_STL.md, правило s5.timer
FUNCTION F_S5Enable : BOOL
VAR_IN_OUT
    stTimer : ST_S5Timer;   // таймер (GVL_S5Timers.aTimer[n])
END_VAR
VAR_INPUT
    xRlo : BOOL;            // RLO перед инструкцией
END_VAR
