// REGION Edge detection
startEdge(CLK := cmd.start);
// END_REGION Edge detection

// REGION Mode handling
CASE cmd.mode OF
    0:
        // выведен из работы
        run := FALSE;
    1, 2:
        IF startEdge.Q AND NOT fault THEN
            run := TRUE;
            starts := starts + 1;
        ELSIF cmd.stop THEN
            run := FALSE;
        END_IF
ELSE
    run := FALSE;
END_CASE
// END_REGION Mode handling

// Контроль обратной связи
fbTimer(IN := run AND NOT feedback, PT := feedbackTime, ET => runTime);
IF fbTimer.Q THEN
    fault := TRUE;
    run := FALSE;
END_IF
IF ack THEN
    fault := FALSE;
    ack := FALSE;
END_IF

FOR i := 3 TO 1 BY -1 DO
    stat.history[i] := stat.history[i - 1];
END_FOR
stat.history[0] := run;
stat.lastMode := cmd.mode;
IF starts > MAX_STARTS THEN
    starts := 0;
END_IF
