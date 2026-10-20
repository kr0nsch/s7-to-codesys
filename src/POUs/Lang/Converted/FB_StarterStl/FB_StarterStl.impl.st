// Сеть 1: Пуск/стоп: SR, сброс главнее
IF xStart AND xInterlock THEN
    xRunMem := TRUE;
END_IF
IF xStop OR NOT xInterlock OR xFault THEN
    xRunMem := FALSE;
END_IF
xRun := xRunMem;
// Сеть 2: Контроль обратной связи
xTonIn := xRun AND NOT xFeedback;
tonFeedback(IN := xTonIn, PT := tFeedbackTime, Q => xTonQ);
// Сеть 3: Авария с самоподхватом
xFault := (xTonQ OR xFault) AND NOT xReset;
// Сеть 4: Счётчик пусков по фронту xRun
xEdge4_1 := xRun AND NOT xEdgeMem;
xEdgeMem := xRun;
IF xEdge4_1 THEN
    // JCN M001
    iStarts := iStarts + 1;
END_IF
