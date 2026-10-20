// Сеть 1 (SCL): Пускатель
// 1. SR с битом xRunMem: сначала S, затем R1 (сброс главнее)
IF xStart AND xInterlock THEN
    xRunMem := TRUE;
END_IF
IF xStop OR NOT xInterlock OR xFault THEN
    xRunMem := FALSE;
END_IF
xRun := xRunMem;
// 2. Контроль обратной связи
tonFeedback(IN := xRun AND NOT xFeedback, PT := tFeedbackTime);
// 3. Авария с самоподхватом
xFault := (tonFeedback.Q OR xFault) AND NOT xReset;
// 4. Счётчик пусков по фронту xRun
IF xRun AND NOT xEdgeMem THEN
    iStarts := iStarts + 1;
END_IF
xEdgeMem := xRun;
