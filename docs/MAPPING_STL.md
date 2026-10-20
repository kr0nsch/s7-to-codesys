# Соответствие STL → ST: все токены XSD V21

Сгенерирован `s7conv 0.1.0` из таблиц конвертера — не редактировать, пересоздаётся `s7conv build-corpus`.

Перечень — 172 значения `StlToken` из `SW.PlcBlocks.STL_v5.xsd` (TIA Portal V21; SHA-256 файла — в
`samples/lang/EXTERNAL.json`). Имя токена не зависит от мнемоники: XML даёт его напрямую, разборщик
AWL переводит мнемонику EN/DE в те же имена. Класс: **auto** — переводится без пометки; **check** —
с пометкой `MIGRATION-CHECK`; **todo** — в этом выпуске не переводится (`MIGRATION-TODO`, исходная
инструкция в комментарии); **impossible** — аналога в CODESYS нет.

Перевод — символьный подъём (режим A): RLO — выражение, /FC, OR-группы и скобки — состояние
транслятора, ACCU — типизированные выражения; переходы восстанавливаются в IF/ELSE (`structured`) или
автомат CASE (`pc`), `JMP` в ST не попадает. Правила с пометкой, которые возникают не из токена, а из
типов: `stl.zero_extend` (`L` WORD/INT → DINT дополняется нулями), `stl.accu_high` (старшая часть
ACCU1), `stl.bitcopy` (копия битов между INT/DINT и REAL), `stl.jump_pc` (автомат переходов).

Итог классификации: 172 из 172 токенов; auto — 73, check — 5, todo — 94, impossible — 0.

| Токен XSD | EN | DE | Класс | Правило | Что | Тесты |
|---|---|---|---|---|---|---|
| `A` | `A` | `U` | auto | `stl.logic` | AND с операндом | `test_stl_and_before_or_and_brackets`<br>`test_random_stl_chains_match_machine` |
| `A_BRACK` | `A(` | `U(` | auto | `stl.logic` | A( — скобка | `test_stl_and_before_or_and_brackets`<br>`test_random_stl_chains_match_machine` |
| `ABS_R` | `ABS` | `ABS` | todo | `stl.math` | ABS REAL | — |
| `ACOS` | `ACOS` | `ACOS` | todo | `stl.math` | ACOS REAL | — |
| `AD` | `AD` | `UD` | todo | `stl.word_logic` | AD — логика двойных слов | — |
| `ADD` | `+` | `+` | auto | `stl.math` | + константа к ACCU1 | `test_stl_load_transfer_and_int_arithmetic`<br>`test_stl_dint_real_arithmetic_and_compare` |
| `ADD_D` | `+D` | `+D` | auto | `stl.math` | +D | `test_stl_load_transfer_and_int_arithmetic`<br>`test_stl_dint_real_arithmetic_and_compare` |
| `ADD_I` | `+I` | `+I` | auto | `stl.math` | +I | `test_stl_load_transfer_and_int_arithmetic`<br>`test_stl_dint_real_arithmetic_and_compare` |
| `ADD_R` | `+R` | `+R` | auto | `stl.math` | +R | `test_stl_load_transfer_and_int_arithmetic`<br>`test_stl_dint_real_arithmetic_and_compare` |
| `ADDAR1` | `+AR1` | `+AR1` | todo | `stl.addr_register` | +AR1 | — |
| `ADDAR2` | `+AR2` | `+AR2` | todo | `stl.addr_register` | +AR2 | — |
| `AN` | `AN` | `UN` | auto | `stl.logic` | AND NOT | `test_stl_and_before_or_and_brackets`<br>`test_random_stl_chains_match_machine` |
| `AN_BRACK` | `AN(` | `UN(` | auto | `stl.logic` | AN( — скобка | `test_stl_and_before_or_and_brackets`<br>`test_random_stl_chains_match_machine` |
| `ASIN` | `ASIN` | `ASIN` | todo | `stl.math` | ASIN REAL | — |
| `Assign` | `=` | `=` | auto | `stl.logic` | присвоить RLO | `test_stl_and_before_or_and_brackets`<br>`test_random_stl_chains_match_machine` |
| `ATAN` | `ATAN` | `ATAN` | todo | `stl.math` | ATAN REAL | — |
| `AW` | `AW` | `UW` | todo | `stl.word_logic` | AW — логика слов | — |
| `BE` | `BE` | `BE` | auto | `stl.block_end` | конец блока | `test_stl_block_end_instructions` |
| `BEC` | `BEC` | `BEB` | auto | `stl.block_end` | условный конец блока | `test_stl_block_end_instructions` |
| `BEU` | `BEU` | `BEA` | auto | `stl.block_end` | безусловный конец блока | `test_stl_block_end_instructions` |
| `BLD` | `BLD` | `BLD` | auto | `stl.nop` | BLD — команда отображения, без действия | `test_language_corpus_suites_pass_in_simulation` |
| `BRACK_MCR` | `)MCR` | `)MCR` | todo | `stl.mcr` | )MCR — закрыть зону MCR | — |
| `BRACKET` | `)` | `)` | auto | `stl.logic` | ) — закрыть скобку | `test_stl_and_before_or_and_brackets`<br>`test_random_stl_chains_match_machine` |
| `BTD` | `BTD` | `BTD` | todo | `stl.convert` | BCD → DINT | — |
| `BTI` | `BTI` | `BTI` | todo | `stl.convert` | BCD → INT | — |
| `CAC` | `TAK` | `TAK` | todo | `stl.mode_b` | TAK — обмен ACCU1 и ACCU2 | — |
| `CAD` | `CAD` | `TAD` | todo | `stl.convert` | обмен байтов ACCU1 | — |
| `CALL` | `CALL` | `CALL` | auto | `stl.call` | CALL блока или инструкции (TON/TOF/TP ...) | `test_language_corpus_suites_pass_in_simulation`<br>`test_external_samples_convert_with_expected_outcome` |
| `CAR` | `CAR` | `TAR` | todo | `stl.addr_register` | обмен AR1 и AR2 | — |
| `CAW` | `CAW` | `TAW` | todo | `stl.convert` | обмен байтов ACCU1-L | — |
| `CC` | `CC` | `CC` | auto | `stl.call` | CC — условный вызов FC без параметров | `test_language_corpus_suites_pass_in_simulation`<br>`test_external_samples_convert_with_expected_outcome` |
| `CD` | `CD` | `ZR` | auto | `s5.counter` | CD — счёт вниз (F_S5CountDown) | `test_stl_s5_counters_lower_to_s7compat_calls`<br>`test_reference_s5_counter_matches_awlsim` |
| `CDB` | `CDB` | `TDB` | todo | `stl.db_register` | обмен регистров DB и DI | — |
| `CLR` | `CLR` | `CLR` | auto | `stl.logic` | RLO := 0 | `test_stl_and_before_or_and_brackets`<br>`test_random_stl_chains_match_machine` |
| `COMMENT` | `//` | `//` | auto | `stl.nop` | строка-комментарий | `test_language_corpus_suites_pass_in_simulation` |
| `COS` | `COS` | `COS` | todo | `stl.math` | COS REAL | — |
| `CU` | `CU` | `ZV` | auto | `s5.counter` | CU — счёт вверх (F_S5CountUp) | `test_stl_s5_counters_lower_to_s7compat_calls`<br>`test_reference_s5_counter_matches_awlsim` |
| `DEC` | `DEC` | `DEC` | todo | `stl.math` | DEC — ACCU1-L-L - n | — |
| `DIV_D` | `/D` | `/D` | auto | `stl.math` | /D | `test_stl_load_transfer_and_int_arithmetic`<br>`test_stl_dint_real_arithmetic_and_compare` |
| `DIV_I` | `/I` | `/I` | auto | `stl.math` | /I | `test_stl_load_transfer_and_int_arithmetic`<br>`test_stl_dint_real_arithmetic_and_compare` |
| `DIV_R` | `/R` | `/R` | auto | `stl.math` | /R | `test_stl_load_transfer_and_int_arithmetic`<br>`test_stl_dint_real_arithmetic_and_compare` |
| `DTB` | `DTB` | `DTB` | todo | `stl.convert` | DINT → BCD | — |
| `DTR` | `DTR` | `DTR` | todo | `stl.convert` | DINT → REAL | — |
| `EMPTY_LINE` | — | — | auto | `stl.nop` | пустая строка | `test_language_corpus_suites_pass_in_simulation` |
| `ENT` | `ENT` | `ENT` | todo | `stl.mode_b` | ENT (только 4 ACCU, S7-400) | — |
| `EQ_D` | `==D` | `==D` | auto | `stl.compare` | сравнение ==D | `test_stl_compare_is_first_check`<br>`test_stl_dint_real_arithmetic_and_compare` |
| `EQ_I` | `==I` | `==I` | auto | `stl.compare` | сравнение ==I | `test_stl_compare_is_first_check`<br>`test_stl_dint_real_arithmetic_and_compare` |
| `EQ_R` | `==R` | `==R` | auto | `stl.compare` | сравнение ==R | `test_stl_compare_is_first_check`<br>`test_stl_dint_real_arithmetic_and_compare` |
| `EXP` | `EXP` | `EXP` | todo | `stl.math` | EXP REAL | — |
| `Extend` | `SE` | `SV` | check | `s5.timebase` | SE — продлённый импульс (F_S5ExtPulse) | `test_stl_s5_timers_lower_to_s7compat_calls`<br>`test_stl_s5_all_start_kinds_and_word_preset`<br>`test_reference_s5_timer_matches_awlsim` |
| `Fall` | `FN` | `FN` | auto | `stl.edge` | FN: спад RLO, явный бит памяти | `test_stl_fp_jcn_label_becomes_if_without_jmp` |
| `Free` | `FR` | `FR` | auto | `s5.timer` | FR — разрешение таймера/счётчика (F_S5Enable, F_S5CounterEnable) | `test_stl_s5_timers_lower_to_s7compat_calls`<br>`test_stl_s5_read_before_write_is_frozen` |
| `GE_D` | `>=D` | `>=D` | auto | `stl.compare` | сравнение >=D | `test_stl_compare_is_first_check`<br>`test_stl_dint_real_arithmetic_and_compare` |
| `GE_I` | `>=I` | `>=I` | auto | `stl.compare` | сравнение >=I | `test_stl_compare_is_first_check`<br>`test_stl_dint_real_arithmetic_and_compare` |
| `GE_R` | `>=R` | `>=R` | auto | `stl.compare` | сравнение >=R | `test_stl_compare_is_first_check`<br>`test_stl_dint_real_arithmetic_and_compare` |
| `GT_D` | `>D` | `>D` | auto | `stl.compare` | сравнение >D | `test_stl_compare_is_first_check`<br>`test_stl_dint_real_arithmetic_and_compare` |
| `GT_I` | `>I` | `>I` | auto | `stl.compare` | сравнение >I | `test_stl_compare_is_first_check`<br>`test_stl_dint_real_arithmetic_and_compare` |
| `GT_R` | `>R` | `>R` | auto | `stl.compare` | сравнение >R | `test_stl_compare_is_first_check`<br>`test_stl_dint_real_arithmetic_and_compare` |
| `INC` | `INC` | `INC` | todo | `stl.math` | INC — ACCU1-L-L + n | — |
| `INV_D` | `INVD` | `KED` | todo | `stl.convert` | INVD — дополнение до единицы DINT | — |
| `INV_I` | `INVI` | `KEW` | todo | `stl.convert` | INVI — дополнение до единицы INT | — |
| `ITB` | `ITB` | `ITB` | todo | `stl.convert` | INT → BCD | — |
| `ITD` | `ITD` | `ITD` | todo | `stl.convert` | INT → DINT | — |
| `JBI` | `JBI` | `SPBI` | todo | `stl.mode_b` | переход при BR = 1 | — |
| `JC` | `JC` | `SPB` | auto | `stl.jump_structured` | переход при RLO = 1 | `test_stl_fp_jcn_label_becomes_if_without_jmp`<br>`test_stl_if_else_pattern` |
| `JCB` | `JCB` | `SPBB` | todo | `stl.mode_b` | переход при RLO = 1 с сохранением в BR | — |
| `JCN` | `JCN` | `SPBN` | auto | `stl.jump_structured` | переход при RLO = 0 | `test_stl_fp_jcn_label_becomes_if_without_jmp`<br>`test_stl_if_else_pattern` |
| `JL` | `JL` | `SPL` | todo | `stl.jump_list` | JL — список переходов | — |
| `JM` | `JM` | `SPM` | todo | `stl.mode_b` | переход при результате < 0 | — |
| `JMZ` | `JMZ` | `SPMZ` | todo | `stl.mode_b` | переход при результате <= 0 | — |
| `JN` | `JN` | `SPN` | todo | `stl.mode_b` | переход при результате <> 0 | — |
| `JNB` | `JNB` | `SPBNB` | todo | `stl.mode_b` | переход при RLO = 0 с сохранением в BR | — |
| `JNBI` | `JNBI` | `SPBIN` | todo | `stl.mode_b` | переход при BR = 0 | — |
| `JO` | `JO` | `SPO` | todo | `stl.mode_b` | переход при OV = 1 | — |
| `JOS` | `JOS` | `SPS` | todo | `stl.mode_b` | переход при OS = 1 | — |
| `JP` | `JP` | `SPP` | todo | `stl.mode_b` | переход при результате > 0 | — |
| `JPZ` | `JPZ` | `SPPZ` | todo | `stl.mode_b` | переход при результате >= 0 | — |
| `JU` | `JU` | `SPA` | auto | `stl.jump_structured` | безусловный переход | `test_stl_fp_jcn_label_becomes_if_without_jmp`<br>`test_stl_if_else_pattern` |
| `JUN` | `JUN` | `SPU` | todo | `stl.mode_b` | переход при неупорядоченном результате (REAL) | — |
| `JZ` | `JZ` | `SPZ` | todo | `stl.mode_b` | переход при результате = 0 | — |
| `L` | `L` | `L` | auto | `stl.accu` | загрузить в ACCU1 (L WORD/INT в DINT — с обнулением, stl.zero_extend) | `test_stl_load_transfer_and_int_arithmetic`<br>`test_zero_extension_mutation_is_caught` |
| `L_DBLG` | `L DBLG` | `L DBLG` | todo | `stl.db_register` | длина открытого DB | — |
| `L_DBNO` | `L DBNO` | `L DBNO` | todo | `stl.db_register` | номер открытого DB | — |
| `L_DILG` | `L DILG` | `L DILG` | todo | `stl.db_register` | длина открытого DI | — |
| `L_DINO` | `L DINO` | `L DINO` | todo | `stl.db_register` | номер открытого DI | — |
| `LAR1` | `LAR1` | `LAR1` | todo | `stl.addr_register` | загрузить AR1 | — |
| `LAR1_ACCU1` | `LAR1` | `LAR1` | todo | `stl.addr_register` | LAR1 из ACCU1 | — |
| `LAR1_AR2` | `LAR1 AR2` | `LAR1 AR2` | todo | `stl.addr_register` | LAR1 AR2 | — |
| `LAR2` | `LAR2` | `LAR2` | todo | `stl.addr_register` | загрузить AR2 | — |
| `LAR2_ACCU1` | `LAR2` | `LAR2` | todo | `stl.addr_register` | LAR2 из ACCU1 | — |
| `LC` | `LC` | `LC` | auto | `s5.timer` | LC — загрузить таймер/счётчик в BCD (F_S5Bcd, F_S5CounterBcd) | `test_stl_s5_timers_lower_to_s7compat_calls`<br>`test_stl_s5_read_before_write_is_frozen` |
| `LE_D` | `<=D` | `<=D` | auto | `stl.compare` | сравнение <=D | `test_stl_compare_is_first_check`<br>`test_stl_dint_real_arithmetic_and_compare` |
| `LE_I` | `<=I` | `<=I` | auto | `stl.compare` | сравнение <=I | `test_stl_compare_is_first_check`<br>`test_stl_dint_real_arithmetic_and_compare` |
| `LE_R` | `<=R` | `<=R` | auto | `stl.compare` | сравнение <=R | `test_stl_compare_is_first_check`<br>`test_stl_dint_real_arithmetic_and_compare` |
| `LEAVE` | `LEAVE` | `LEAVE` | todo | `stl.mode_b` | LEAVE (только 4 ACCU, S7-400) | — |
| `LN` | `LN` | `LN` | todo | `stl.math` | LN REAL | — |
| `LOOP` | `LOOP` | `LOOP` | todo | `stl.loop` | LOOP — цикл по ACCU1-L | — |
| `LT_D` | `<D` | `<D` | auto | `stl.compare` | сравнение <D | `test_stl_compare_is_first_check`<br>`test_stl_dint_real_arithmetic_and_compare` |
| `LT_I` | `<I` | `<I` | auto | `stl.compare` | сравнение <I | `test_stl_compare_is_first_check`<br>`test_stl_dint_real_arithmetic_and_compare` |
| `LT_R` | `<R` | `<R` | auto | `stl.compare` | сравнение <R | `test_stl_compare_is_first_check`<br>`test_stl_dint_real_arithmetic_and_compare` |
| `MCR_BRACK` | `MCR(` | `MCR(` | todo | `stl.mcr` | MCR( — открыть зону MCR | — |
| `MCRA` | `MCRA` | `MCRA` | todo | `stl.mcr` | включить MCR | — |
| `MCRD` | `MCRD` | `MCRD` | todo | `stl.mcr` | выключить MCR | — |
| `MOD_D` | `MOD` | `MOD` | auto | `stl.math` | остаток DINT | `test_stl_load_transfer_and_int_arithmetic`<br>`test_stl_dint_real_arithmetic_and_compare` |
| `MOVE` | `MOVE` | `MOVE` | todo | `stl.unknown` | MOVE в сети STL TIA (не документирован в справочнике STL) | — |
| `MOVE_BLOCK` | `MOVE_BLOCK` | `MOVE_BLOCK` | todo | `stl.unknown` | MOVE_BLOCK в сети STL TIA | — |
| `MUL_D` | `*D` | `*D` | auto | `stl.math` | *D | `test_stl_load_transfer_and_int_arithmetic`<br>`test_stl_dint_real_arithmetic_and_compare` |
| `MUL_I` | `*I` | `*I` | auto | `stl.math` | *I | `test_stl_load_transfer_and_int_arithmetic`<br>`test_stl_dint_real_arithmetic_and_compare` |
| `MUL_R` | `*R` | `*R` | auto | `stl.math` | *R | `test_stl_load_transfer_and_int_arithmetic`<br>`test_stl_dint_real_arithmetic_and_compare` |
| `NE_D` | `<>D` | `<>D` | auto | `stl.compare` | сравнение <>D | `test_stl_compare_is_first_check`<br>`test_stl_dint_real_arithmetic_and_compare` |
| `NE_I` | `<>I` | `<>I` | auto | `stl.compare` | сравнение <>I | `test_stl_compare_is_first_check`<br>`test_stl_dint_real_arithmetic_and_compare` |
| `NE_R` | `<>R` | `<>R` | auto | `stl.compare` | сравнение <>R | `test_stl_compare_is_first_check`<br>`test_stl_dint_real_arithmetic_and_compare` |
| `NEG` | `NOT` | `NOT` | auto | `stl.logic` | NOT — инверсия RLO | `test_stl_and_before_or_and_brackets`<br>`test_random_stl_chains_match_machine` |
| `NEG_D` | `NEGD` | `KZD` | todo | `stl.convert` | NEGD — смена знака DINT | — |
| `NEG_I` | `NEGI` | `KZW` | todo | `stl.convert` | NEGI — смена знака INT | — |
| `NEG_R` | `NEGR` | `NEGR` | todo | `stl.convert` | NEGR — смена знака REAL | — |
| `NOP_0` | `NOP 0` | `NOP 0` | auto | `stl.nop` | NOP 0 | `test_language_corpus_suites_pass_in_simulation` |
| `NOP_1` | `NOP 1` | `NOP 1` | auto | `stl.nop` | NOP 1 | `test_language_corpus_suites_pass_in_simulation` |
| `O` | `O` | `O` | auto | `stl.logic` | OR с операндом; без операнда — AND перед OR | `test_stl_and_before_or_and_brackets`<br>`test_random_stl_chains_match_machine` |
| `O_BRACK` | `O(` | `O(` | auto | `stl.logic` | O( — скобка | `test_stl_and_before_or_and_brackets`<br>`test_random_stl_chains_match_machine` |
| `OD` | `OD` | `OD` | todo | `stl.word_logic` | OD — логика двойных слов | — |
| `OffDelay` | `SF` | `SA` | check | `s5.timebase` | SF — задержка выключения (F_S5OffDelay) | `test_stl_s5_timers_lower_to_s7compat_calls`<br>`test_stl_s5_all_start_kinds_and_word_preset`<br>`test_reference_s5_timer_matches_awlsim` |
| `ON` | `ON` | `ON` | auto | `stl.logic` | OR NOT | `test_stl_and_before_or_and_brackets`<br>`test_random_stl_chains_match_machine` |
| `ON_BRACK` | `ON(` | `ON(` | auto | `stl.logic` | ON( — скобка | `test_stl_and_before_or_and_brackets`<br>`test_random_stl_chains_match_machine` |
| `OnDelay` | `SD` | `SE` | check | `s5.timebase` | SD — задержка включения (F_S5OnDelay) | `test_stl_s5_timers_lower_to_s7compat_calls`<br>`test_stl_s5_all_start_kinds_and_word_preset`<br>`test_reference_s5_timer_matches_awlsim` |
| `OPEN_DB` | `OPN` | `AUF` | todo | `stl.db_offset` | OPN DB — открыть DB (адресация по смещению) | — |
| `OPEN_DI` | `OPN DI` | `AUF DI` | todo | `stl.db_offset` | OPN DI | — |
| `OW` | `OW` | `OW` | todo | `stl.word_logic` | OW — логика слов | — |
| `POP` | `POP` | `POP` | todo | `stl.mode_b` | POP | — |
| `PSEUDO` | `PSEUDO` | `PSEUDO` | todo | `stl.unknown` | псевдоинструкция TIA (смысл не документирован) | — |
| `Pulse` | `SP` | `SI` | check | `s5.timebase` | SP — импульс (F_S5Pulse) | `test_stl_s5_timers_lower_to_s7compat_calls`<br>`test_stl_s5_all_start_kinds_and_word_preset`<br>`test_reference_s5_timer_matches_awlsim` |
| `PUSH` | `PUSH` | `PUSH` | todo | `stl.mode_b` | PUSH | — |
| `R` | `R` | `R` | auto | `stl.logic` | сбросить бит (с таймером/счётчиком — S5) | `test_stl_and_before_or_and_brackets`<br>`test_random_stl_chains_match_machine` |
| `Retentive` | `SS` | `SS` | check | `s5.timebase` | SS — задержка включения с памятью (F_S5RetOnDelay) | `test_stl_s5_timers_lower_to_s7compat_calls`<br>`test_stl_s5_all_start_kinds_and_word_preset`<br>`test_reference_s5_timer_matches_awlsim` |
| `Rise` | `FP` | `FP` | auto | `stl.edge` | FP: фронт RLO, явный бит памяти | `test_stl_fp_jcn_label_becomes_if_without_jmp` |
| `RLD` | `RLD` | `RLD` | todo | `stl.shift` | циклический сдвиг влево | — |
| `RLDA` | `RLDA` | `RLDA` | todo | `stl.mode_b` | сдвиг через CC1 влево | — |
| `RND` | `RND` | `RND` | todo | `stl.round` | округление к ближайшему (половина к чётному) | — |
| `RND_M` | `RND-` | `RND-` | todo | `stl.round` | округление вниз | — |
| `RND_P` | `RND+` | `RND+` | todo | `stl.round` | округление вверх | — |
| `RRD` | `RRD` | `RRD` | todo | `stl.shift` | циклический сдвиг вправо | — |
| `RRDA` | `RRDA` | `RRDA` | todo | `stl.mode_b` | сдвиг через CC1 вправо | — |
| `S` | `S` | `S` | auto | `stl.logic` | установить бит (с таймером/счётчиком — S5) | `test_stl_and_before_or_and_brackets`<br>`test_random_stl_chains_match_machine` |
| `SAVE` | `SAVE` | `SAVE` | todo | `stl.mode_b` | BR := RLO (ENO через BR) — режим B | — |
| `SET` | `SET` | `SET` | auto | `stl.logic` | RLO := 1 | `test_stl_and_before_or_and_brackets`<br>`test_random_stl_chains_match_machine` |
| `SIN` | `SIN` | `SIN` | todo | `stl.math` | SIN REAL | — |
| `SLD` | `SLD` | `SLD` | todo | `stl.shift` | сдвиг двойного слова влево | — |
| `SLW` | `SLW` | `SLW` | todo | `stl.shift` | сдвиг слова влево | — |
| `SQR` | `SQR` | `SQR` | todo | `stl.math` | SQR REAL | — |
| `SQRT` | `SQRT` | `SQRT` | todo | `stl.math` | SQRT REAL | — |
| `SRD` | `SRD` | `SRD` | todo | `stl.shift` | сдвиг двойного слова вправо | — |
| `SRSD` | `SSD` | `SSD` | todo | `stl.shift` | сдвиг DINT со знаком | — |
| `SRSW` | `SSI` | `SSI` | todo | `stl.shift` | сдвиг INT со знаком | — |
| `SRW` | `SRW` | `SRW` | todo | `stl.shift` | сдвиг слова вправо | — |
| `SUB_D` | `-D` | `-D` | auto | `stl.math` | -D | `test_stl_load_transfer_and_int_arithmetic`<br>`test_stl_dint_real_arithmetic_and_compare` |
| `SUB_I` | `-I` | `-I` | auto | `stl.math` | -I | `test_stl_load_transfer_and_int_arithmetic`<br>`test_stl_dint_real_arithmetic_and_compare` |
| `SUB_R` | `-R` | `-R` | auto | `stl.math` | -R | `test_stl_load_transfer_and_int_arithmetic`<br>`test_stl_dint_real_arithmetic_and_compare` |
| `T` | `T` | `T` | auto | `stl.accu` | записать ACCU1 (разные типы — stl.bitcopy) | `test_stl_load_transfer_and_int_arithmetic`<br>`test_zero_extension_mutation_is_caught` |
| `TAN` | `TAN` | `TAN` | todo | `stl.math` | TAN REAL | — |
| `TAR1` | `TAR1` | `TAR1` | todo | `stl.addr_register` | записать AR1 | — |
| `TAR1_ACCU1` | `TAR1` | `TAR1` | todo | `stl.addr_register` | TAR1 в ACCU1 | — |
| `TAR1_AR2` | `TAR1 AR2` | `TAR1 AR2` | todo | `stl.addr_register` | TAR1 AR2 | — |
| `TAR2` | `TAR2` | `TAR2` | todo | `stl.addr_register` | записать AR2 | — |
| `TAR2_ACCU1` | `TAR2` | `TAR2` | todo | `stl.addr_register` | TAR2 в ACCU1 | — |
| `TRUNC` | `TRUNC` | `TRUNC` | todo | `stl.convert` | отбрасывание дробной части | — |
| `UC` | `UC` | `UC` | auto | `stl.call` | UC — безусловный вызов FC без параметров | `test_language_corpus_suites_pass_in_simulation`<br>`test_external_samples_convert_with_expected_outcome` |
| `X` | `X` | `X` | auto | `stl.logic` | XOR | `test_stl_and_before_or_and_brackets`<br>`test_random_stl_chains_match_machine` |
| `X_BRACK` | `X(` | `X(` | auto | `stl.logic` | X( — скобка | `test_stl_and_before_or_and_brackets`<br>`test_random_stl_chains_match_machine` |
| `XD` | `XD` | `XOD` | todo | `stl.word_logic` | XD — логика двойных слов | — |
| `XN` | `XN` | `XN` | auto | `stl.logic` | XOR NOT | `test_stl_and_before_or_and_brackets`<br>`test_random_stl_chains_match_machine` |
| `XN_BRACK` | `XN(` | `XN(` | auto | `stl.logic` | XN( — скобка | `test_stl_and_before_or_and_brackets`<br>`test_random_stl_chains_match_machine` |
| `XW` | `XW` | `XOW` | todo | `stl.word_logic` | XW — логика слов | — |
