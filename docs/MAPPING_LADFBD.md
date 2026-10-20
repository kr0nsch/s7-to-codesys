# Соответствие LAD/FBD → ST: словарь элементов

Сгенерирован `s7conv 0.1.0` из таблиц конвертера — не редактировать, пересоздаётся `s7conv build-corpus`.

XSD SimaticML не ограничивает имена элементов `Part` и их пинов (`SimaticName`, `PinName_TE` —
`xs:string`), поэтому перевод держится на словаре: строка — имя Part, правило, что получается в ST и
откуда известны имя и пины. Уровень **H** — имя и пины есть в открытом экспорте TIA Portal
(`samples/lang/EXTERNAL.json`), **L** — по руководству Siemens, экспорта нет; элемент уровня L
переводится, но получает пометку `vocab_unverified` (не выше «требует проверки»). Префикс правила в
отчёте — `lad.` для LAD и `fbd.` для FBD. Неизвестный элемент — `unknown_part` (MIGRATION-TODO с UId),
висячий провод или потерянный операнд — `wire`.

| Part | Правило | Что | Уровень | Откуда имя и пины | ST | Тесты |
|---|---|---|---|---|---|---|
| `Calculate` | `calculate` | CALCULATE (Equation) | L | XSD LADFBD_v5: Equation — только для Calculate | выражение Equation с подстановкой IN1…INn | `test_limit_counter_return_and_calculate_boxes` |
| `Call` | `call` | вызов FB/FC (EN/ENO) | L | XSD LADFBD_v5: Call/CallInfo; экспорта нет | вызов FB/FC под `IF en`; вызываемый на LAD/FBD без ENO/BR — ENO = EN | `test_call_chain_eno_equals_en_for_plain_lad_callee` |
| `Coil` | `coil` | катушка (Negated operand — отрицающая) | H | lad-cookbook @ e131b25: MCPVerify_FB_LAD_v3.xml | `op := rlo;` (Negated operand — `op := NOT rlo;`) | `test_series_and_branches_give_and_or`<br>`test_set_reset_coils_and_negated_coil` |
| `Eq` | `compare` | сравнение == | H | lad-cookbook @ e131b25: MCPVerify_FC_LAD_v2.xml | `pre AND (a op b)` | `test_compare_with_pre_and_move_with_en` |
| `Ge` | `compare` | сравнение >= | H | lad-cookbook @ e131b25: MCPVerify_FC_LAD_v2.xml | `pre AND (a op b)` | `test_compare_with_pre_and_move_with_en` |
| `Gt` | `compare` | сравнение > | H | lad-cookbook @ e131b25: MCPVerify_FC_LAD.xml | `pre AND (a op b)` | `test_compare_with_pre_and_move_with_en` |
| `InRange` | `compare` | IN_RANGE | L | справка TIA, IN_RANGE | `pre AND (a op b)` | `test_compare_with_pre_and_move_with_en` |
| `Le` | `compare` | сравнение <= | H | lad-cookbook @ e131b25: MCPVerify_FC_LAD_v2.xml | `pre AND (a op b)` | `test_compare_with_pre_and_move_with_en` |
| `Lt` | `compare` | сравнение < | H | lad-cookbook @ e131b25: MCPVerify_FB_LAD_v3.xml | `pre AND (a op b)` | `test_compare_with_pre_and_move_with_en` |
| `Ne` | `compare` | сравнение <> | H | lad-cookbook @ e131b25: MCPVerify_FC_LAD_v2.xml | `pre AND (a op b)` | `test_compare_with_pre_and_move_with_en` |
| `OutRange` | `compare` | OUT_RANGE | L | справка TIA, OUT_RANGE | `pre AND (a op b)` | `test_compare_with_pre_and_move_with_en` |
| `A` | `contact` | AND (FBD) | L | s7kop/FBD: блок AND; имя Part «A» — по аналогии с «O» | булево выражение: последовательно — AND, ветви (O) — OR, Negated — NOT | `test_series_and_branches_give_and_or`<br>`test_random_lad_networks_match_power_flow` |
| `Contact` | `contact` | контакт (Negated — размыкающий) | H | lad-cookbook @ e131b25: MCPVerify_FB_LAD_v3.xml | булево выражение: последовательно — AND, ветви (O) — OR, Negated — NOT | `test_series_and_branches_give_and_or`<br>`test_random_lad_networks_match_power_flow` |
| `Not` | `contact` | NOT (инверсия RLO) | H | lad-cookbook @ e131b25: MCPVerify_FB_LAD_v3.xml | булево выражение: последовательно — AND, ветви (O) — OR, Negated — NOT | `test_series_and_branches_give_and_or`<br>`test_random_lad_networks_match_power_flow` |
| `O` | `contact` | слияние ветвей / OR | H | lad-cookbook @ e131b25: MCPVerify_FC_LAD.xml | булево выражение: последовательно — AND, ветви (O) — OR, Negated — NOT | `test_series_and_branches_give_and_or`<br>`test_random_lad_networks_match_power_flow` |
| `X` | `contact` | XOR (FBD) | L | блок XOR; имя Part «X» — по аналогии с «O» | булево выражение: последовательно — AND, ветви (O) — OR, Negated — NOT | `test_series_and_branches_give_and_or`<br>`test_random_lad_networks_match_power_flow` |
| `Convert` | `convert` | CONVERT (SrcType → DestType) | H | lad-cookbook @ e131b25: MCPVerify_FC_LAD_v2.xml | `SRC_TO_DST(in)` по SrcType/DestType | `test_external_samples_convert_with_expected_outcome` |
| `Round` | `convert` | ROUND | L | справка TIA, ROUND | `SRC_TO_DST(in)` по SrcType/DestType | `test_external_samples_convert_with_expected_outcome` |
| `Trunc` | `convert` | TRUNC | L | справка TIA, TRUNC | `SRC_TO_DST(in)` по SrcType/DestType | `test_external_samples_convert_with_expected_outcome` |
| `CTD` | `counter` | CTD (экземпляр) | L | справка TIA, CTD | вызов экземпляра `inst(CU := …, R := …, PV := …)` | `test_limit_counter_return_and_calculate_boxes` |
| `CTU` | `counter` | CTU (экземпляр) | L | справка TIA, CTU | вызов экземпляра `inst(CU := …, R := …, PV := …)` | `test_limit_counter_return_and_calculate_boxes` |
| `CTUD` | `counter` | CTUD (экземпляр) | L | справка TIA, CTUD | вызов экземпляра `inst(CU := …, R := …, PV := …)` | `test_limit_counter_return_and_calculate_boxes` |
| `NBox` | `edge` | N_TRIG: спад RLO, бит памяти bit | L | по аналогии с PBox | явный бит памяти: `q := clk AND NOT m; m := clk;` | `test_pbox_uses_explicit_memory_bit` |
| `NCoil` | `edge` | катушка N: импульс по спаду RLO | L | справка TIA, «-(N)-» | явный бит памяти: `q := clk AND NOT m; m := clk;` | `test_pbox_uses_explicit_memory_bit` |
| `NContact` | `edge` | контакт N: спад операнда, бит памяти bit | L | s7kop__b.pdf, §1.18 | явный бит памяти: `q := clk AND NOT m; m := clk;` | `test_pbox_uses_explicit_memory_bit` |
| `PBox` | `edge` | P_TRIG: фронт RLO, бит памяти bit | H | lad-cookbook @ e131b25: MCPVerify_FB_LAD_v3.xml | явный бит памяти: `q := clk AND NOT m; m := clk;` | `test_pbox_uses_explicit_memory_bit` |
| `PCoil` | `edge` | катушка P: импульс по фронту RLO | L | справка TIA, «-(P)-» | явный бит памяти: `q := clk AND NOT m; m := clk;` | `test_pbox_uses_explicit_memory_bit` |
| `PContact` | `edge` | контакт P: фронт операнда, бит памяти bit | L | s7kop__b.pdf, §1.17 | явный бит памяти: `q := clk AND NOT m; m := clk;` | `test_pbox_uses_explicit_memory_bit` |
| `And` | `instruction` | AND слов | L | справка TIA, AND | функция SCL (LIMIT, SEL, NORM_X → F_NormX, SCALE_X → F_ScaleX, SHL/SHR, MIN/MAX) | `test_limit_counter_return_and_calculate_boxes` |
| `Limit` | `instruction` | LIMIT | L | справка TIA, LIMIT | функция SCL (LIMIT, SEL, NORM_X → F_NormX, SCALE_X → F_ScaleX, SHL/SHR, MIN/MAX) | `test_limit_counter_return_and_calculate_boxes` |
| `Max` | `instruction` | MAX | L | справка TIA, MAX | функция SCL (LIMIT, SEL, NORM_X → F_NormX, SCALE_X → F_ScaleX, SHL/SHR, MIN/MAX) | `test_limit_counter_return_and_calculate_boxes` |
| `Min` | `instruction` | MIN | L | справка TIA, MIN | функция SCL (LIMIT, SEL, NORM_X → F_NormX, SCALE_X → F_ScaleX, SHL/SHR, MIN/MAX) | `test_limit_counter_return_and_calculate_boxes` |
| `NormX` | `instruction` | NORM_X | L | справка TIA, NORM_X | функция SCL (LIMIT, SEL, NORM_X → F_NormX, SCALE_X → F_ScaleX, SHL/SHR, MIN/MAX) | `test_limit_counter_return_and_calculate_boxes` |
| `Or` | `instruction` | OR слов | L | справка TIA, OR | функция SCL (LIMIT, SEL, NORM_X → F_NormX, SCALE_X → F_ScaleX, SHL/SHR, MIN/MAX) | `test_limit_counter_return_and_calculate_boxes` |
| `ScaleX` | `instruction` | SCALE_X | L | справка TIA, SCALE_X | функция SCL (LIMIT, SEL, NORM_X → F_NormX, SCALE_X → F_ScaleX, SHL/SHR, MIN/MAX) | `test_limit_counter_return_and_calculate_boxes` |
| `Sel` | `instruction` | SEL | L | справка TIA, SEL | функция SCL (LIMIT, SEL, NORM_X → F_NormX, SCALE_X → F_ScaleX, SHL/SHR, MIN/MAX) | `test_limit_counter_return_and_calculate_boxes` |
| `Shl` | `instruction` | SHL | L | справка TIA, SHL | функция SCL (LIMIT, SEL, NORM_X → F_NormX, SCALE_X → F_ScaleX, SHL/SHR, MIN/MAX) | `test_limit_counter_return_and_calculate_boxes` |
| `Shr` | `instruction` | SHR | L | справка TIA, SHR | функция SCL (LIMIT, SEL, NORM_X → F_NormX, SCALE_X → F_ScaleX, SHL/SHR, MIN/MAX) | `test_limit_counter_return_and_calculate_boxes` |
| `Xor` | `instruction` | XOR слов | L | справка TIA, XOR | функция SCL (LIMIT, SEL, NORM_X → F_NormX, SCALE_X → F_ScaleX, SHL/SHR, MIN/MAX) | `test_limit_counter_return_and_calculate_boxes` |
| `Jump` | `jump` | прыжок JMP к метке | L | XSD LADFBD_v5: Labels; экспорта нет | прыжок вперёд через сети → `IF NOT rlo THEN … END_IF` | `test_forward_jump_over_networks_becomes_if` |
| `JumpNot` | `jump` | прыжок JMPN к метке | L | XSD LADFBD_v5: Labels; экспорта нет | прыжок вперёд через сети → `IF NOT rlo THEN … END_IF` | `test_forward_jump_over_networks_becomes_if` |
| `Abs` | `math` | ABS | L | справка TIA, ABS | `IF en THEN out := a op b; END_IF`; подключённый ENO — `F_S7Eno<Оп><Тип>` до записи | `test_add_with_connected_eno_uses_s7compat_before_write` |
| `Add` | `math` | ADD | H | lad-cookbook @ e131b25: MCPVerify_FC_LAD.xml | `IF en THEN out := a op b; END_IF`; подключённый ENO — `F_S7Eno<Оп><Тип>` до записи | `test_add_with_connected_eno_uses_s7compat_before_write` |
| `Div` | `math` | DIV | H | lad-cookbook @ e131b25: MCPVerify_FC_LAD_v2.xml | `IF en THEN out := a op b; END_IF`; подключённый ENO — `F_S7Eno<Оп><Тип>` до записи | `test_add_with_connected_eno_uses_s7compat_before_write` |
| `Mod` | `math` | MOD | H | lad-cookbook @ e131b25: MCPVerify_FC_LAD_v2.xml | `IF en THEN out := a op b; END_IF`; подключённый ENO — `F_S7Eno<Оп><Тип>` до записи | `test_add_with_connected_eno_uses_s7compat_before_write` |
| `Mul` | `math` | MUL | H | lad-cookbook @ e131b25: MCPVerify_FC_LAD_v2.xml | `IF en THEN out := a op b; END_IF`; подключённый ENO — `F_S7Eno<Оп><Тип>` до записи | `test_add_with_connected_eno_uses_s7compat_before_write` |
| `Neg` | `math` | NEG | L | справка TIA, NEG | `IF en THEN out := a op b; END_IF`; подключённый ENO — `F_S7Eno<Оп><Тип>` до записи | `test_add_with_connected_eno_uses_s7compat_before_write` |
| `Sub` | `math` | SUB | H | lad-cookbook @ e131b25: MCPVerify_FC_LAD_v2.xml | `IF en THEN out := a op b; END_IF`; подключённый ENO — `F_S7Eno<Оп><Тип>` до записи | `test_add_with_connected_eno_uses_s7compat_before_write` |
| `Move` | `move` | MOVE (en, in, out1…outN) | H | lad-cookbook @ e131b25: MCPVerify_FC_LAD.xml | `IF en THEN out := in; END_IF`, ENO = EN | `test_compare_with_pre_and_move_with_en` |
| `Return` | `return` | RET | L | справка TIA, RET | `IF rlo THEN RETURN; END_IF` | `test_limit_counter_return_and_calculate_boxes` |
| `RCoil` | `set_reset` | катушка R | H | lad-cookbook @ e131b25: MCPVerify_FC_LAD.xml | `IF rlo THEN op := TRUE/FALSE; END_IF` | `test_set_reset_coils_and_negated_coil` |
| `SCoil` | `set_reset` | катушка S | H | lad-cookbook @ e131b25: MCPVerify_FC_LAD.xml | `IF rlo THEN op := TRUE/FALSE; END_IF` | `test_set_reset_coils_and_negated_coil` |
| `RS` | `sr_operand` | RS с битом-операндом: установка главнее | L | s7kop__b.pdf, §1.11 | два IF в порядке S7 (SR: сначала S, затем R1; RS: сначала R, затем S1), `q := op` | `test_flipflop_with_operand_keeps_s7_order`<br>`test_old_flipflop_mapping_breaks_starter_scenario`<br>`test_old_sr_mapping_mutation_is_caught` |
| `SR` | `sr_operand` | SR с битом-операндом: сброс главнее | L | s7kop__b.pdf, §1.10 | два IF в порядке S7 (SR: сначала S, затем R1; RS: сначала R, затем S1), `q := op` | `test_flipflop_with_operand_keeps_s7_order`<br>`test_old_flipflop_mapping_breaks_starter_scenario`<br>`test_old_sr_mapping_mutation_is_caught` |
| `TOF` | `timer` | TOF (экземпляр) | L | по аналогии с TON | вызов экземпляра `inst(IN := …, PT := …)`, выходы `inst.Q/ET`; TON_TIME → TON или FB_S7Ton | `test_language_corpus_suites_pass_in_simulation`<br>`test_document_header_interface_and_units` |
| `TON` | `timer` | TON (экземпляр) | H | lad-cookbook @ e131b25: MCPVerify_FB_LAD_v3.xml | вызов экземпляра `inst(IN := …, PT := …)`, выходы `inst.Q/ET`; TON_TIME → TON или FB_S7Ton | `test_language_corpus_suites_pass_in_simulation`<br>`test_document_header_interface_and_units` |
| `TP` | `timer` | TP (экземпляр) | L | по аналогии с TON | вызов экземпляра `inst(IN := …, PT := …)`, выходы `inst.Q/ET`; TON_TIME → TON или FB_S7Ton | `test_language_corpus_suites_pass_in_simulation`<br>`test_document_header_interface_and_units` |

Элементов в словаре: 57; подтверждены открытым экспортом (H): 21, по руководству
(L): 36.

## Ловушки, которые перевод учитывает явно

| Ловушка | Как переводится | Правило |
|---|---|---|
| SR/RS у S7 и CODESYS называются одинаково, приоритет противоположный; в LAD/FBD состояние хранит бит-операнд | два IF на бит-операнд в порядке S7; экземпляр SR/RS CODESYS не используется (бит пишут другие сети и HMI) | `sr_operand` |
| ENO = EN AND NOT ошибка блока (LAD S7-300/400, прил. C.1); в CODESYS ENO = EN | ENO арифметики INT/DINT — `F_S7Eno<Оп><Тип>` до записи результата; прочее — ENO = EN с пометкой | `eno_error` |
| бит памяти P/N может читать другая сеть | явная переменная-бит, а не скрытая память R_TRIG | `edge` |
| бит памяти фронта во временной области (ошибка исходной программы) | перевод как есть, пометка | `edge_memory` |
| деление на 0: S7 — ENO = 0, CODESYS — исключение | деление под условием делитель <> 0 | `div_zero` |
| вызов блока, который пишет ENO/BR | ENO = EN с пометкой | `call_eno` |

Сети SCL внутри блока LAD/FBD переводятся как SCL (правило `scl.network`); сети STL — по
[MAPPING_STL.md](MAPPING_STL.md).
