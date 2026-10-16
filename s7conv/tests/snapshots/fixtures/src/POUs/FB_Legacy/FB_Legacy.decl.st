// Назначение: Функциональный блок «FB_Legacy», сконвертирован из SCL
// Автор:      не указан (исходный блок S7); перевод в ST — s7conv 0.1.0
// Версия:     0.1 (исходный блок S7)
// Документ:   docs/CONVERSION_REPORT.md, docs/MAPPING.md
// Источник:   s7conv/tests/fixtures/unsupported.scl, строки 2–44, FUNCTION_BLOCK "FB_Legacy"
// Сгенерировано s7conv: пометки MIGRATION-CHECK и MIGRATION-TODO требуют ручного разбора.
// MIGRATION-CHECK: стандартный (неоптимизированный) доступ S7: абсолютная адресация и порядок байтов не переносятся
//                  (стр. 2)
// MIGRATION-CHECK: реманентность задаётся в экземпляре DB (DB_SPECIFIC) — объявлено VAR (стр. 19)
// ---- комментарий в начале исходного файла SCL ----
// Фикстура s7conv: конструкции, которые конвертер не переводит или переводит с пометкой.
FUNCTION_BLOCK FB_Legacy
VAR_INPUT
    // MIGRATION-TODO: Variant — нет аналога в CODESYS; переписать (ANY, POINTER или перегрузка) (стр. 6)
    // anyIn : Variant;
    // MIGRATION-TODO: DTL — структура S7 (YEAR, MONTH, ...), в CODESYS нет; заменить на DT или свою структуру (стр.
    //                 7)
    // stamp : DTL;
    // MIGRATION-CHECK: имя «time» переименовано в «time_» (ключевое слово CODESYS или повтор) (стр. 8)
    time_ : TIME;
END_VAR
VAR
    raw : WORD;
    // MIGRATION-TODO: AT (наложение переменных S7) — переписать через UNION или битовый доступ (стр. 12)
    // bits AT raw : Array[0..15] of Bool;
    // MIGRATION-CHECK: счётчик S7 → CTU (CODESYS Standard): PV и CV — WORD (0…65535), в S7 — тип счётчика;
    //                  проверить диапазон (стр. 13)
    counter : CTU;
    txt : WSTRING(10);
    // MIGRATION-CHECK: Char → STRING(1): в CODESYS нет типа CHAR, сравнения и CHAR_TO_* проверить (стр. 15)
    ch : STRING(1);
    flags : BYTE;
    // MIGRATION-TODO: TONR (таймер с накоплением) — в CODESYS Standard нет (стр. 17)
    // acc : TONR_TIME;
END_VAR
VAR
    keep : INT;
END_VAR
