counter(CU := raw.0, RESET := raw.1, PV := 10);
IF counter.Q THEN
    // MIGRATION-TODO: GOTO — переходы не переносятся (переписать структурно) (стр. 26)
    // GOTO done;
    ; // нет операторов
END_IF
// MIGRATION-TODO: PEEK_WORD: нет прямого аналога в CODESYS Standard (стр. 28)
// #raw := PEEK_WORD(area := 16#84, dbNumber := 1, byteOffset := 0);
// MIGRATION-CHECK: срез .%B1 → WORD_TO_BYTE(SHR(...)): нумерация срезов S7 от младшей части — сверить с источником
//                  (стр. 29)
flags := WORD_TO_BYTE(SHR(raw, 8));
// MIGRATION-TODO: оператор не разобран: ожидалось ';', найдено 'ENO' (стр. 30)
// #keep := #keep + 1 ENO => #ok;
txt := "abc";
ch := 'A';
// MIGRATION-CHECK: ROUND → REAL_TO_DINT: правило округления половины (x.5) сверить с источником (стр. 33)
keep := REAL_TO_DINT(2.5) + TRUNC(1.5);
// MIGRATION-TODO: адрес %DB1.DBX0.0 не поддерживается (только %I, %Q, %M) (стр. 34)
// %DB1.DBX0.0 := TRUE;
// MIGRATION-CHECK: отрицательный TIME: в CODESYS TIME беззнаковый (UDINT мс) (стр. 35)
time_ := T#-5s;
raw := SHL(raw, 2) OR WORD#16#00FF;
keep := LIMIT(0, keep, 100);
keep := MAX(1, 2, 3);
// MIGRATION-CHECK: REAL_TO_DWORD: в S7-1200/1500 переносится битовый образ, в CODESYS — числовое значение (стр. 39)
raw := DWORD_TO_WORD(REAL_TO_DWORD(1.0));
// MIGRATION-CHECK: ** → EXPT: тип результата для целых операндов сверить (в S7 — REAL/LREAL) (стр. 40)
keep := EXPT(keep, 2);
// MIGRATION-TODO: метка перехода — переходы не переносятся (стр. 41)
// done:
keep := 0;
// MIGRATION-TODO: DB "Unknown_DB" не найден в корпусе — добавьте его исходник (стр. 42)
// "Unknown_DB".value := 1;
// MIGRATION-TODO: оператор не разобран: ожидалось выражение, найдено ':=' (стр. 43)
// #keep := := 2;
