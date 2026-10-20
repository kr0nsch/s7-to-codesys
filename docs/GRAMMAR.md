# Грамматика подмножества SCL, которое разбирает s7conv

Вход — исходники SCL в формате выгрузки TIA Portal («Generate source from blocks», файлы `*.scl`,
V15–V18) и близкий к нему классический SCL STEP 7. Реализация — `s7conv/lexer.py` (лексер) и
`s7conv/parser.py` (разборщик), модель AST — `s7conv/nodes.py`. Что делается с разобранными
конструкциями при генерации ST, описано в [MAPPING.md](MAPPING.md).

Сети SCL из SimaticML (`StructuredText`) собираются из токенов XML в текст и разбираются этим же
разборщиком; сети LAD, FBD и STL понижаются в текст SCL (`s7conv/lower/`) и тоже проходят через него —
грамматики XML здесь нет, разбор SimaticML описан в [ARCHITECTURE.md](ARCHITECTURE.md), раздел «Все языки».

## Выбор подхода: рекурсивный спуск, а не lark

Разборщик написан вручную (рекурсивный спуск с приоритетами операций). Причины:

1. **Восстановление после ошибок на уровне оператора.** Неразобранный оператор не должен ронять файл:
   он становится узлом `RawStmt` (исходный текст + причина), эмиттер выводит его как
   `// MIGRATION-TODO: оператор не разобран` с закомментированным исходником, а разбор продолжается
   со следующего оператора. Так же — объявления (`RawDecl`) и блоки (`RawBlock`). В lark (Earley/LALR)
   такое восстановление делается обработчиками ошибок и пересинхронизацией вручную — кода не меньше,
   а контроль хуже.
2. **Комментарии переносятся в ST.** Лексер не выбрасывает комментарии, а привязывает их к следующему
   токену; разборщик раздаёт их операторам и объявлениям (перед оператором, в конце строки, внутри
   многострочного вызова, перед `END_IF`). Для миграции это важно: комментарии — документация логики.
3. **Контекстная лексика TIA.** Строки заголовка блока (`TITLE = ...`, `AUTHOR : ...`) читаются до конца
   строки, но только в «зоне заголовка» — `name : String;` в секции `VAR` остаётся объявлением; имя
   `REGION` — остаток строки; тело литерала зависит от префикса (`DT#2024-01-31-12:00:00` содержит `-`
   и `:`); `"..."` — символ, а не строка. Это проще выразить кодом лексера, чем грамматикой без
   конфликтов.
4. **Точные позиции.** У каждого оператора и объявления есть строка и смещения в файле — по ним
   строится отчёт (номера строк) и выводится закомментированный исходный текст.

Свойство «разбор ∘ печать» для выражений проверяется hypothesis
(`s7conv/tests/test_roundtrip.py`): для любого выражения из всех поддерживаемых форм
`parse_expression(expr_to_scl(e)) == e`, где `expr_to_scl` ставит минимум скобок.

## Лексика

| Лексема | Примеры | Примечание |
|---|---|---|
| Комментарии | `// ...`, `(* ... *)` | `(* *)` не вкладываются (как в SCL); сохраняются и переносятся в ST |
| Прагмы, атрибуты | `{ S7_Optimized_Access := 'TRUE' }`, `{InstructionName := 'TON_TIME'; LibVersion := '1.0'}` | атрибуты блока и переменной; прагма в теле — оператор `Pragma` |
| Локальная переменная | `#start`, `#"имя с пробелом"` | |
| Глобальный символ | `"DB_Plant"`, `"Start_PB"`, `"FC_Scale"` | DB, тег, блок — различает таблица символов эмиттера |
| Имя | `ABS`, `NORM_X`, `ENO`, `a` | функции, флаги, переменные классического SCL и BEGIN блока данных |
| Целое, вещественное | `42`, `1_000`, `3.14`, `1.5e-3`, `2E5` | `0..9` — целое, `..`, целое |
| Строка | `'текст'`, `'it$'s'`, `'$N'` | экранирование `$` |
| Литерал с префиксом | `T#5s`, `TIME#1h30m`, `LT#5s`, `S5T#2s`, `D#2024-01-31`, `TOD#08:30:00`, `DT#2024-01-31-12:00:00`, `16#FF`, `2#1010`, `8#17`, `B#16#0F`, `W#16#FFFF`, `DW#16#...`, `LW#16#...`, `L#100`, `INT#-5`, `REAL#1.5`, `BOOL#TRUE`, `CHAR#'A'`, `WSTRING#'abc'`, `C#5`, `P#M100.0 BYTE 16` | тело литерала разбирается по префиксу |
| Прямой адрес | `%I0.0`, `%IW64`, `%QW80`, `%MD20`, `%M12.1`, `%IW272:P`, `%DB30.DBW0` | немецкая мнемоника `%E`/`%A` тоже |
| Срез | `.%X3`, `.%B1`, `.%W0`, `.%D0` | после `.` |
| Свойство заголовка | `TITLE = ...`, `AUTHOR : ...`, `FAMILY : ...`, `NAME : ...`, `VERSION : 0.1` | только между строкой блока и первой секцией |
| Имя REGION | `REGION Pump group (P101...P103)` | остаток строки до `//` |
| Операции | `:=` `=>` `+=` `-=` `*=` `/=` `?=` `**` `..` `<=` `>=` `<>` `=` `<` `>` `+` `-` `*` `/` `&` `^` `( ) [ ] , ; : .` | `AND OR XOR NOT MOD` — ключевые слова |

Регистр ключевых слов не важен. Вход декодируется как UTF-8 (с BOM или без), иначе как cp1251;
переводы строк CRLF/CR приводятся к LF, табы допустимы. Неизвестный символ даёт токен ошибки —
оператор с ним уходит в `RawStmt`.

## Синтаксис (EBNF)

```ebnf
source      = { block | text_outside } ;
block       = fb | fc | ob | db | udt ;
fb          = "FUNCTION_BLOCK" name header { section } [ "BEGIN" ] { statement } "END_FUNCTION_BLOCK" ;
fc          = "FUNCTION" name [ ":" type ] header { section } [ "BEGIN" ] { statement } "END_FUNCTION" ;
ob          = "ORGANIZATION_BLOCK" name header { section } [ "BEGIN" ] { statement } "END_ORGANIZATION_BLOCK" ;
db          = "DATA_BLOCK" name header ( { section } | "STRUCT" fields "END_STRUCT" [";"] | type header )
              [ "BEGIN" { statement } ] "END_DATA_BLOCK" ;
udt         = "TYPE" name header ( "STRUCT" fields "END_STRUCT" [";"] | type ) "END_TYPE" ;
name        = QIDENT | IDENT ;
header      = { HEADER_PROP | PRAGMA | flag } ;
flag        = "NON_RETAIN" | "RETAIN" | "KNOW_HOW_PROTECT" | "READ_ONLY" | "UNLINKED" | "CODE_VERSION1" ;

section     = section_kw { modifier } { declaration } section_end [ ";" ] ;
section_kw  = "VAR_INPUT" | "VAR_OUTPUT" | "VAR_IN_OUT" | "VAR" | "VAR_TEMP" | "VAR_STAT" | "CONST" | "LABEL" ;
modifier    = "CONSTANT" | "RETAIN" | "NON_RETAIN" | "DB_SPECIFIC" | "PERSISTENT" ;
section_end = "END_VAR" | "END_CONST" | "END_LABEL" ;
declaration = var_name { PRAGMA } { "," var_name } [ "AT" postfix ] ":" type { PRAGMA } [ ":=" init ] ";"
            | var_name ":=" expression ";"                       (* CONST классического SCL *) ;
var_name    = IDENT | QIDENT ;
fields      = { declaration } ;
type        = IDENT                                               (* Int, Bool, TON_TIME, IEC_TIMER ... *)
            | QIDENT                                              (* "UDT_X", "FB_Y" *)
            | ( "String" | "WString" ) [ "[" expression "]" ]
            | "Array" "[" range { "," range } "]" "of" type
            | "Struct" fields "END_STRUCT"
            | "REF_TO" type ;
range       = "*" | expression ".." expression ;
init        = expression | "[" init_item { "," init_item } "]" ;
init_item   = INT "(" init ")" | init ;

statement   = assignment | call_stmt | if | case | for | while | repeat | region
            | "EXIT" ";" | "CONTINUE" ";" | "RETURN" ";" | "GOTO" IDENT ";" | IDENT ":"   (* метка *)
            | PRAGMA | ";" ;
assignment  = postfix ( ":=" | "+=" | "-=" | "*=" | "/=" | "?=" ) expression ";" ;
call_stmt   = postfix_call ";" ;
if          = "IF" expression "THEN" { statement } { "ELSIF" expression "THEN" { statement } }
              [ "ELSE" { statement } ] "END_IF" [";"] ;
case        = "CASE" expression "OF" { labels ":" { statement } } [ "ELSE" [":"] { statement } ] "END_CASE" [";"] ;
labels      = label { "," label } ;
label       = additive [ ".." additive ] ;
for         = "FOR" postfix ":=" expression "TO" expression [ "BY" expression ] "DO" { statement } "END_FOR" [";"] ;
while       = "WHILE" expression "DO" { statement } "END_WHILE" [";"] ;
repeat      = "REPEAT" { statement } "UNTIL" expression [";"] "END_REPEAT" [";"] ;
region      = "REGION" [ REGION_NAME ] { statement } "END_REGION" [";"] ;

expression  = xor { "OR" xor } ;
xor         = and { "XOR" and } ;
and         = equality { ( "AND" | "&" ) equality } ;
equality    = relation { ( "=" | "<>" ) relation } ;
relation    = additive { ( "<" | ">" | "<=" | ">=" ) additive } ;
additive    = term { ( "+" | "-" ) term } ;
term        = unary { ( "*" | "/" | "MOD" ) unary } ;
unary       = ( "-" | "+" | "NOT" ) unary | power ;
power       = postfix { "**" power_rhs } ;
power_rhs   = ( "-" | "+" | "NOT" ) power_rhs | postfix ;
postfix     = primary { "." ( IDENT | QIDENT | SLICE | INT ) | "[" expression { "," expression } "]"
                        | "(" [ argument { "," argument } ] ")" } ;
argument    = IDENT ( ":=" | "=>" ) expression | expression ;
primary     = literal | LOCAL | QIDENT | IDENT | ADDRESS | "(" expression ")" ;
```

`;` после простого оператора обязателен, но его отсутствие перед `END_...`, `ELSE`, `ELSIF`, `UNTIL`
допускается (так пишут вручную). `BEGIN` в FB/FC/OB необязателен (классический SCL).

### Приоритеты операций

От сильного к слабому; бинарные операции левоассоциативны.

| Приоритет | Операции | Как в справке TIA Portal / МЭК 61131-3 |
|---|---|---|
| 1 | `( )`, вызов, `.`, `[ ]` | да |
| 2 | `**` | да; `-2 ** 2` = `-(2 ** 2)`; показатель может быть со знаком: `2 ** -1` |
| 3 | унарные `-`, `+`, `NOT` | да |
| 4 | `*`, `/`, `MOD` | да |
| 5 | `+`, `-` | да |
| 6 | `<`, `>`, `<=`, `>=` | да |
| 7 | `=`, `<>` | да |
| 8 | `AND`, `&` | да |
| 9 | `XOR` | да |
| 10 | `OR` | да |

Ассоциативность `**` в справке TIA Portal явно не нашлась — принята левая, как у остальных
операций МЭК (сверить с источником). На результат конвертации это не влияет: `**` выводится как
`EXPT(a, b)` с явной вложенностью.

## Восстановление после ошибок

| Где ошибка | Что становится | Куда идёт разбор дальше |
|---|---|---|
| Простой оператор | `RawStmt` с текстом до `;` | следующий оператор |
| Составной оператор (`IF`, `CASE`, `FOR`, `WHILE`, `REPEAT`, `REGION`) | `RawStmt` до парного `END_...` | следующий оператор |
| Объявление | `RawDecl` до `;` | следующее объявление |
| Заголовок/структура блока | `RawBlock` до `END_<вид блока>` | следующий блок |
| Текст вне блоков | `RawBlock` «текст вне блока» | следующий блок |

Каждая ошибка попадает в `SourceFile.issues` (строка, столбец, причина) — их печатает `s7conv check`,
а отчёт конвертации показывает как «не поддерживается: не разобрано».

## Что разбирается, но не переводится

Эти конструкции разборщик понимает (без ошибок разбора), а эмиттер выводит как `MIGRATION-TODO`
с причиной — подробности в [MAPPING.md](MAPPING.md), раздел «Не поддерживается»:

- `GOTO` и метки переходов;
- `AT`-наложения переменных, `REF_TO`, типы `Variant`, `Any`, `Pointer`, `DB_ANY`, `DTL`, системные
  типы `HW_*`, `OB_*`, `EVENT_*`, `CONN_*`;
- `ENO`, `EN`, `OK`; присваивание `?=`;
- запись в срезы `.%B/.%W/.%D` (чтение переводится);
- адреса `%DB30.DBW0`, `%L`, `%T`, `%C`, прямой доступ к периферии `%IW272:P`;
- литералы `P#...` (указатель ANY) и `C#...`;
- системные функции без аналога в CODESYS Standard (`PEEK`, `POKE`, `RD_SYS_T`, `RUNTIME`, `TypeOf`,
  `BLKMOV`, таймеры S5 `S_ODT` и др.).

## Что не разбирается

Конструкции вне подмножества — оператор с ними становится `RawStmt` (`MIGRATION-TODO: оператор не
разобран`):

| Конструкция | Пример | Почему нет |
|---|---|---|
| Множественное присваивание | `#a := #b := 0;` | редкость в выгрузках TIA; перепишите двумя операторами |
| Разыменование | `#ref^ := 1;` | ссылки S7 не переносятся |
| Классический вызов `FB.DB` | `FB10.DB10(...)` | только форма TIA: `"DB"(...)` или `#inst(...)` |
| Вложенные комментарии | `(* (* *) *)` | SCL их не допускает: первая `*)` закрывает комментарий |
| `/* ... */` | | в SCL TIA нет |
| Текстовые исходники STL (`.awl`), GRAPH | | этот разборщик читает только SCL; LAD, FBD и STL принимаются в SimaticML (`*.xml`), GRAPH и `.awl` — следующий выпуск |

Корпус `samples/scl/` (20 файлов, 44 блока) разбирается полностью: `python -m s7conv check samples/scl`.
