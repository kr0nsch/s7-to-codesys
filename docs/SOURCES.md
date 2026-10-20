# Источники

Документы вендоров и чужой код в репозиторий не кладутся — только ссылки. Где правило перевода опирается
на источник, номер раздела указан в коде (docstring) и в справочниках соответствий.

## Siemens

| Документ | Что из него взято |
|---|---|
| Statement List (STL) for S7-300 and S7-400, A5E00706960-01 — https://cache.industry.siemens.com/dl/files/496/18653496/att_97188/v1/AWL_e.pdf | машина STL: слово состояния, «AND перед OR», скобки (7 уровней), 2/4 аккумулятора, `L` обнуляет ACCU1 (§9.2), арифметика только ACCU1-L/ACCU2-L (§7.3), переходы, S5-таймеры (гл. 12) — `semantics/stl_machine.py`, `lower/stl_lift.py` |
| Ladder Logic (LAD) for S7-300 and S7-400, A5E02790079-01 — https://cache.industry.siemens.com/dl/files/822/45523822/att_82001/v1/s7kop__b.pdf | SR — сброс главнее (§1.10), RS — установка главнее (§1.11), фронты P/N с битом памяти, ENO = EN AND NOT ошибка (прил. C.1) — `semantics/net_eval.py`, `lower/net_to_ast.py` |
| FAQ 67655405 «Migration of STL Programs to S7-1500» — https://support.industry.siemens.com/cs/ww/en/view/67655405 | профиль S7-1500: 2 ACCU, после CALL слово состояния и ACCU не определены, регистр DB, нет MCR/ENT/LEAVE |
| TIA Portal Openness V19, System Manual 11/2023 — https://support.industry.siemens.com/cs/attachments/109826886/TIAPortalOpenness_enUS_en-US.pdf | экспорт блоков FB/FC/OB/DB на STL/FBD/LAD/GRAPH/SCL в SimaticML (с. 1350–1351), `GenerateSource` только для `.awl/.scl/.db/.udt` (с. 510–511) |
| S7-GRAPH V5.3 for S7-300/400, A5E00290656-01 — https://cache.industry.siemens.com/dl/files/630/1137630/att_28560/v1/Graph7_e.pdf | модель GRAPH (следующий выпуск) |
| XSD SimaticML V15.1–V21 — копии в https://github.com/dotnetprojects/DotNetSiemensPLCToolBoxLibrary/tree/bbe5beccbadcf7497408e92883e260cc5024a874/externalDlls/siemens | структура `Sections`, `FlgNet`, `StatementList`, `StructuredText`; 172 значения `StlToken` (`SW.PlcBlocks.STL_v5.xsd`); SHA-256 файлов — `samples/lang/EXTERNAL.json`; © Siemens AG, в git не кладутся |

## CODESYS

| Документ | Что из него взято |
|---|---|
| Офлайн-справка CODESYS 3.5.17.30, библиотека Standard (`standard.chm`: SR, RS, CTU, CTD, CTUD) | модели `stsim` (`builtin_flipflop`, `builtin_counter`); SR — set-dominant (`SET1`), RS — reset-dominant (`RESET1`). Справка пишет о входах «Rising edge» — поведение по уровню подтверждено тестом `RsSetHeldReappliesAfterReset` в Control Win |
| Офлайн-справка CODESYS 3.5.17.30 (`codesys.chm`): `JMP` в ST, ENO у блоков FBD/LD | ENO = EN; `JMP` есть, но в `src/` не используется (RuSTy и iec_checker его не разбирают) |

## Открытые экспорты TIA (приёмка разборщика)

| Репозиторий | Лицензия | Использование |
|---|---|---|
| bulaofen0036-coder/TIA_Portal_Openness_MCP @ e131b2570c75c323bc330e9793c293e4b5f231c6, `tools/tiaportal-mcp/skill/lad-cookbook` | MIT | имена и пины элементов LAD уровня H в словаре; приёмочный тест (файлы скачиваются, в git не кладутся) |
| asier-vega-gutierrez/Smart_Factory @ a2fdad2cd4643facb8d175d04ff896fc42c29ad7 | Apache-2.0 | экспорт STL V18 для приёмочного теста |

Не используются: репозитории без лицензии и siemens/tia-portal-openness-code-snippets (лицензия запрещает
использование в России).

## Идеи

| Источник | Что взято |
|---|---|
| CBMC, STL-фронтенд — https://github.com/diffblue/cbmc/tree/develop/src/statement-list (лицензия BSD-подобная) | символьный подъём STL: /FC и OR-бит как значения времени трансляции, RLO как выражение, стек скобок; код не копировался |
| Czarnak/simaticml-decoder — https://github.com/Czarnak/simaticml-decoder (MIT) | что открытого перекомпилируемого перевода LAD/FBD/STL/GRAPH из SimaticML нет; код не копировался |
