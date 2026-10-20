// Назначение: Пускатель насоса (LAD)
//             Пускатель насоса с контролем обратной связи (один блок на LAD, FBD, STL, SCL).
//             1. Пуск/стоп — SR с битом-операндом xRunMem: S = xStart AND xInterlock; R1 = xStop OR NOT xInterlock
//             OR xFault.
//             SR S7: сначала S, затем R1 — при S = R1 = 1 (Пуск и Стоп одновременно) бит сброшен. xRun := xRunMem.
//             2. Контроль обратной связи: TON tonFeedback (IN = xRun AND NOT xFeedback, PT = tFeedbackTime).
//             3. Авария с самоподхватом: xFault := (tonFeedback.Q OR xFault) AND NOT xReset.
//             4. Счётчик пусков: по фронту xRun (бит памяти xEdgeMem) iStarts := iStarts + 1.
//             Порядок сетей 1-4; xFault в сети 1 — значение прошлого вызова.
// Автор:      WTP2 (исходный блок S7); перевод в ST — s7conv 0.1.0
// Версия:     0.1 (исходный блок S7)
// Документ:   docs/CONVERSION_REPORT.md, docs/MAPPING.md
// Источник:   samples/lang/FB_StarterLad.xml, LAD, SW.Blocks.FB "FB_StarterLad", пространство имён Interface/v5,
//             FAMILY Drives
// Сгенерировано s7conv: пометки MIGRATION-CHECK и MIGRATION-TODO требуют ручного разбора.
FUNCTION_BLOCK FB_StarterLad
VAR_INPUT
    xStart : BOOL;  // Пуск (кнопка)
    xStop : BOOL;  // Стоп (кнопка, TRUE — нажата)
    xInterlock : BOOL := TRUE;  // Блокировки в норме, пуск разрешён
    xFeedback : BOOL;  // Обратная связь контактора
    tFeedbackTime : TIME := T#2S;  // Допустимое время без обратной связи
    xReset : BOOL;  // Сброс аварии
END_VAR
VAR_OUTPUT
    xRun : BOOL;  // Команда контактору
    xFault : BOOL;  // Авария: нет обратной связи
    iStarts : INT;  // Число пусков
END_VAR
VAR
    xRunMem : BOOL;  // Бит-операнд SR пуска
    xEdgeMem : BOOL;  // Бит памяти фронта xRun
    tonFeedback : FB_S7Ton;  // Таймер контроля обратной связи
END_VAR
VAR_TEMP
    xNet4_1 : BOOL;  // сеть 4: PBox (UId 23)
END_VAR
