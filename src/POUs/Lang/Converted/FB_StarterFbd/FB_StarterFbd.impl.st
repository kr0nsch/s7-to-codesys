// Сеть 1: Пуск/стоп: SR, сброс главнее
// SR с битом #xRunMem: порядок S7 — сброс главнее
// MIGRATION-CHECK: элемент «SR»: имя и пины в SimaticML не подтверждены открытым экспортом (docs/MAPPING_LADFBD.md,
//                  уровень L) (FB_StarterFbd.xml, сеть 1, UId 28)
IF xStart AND xInterlock THEN
    xRunMem := TRUE;
END_IF
IF xStop OR NOT xInterlock OR xFault THEN
    xRunMem := FALSE;
END_IF
xRun := xRunMem;
// Сеть 2: Контроль обратной связи
tonFeedback(IN := xRun AND NOT xFeedback, PT := tFeedbackTime);
// Сеть 3: Авария с самоподхватом
xFault := (tonFeedback.Q OR xFault) AND NOT xReset;
// Сеть 4: Счётчик пусков по фронту xRun
xNet4_1 := xRun AND NOT xEdgeMem;
xEdgeMem := xRun;
IF xNet4_1 THEN
    iStarts := iStarts + 1;
END_IF
