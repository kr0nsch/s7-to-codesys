IF NOT xS7convStartupDone THEN
    xS7convStartupDone := TRUE;
    DB_Hmi.counter := 0;
    DB_Hmi.ackRequest := FALSE;
END_IF
