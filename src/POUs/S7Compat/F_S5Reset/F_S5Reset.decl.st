// Назначение: R T n — сброс таймера S5: при RLO = 1 таймер останавливается, Q = FALSE, остаток — 0. Сброс
//             действует по уровню: пока RLO = 1, таймер держится сброшенным, а после снятия сброса снова
//             запускается только фронтом пуска (как awlsim; справочник STL пишет «при переходе RLO 0 → 1»,
//             справочник LAD для S_ODT — «и при RLO = 1, если таймер не идёт»; docs/ASSUMPTIONS.md, запись L15).
// Автор:      kr0nsch
// Версия:     1.2.0
// Документ:   docs/MAPPING_STL.md, правило s5.timer
FUNCTION F_S5Reset : BOOL
VAR_IN_OUT
    stTimer : ST_S5Timer;   // таймер (GVL_S5Timers.aTimer[n])
END_VAR
VAR_INPUT
    xRlo : BOOL;            // RLO перед инструкцией
END_VAR
