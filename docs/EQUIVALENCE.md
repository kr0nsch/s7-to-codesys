# Эквивалентность переводов LAD, FBD, STL, SCL и GRAPH

Как проверяется, что перевод сохранил поведение блока S7, и чего эта проверка не доказывает.

## Оракулы

| № | Оракул | Что сравнивается | Где |
|---|---|---|---|
| 1 | Сценарии CSV по описанию логики блока → наборы coUnit | выходы после каждого вызова со значениями, посчитанными моделями `scenarios/lang/reference` (и вручную — `HAND_CHECKS`) | CODESYS Control Win (`cds.py test`), интерпретатор ST `stsim` (pytest) |
| 2 | `s7conv equiv`: эталон S7 против `stsim` на переведённом ST | все выходы и статика после каждого вызова на строках сценариев и на случайных входах (`--random N --seed S`) | pytest, CI (`--random 500`, переходы STL `structured` и `pc`) |
| 3 | Семейство блоков | четыре перевода `FB_Starter` (LAD, FBD, STL, SCL) на одних входах: SCL сверяется с эталоном LAD того же семейства (`scenarios/lang/aliases.json`) | `equiv` |
| 4 | Свойства (hypothesis) | случайные цепочки STL со скобками до 7 уровней и случайные сети LAD (последовательно, ветви до трёх уровней, SR/RS): эталон против понижения | `s7conv/tests/test_equiv.py` |

Эталон — `s7conv/semantics/`: `net_eval` (поток питания LAD/FBD по справочнику LAD S7-300/400),
`stl_machine` (машина STL S7-300: /FC, OR-бит, стек скобок, 2 ACCU, OV/OS, переходы, таймеры и счётчики S5 —
`s5`) и `graph_seq` (последовательность GRAPH: шаги, переходы, ветви, действия, контроль, блокировка;
условия — тем же `net_eval`). Он не импортирует
понижение, эмиттер и таблицы соответствий — это проверяет `test_semantics_does_not_import_the_translator`.

Режим времени — R1 «строка = вызов» (`migration/prompts/00-INDEX.md` §4.5): перед вызовом часы `GVL_S7Clock`
ставятся на `t_ms` строки, эталон получает те же миллисекунды; таймеры переведённого кода — S7Compat
(`--timers s7compat`).

## Результат на корпусе `samples/lang`

`python -m s7conv equiv samples/lang --scenarios scenarios/lang --random 500 --seed 20261019`
(и с `--stl-jumps pc`), 2026-10-20:

| Блок | Эталон | Вызовов по сценариям | Случайных вызовов | Расхождений |
|---|---|---:|---:|---:|
| `FB_StarterLad` | LAD | 47 | 500 | 0 |
| `FB_StarterFbd` | FBD | 47 | 500 | 0 |
| `FB_StarterStl` | STL S7-300 | 47 | 500 | 0 |
| `FB_StarterScl` | семейство FB_Starter: эталон FB_StarterLad | 47 | 500 | 0 |
| `FB_PumpInterlockLad` | LAD (с вызовами FC_ClampPctLad) | 25 | 500 | 0 |
| `FB_ConveyorStl` | STL S7-300, таймер S5 (`s5`) | 58 | 500 | 0 |
| `FB_BackwashGraph` | GRAPH | 46 | 500 | 0 |

Те же сценарии в CODESYS Control Win: наборы `FB_StarterLad_ScenarioTest` … `FB_PumpInterlockLad_ScenarioTest`
пройдены (41 тест; [TEST_REPORT.md](TEST_REPORT.md)).

## Оракул ловит свои ошибки: мутации

Каждая мутация выключает одно правило перевода; тест обязан упасть.

| Мутация | Чем поймана | Тест |
|---|---|---|
| «старое SR→SR»: SR с битом-операндом в порядке RS (установка последней) | `equiv`: расхождение `xRun`/`xRunMem` в сценарии `StartAndStopTogether`; `stsim`: падает тот же сценарий набора `FB_StarterLad_ScenarioTest` | `test_old_sr_mapping_mutation_is_caught`, `test_old_flipflop_mapping_breaks_starter_scenario` |
| «старое SR→SR» для экземпляров SCL (одноимённый блок CODESYS) | coUnit в Control Win: `FB_StandardFlipFlop_Test.S7SrResetDominantViaRs` проверяет, что перевод S7 SR — CODESYS RS; модели `stsim` SR/RS проверены там же | `test_converted_s7_flipflops_keep_s7_priority_at_s_equal_r` |
| ENO арифметики = EN (без проверки переполнения) | `equiv` на блоке с `ADD` 32767 + 1: расхождение `xOk` | `test_eno_mutation_is_caught` |
| `L` INT → `T` DINT со знаковым расширением вместо дополнения нулями | `equiv`: расхождение `diOut` (-1 → 65535 у S7) | `test_zero_extension_mutation_is_caught` |
| GRAPH: переход из шага с ошибкой контроля не держится (без `NOT <Шаг>_SvErr`) | `stsim`: падают сценарий `Supervision` набора `FB_BackwashGraph_ScenarioTest` и `FB_BackwashGraph_SeqTest.SupervisionHoldsUntilAck` | `test_supervision_blocking_mutation_is_caught` |
| GRAPH: событие `S1` каждый цикл вместо однократного | `stsim`: падают все 6 сценариев `FB_BackwashGraph` и 2 теста общего набора | `test_s1_event_every_cycle_mutation_is_caught` |
| S5: SD не останавливается при RLO = 0 | `stsim`: сценарий `HornCutShort` конвейера и `FB_S5Timer_Test.OnDelayNeedsRloHeld` | `test_s5_on_delay_stop_mutation_is_caught` |

## Чего эта проверка не доказывает

- **Эталон — модель по руководствам, а не CPU.** Спорные места записаны в [ASSUMPTIONS.md](ASSUMPTIONS.md)
  (порядок элементов в сети LAD, запись результата ADD при переполнении, «AND перед OR» в STL).
  «Эквивалентно» значит «на сценариях и случайных входах по модели», не формальное доказательство.
- **Общий разбор XML.** Эталон и транслятор читают SimaticML одним разборщиком (`frontends`, `ir`): ошибка
  разбора ударит по обоим одинаково. Её закрывают сценарии по описанию логики (не по XML), XSD своей
  версии и приёмка открытых экспортов. awlsim (независимый эмулятор S7) пока сверяет только модель таймеров и
  счётчиков S5 (`test_s5_awlsim.py`); прогон программ STL целиком через awlsim — следующий выпуск.
- **Одинаковая модель STL.** Символьный подъём и машина `stl_machine` реализуют одну и ту же модель «AND
  перед OR» разным кодом (выражения против значений). Ошибку в самой модели они не поймают — её ловили бы
  awlsim или CPU. То же для GRAPH: ST-двойник и `graph_seq` реализуют один порядок цикла (допущения L18–L22);
  вариант SFC сверяется с двойником многоцикловым набором coUnit, а не эталоном.
- **Кольцо S7 → CODESYS → S7 не ловит симметричные ошибки.** Если прямой и обратный конвертер одинаково
  ошибаются в соответствии (SR ↔ SR при противоположных приоритетах), круговой перевод даёт исходный код.
  Ловит такое только смысловой оракул со сценарием S = R = 1 — он есть в `FB_Starter.csv`
  (`StartAndStopTogether`) и в `FB_StandardFlipFlop_Test`.
- **S7-1500.** После CALL слово состояния и ACCU не определены (⊥): эталон даёт ⊥ и не сравнивает зависящие
  от него выходы, а перевод ставит в этом месте пометку `stl.call_registers_1500`. Корпус 1.1.0 —
  STL S7-300.
