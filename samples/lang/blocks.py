"""Корпус всех языков S7: описание блоков вымышленной водопроводной станции (ВОС «Северная»).

Из этого файла samples/lang/build_xml.py собирает SimaticML (samples/lang/*.xml). Описание логики — в
комментарии блока (ru-RU) и samples/lang/README.md; эталонные модели сценариев
(scenarios/lang/reference/model_*.py) написаны по описанию, а не по коду.

Блоки:
- FB_StarterLad / FB_StarterFbd / FB_StarterStl / FB_StarterScl — один пускатель насоса на четырёх языках
  с общим интерфейсом и общими сценариями (scenarios/lang/FB_Starter.csv);
- FB_PumpInterlockLad — блокировки насоса по уровню и давлению: S/R, сравнения, MOVE, прыжок вперёд,
  P-фронт с битом, который читается в другой сети, ADD с ENO, цепочка трёх вызовов EN → ENO → EN;
- FC_ClampPctLad — ограничение значения (LAD), вызывается из FB_PumpInterlockLad;
- DB_Process (стандартный доступ, смещения членов) и UDT_Valve — данные для STL.
"""

from __future__ import annotations

from build_xml import Block, Member, Net, Scl, Section, Stl, Unit, lad_unit, scl_unit, stl_unit

STARTER_DESCRIPTION = """Пускатель насоса с контролем обратной связи (один блок на LAD, FBD, STL, SCL).
1. Пуск/стоп — SR с битом-операндом xRunMem: S = xStart AND xInterlock; R1 = xStop OR NOT xInterlock OR xFault.
   SR S7: сначала S, затем R1 — при S = R1 = 1 (Пуск и Стоп одновременно) бит сброшен. xRun := xRunMem.
2. Контроль обратной связи: TON tonFeedback (IN = xRun AND NOT xFeedback, PT = tFeedbackTime).
3. Авария с самоподхватом: xFault := (tonFeedback.Q OR xFault) AND NOT xReset.
4. Счётчик пусков: по фронту xRun (бит памяти xEdgeMem) iStarts := iStarts + 1.
Порядок сетей 1-4; xFault в сети 1 — значение прошлого вызова."""


def starter_sections(extra_temp: list[Member] | None = None) -> list[Section]:
    """Общий интерфейс четырёх вариантов FB_Starter."""
    return [
        Section(
            "Input",
            [
                Member("xStart", "Bool", "Пуск (кнопка)"),
                Member("xStop", "Bool", "Стоп (кнопка, TRUE — нажата)"),
                Member("xInterlock", "Bool", "Блокировки в норме, пуск разрешён", start="TRUE"),
                Member("xFeedback", "Bool", "Обратная связь контактора"),
                Member("tFeedbackTime", "Time", "Допустимое время без обратной связи", start="T#2S"),
                Member("xReset", "Bool", "Сброс аварии"),
            ],
        ),
        Section(
            "Output",
            [
                Member("xRun", "Bool", "Команда контактору"),
                Member("xFault", "Bool", "Авария: нет обратной связи"),
                Member("iStarts", "Int", "Число пусков"),
            ],
        ),
        Section("InOut"),
        Section(
            "Static",
            [
                Member("xRunMem", "Bool", "Бит-операнд SR пуска"),
                Member("xEdgeMem", "Bool", "Бит памяти фронта xRun"),
                Member("tonFeedback", "TON_TIME", "Таймер контроля обратной связи", version="1.0"),
            ],
        ),
        Section("Temp", extra_temp or []),
        Section("Constant"),
    ]


# ---------------------------------------------------------------------------
# FB_Starter на LAD
# ---------------------------------------------------------------------------


def starter_lad() -> Block:
    nets: list[Net] = []
    # 1. SR с битом-операндом
    n = Net("Пуск/стоп: SR, сброс главнее")
    s = n.contact(n.contact("rail", "#xStart"), "#xInterlock")
    r_stop = n.contact("rail", "#xStop")
    r_il = n.contact("rail", "#xInterlock", neg=True)
    r_flt = n.contact("rail", "#xFault")
    r = n.orr(r_stop, r_il, r_flt)
    sr = n.part("SR")
    n.wire(s, (sr, "s"))
    n.wire(r, (sr, "r1"))
    n.operand_in(sr, "operand", "#xRunMem")
    n.coil((sr, "q"), "#xRun")
    nets.append(n)
    # 2. TON обратной связи
    n = Net("Контроль обратной связи")
    rlo = n.contact(n.contact("rail", "#xRun"), "#xFeedback", neg=True)
    ton = n.part("TON", version="1.0", instance="#tonFeedback", templates=[("time_type", "Type", "Time")])
    n.wire(rlo, (ton, "IN"))
    n.operand_in(ton, "PT", "#tFeedbackTime")
    n.open((ton, "ET"))
    nets.append(n)
    # 3. Авария с самоподхватом
    n = Net("Авария с самоподхватом")
    q = n.contact("rail", "#tonFeedback.Q")
    hold = n.contact("rail", "#xFault")
    br = n.orr(q, hold)
    n.coil(n.contact(br, "#xReset", neg=True), "#xFault")
    nets.append(n)
    # 4. Счётчик пусков по фронту
    n = Net("Счётчик пусков по фронту xRun")
    run = n.contact("rail", "#xRun")
    pbox = n.part("PBox")
    n.wire(run, (pbox, "in"))
    n.operand_in(pbox, "bit", "#xEdgeMem")
    add = n.part("Add", disabled_eno=True, templates=[("SrcType", "Type", "Int"), ("Card", "Cardinality", "2")])
    n.wire((pbox, "out"), (add, "en"))
    n.operand_in(add, "in1", "#iStarts")
    n.operand_in(add, "in2", "1")
    n.operand_out(add, "out", "#iStarts")
    nets.append(n)
    return Block(
        "FB",
        "FB_StarterLad",
        101,
        lang="LAD",
        title="Пускатель насоса (LAD)",
        comment=STARTER_DESCRIPTION,
        family="Drives",
        sections=starter_sections(),
        units=[lad_unit(x) for x in nets],
    )


# ---------------------------------------------------------------------------
# FB_Starter на FBD
# ---------------------------------------------------------------------------


def starter_fbd() -> Block:
    nets: list[Net] = []
    n = Net("Пуск/стоп: SR, сброс главнее", lang="FBD")
    s = n.gate("A", "#xStart", "#xInterlock")
    r = n.gate("O", "#xStop", "#xInterlock", "#xFault", negated=[2])
    sr = n.part("SR")
    n.wire(s, (sr, "s"))
    n.wire(r, (sr, "r1"))
    n.operand_in(sr, "operand", "#xRunMem")
    n.coil((sr, "q"), "#xRun")
    nets.append(n)
    n = Net("Контроль обратной связи", lang="FBD")
    rlo = n.gate("A", "#xRun", "#xFeedback", negated=[2])
    ton = n.part("TON", version="1.0", instance="#tonFeedback", templates=[("time_type", "Type", "Time")])
    n.wire(rlo, (ton, "IN"))
    n.operand_in(ton, "PT", "#tFeedbackTime")
    n.open((ton, "Q"))
    n.open((ton, "ET"))
    nets.append(n)
    n = Net("Авария с самоподхватом", lang="FBD")
    hold = n.gate("O", "#tonFeedback.Q", "#xFault")
    n.coil(n.gate("A", hold, "#xReset", negated=[2]), "#xFault")
    nets.append(n)
    n = Net("Счётчик пусков по фронту xRun", lang="FBD")
    pbox = n.part("PBox")
    n.operand_in(pbox, "in", "#xRun")
    n.operand_in(pbox, "bit", "#xEdgeMem")
    add = n.part("Add", disabled_eno=True, templates=[("SrcType", "Type", "Int"), ("Card", "Cardinality", "2")])
    n.wire((pbox, "out"), (add, "en"))
    n.operand_in(add, "in1", "#iStarts")
    n.operand_in(add, "in2", "1")
    n.operand_out(add, "out", "#iStarts")
    nets.append(n)
    return Block(
        "FB",
        "FB_StarterFbd",
        102,
        lang="FBD",
        title="Пускатель насоса (FBD)",
        comment=STARTER_DESCRIPTION,
        family="Drives",
        sections=starter_sections(),
        units=[lad_unit(x) for x in nets],
    )


# ---------------------------------------------------------------------------
# FB_Starter на STL
# ---------------------------------------------------------------------------


def starter_stl() -> Block:
    temps = [Member("xTonIn", "Bool", "Вход таймера"), Member("xTonQ", "Bool", "Выход таймера")]
    n1 = Stl("Пуск/стоп: SR, сброс главнее")
    n1.op("A", "#xStart").op("A", "#xInterlock").op("S", "#xRunMem")
    n1.op("A", "#xStop").op("ON", "#xInterlock").op("O", "#xFault").op("R", "#xRunMem")
    n1.op("A", "#xRunMem").op("Assign", "#xRun")
    n2 = Stl("Контроль обратной связи")
    n2.op("A", "#xRun").op("AN", "#xFeedback").op("Assign", "#xTonIn")
    n2.call_instruction(
        "TON",
        "#tonFeedback",
        [("time_type", "Type", "Time")],
        [
            ("IN", "Input", "Bool", "#xTonIn"),
            ("PT", "Input", "Time", "#tFeedbackTime"),
            ("Q", "Output", "Bool", "#xTonQ"),
            ("ET", "Output", "Time", None),
        ],
    )
    n3 = Stl("Авария с самоподхватом")
    n3.op("A_BRACK").op("O", "#xTonQ").op("O", "#xFault").op("BRACKET")
    n3.op("AN", "#xReset").op("Assign", "#xFault")
    n4 = Stl("Счётчик пусков по фронту xRun")
    n4.op("A", "#xRun").op("Rise", "#xEdgeMem").op("JCN", "label:M001")
    n4.op("L", "#iStarts").op("L", "1").op("ADD_I").op("T", "#iStarts")
    n4.op("NOP_0", label="M001")
    return Block(
        "FB",
        "FB_StarterStl",
        103,
        lang="STL",
        title="Пускатель насоса (STL)",
        comment=STARTER_DESCRIPTION,
        family="Drives",
        layout="Standard",
        sections=starter_sections(temps),
        units=[stl_unit(x) for x in (n1, n2, n3, n4)],
    )


# ---------------------------------------------------------------------------
# FB_Starter на SCL (SimaticML)
# ---------------------------------------------------------------------------

STARTER_SCL = """
// 1. SR с битом xRunMem: сначала S, затем R1 (сброс главнее)
IF #xStart AND #xInterlock THEN
    #xRunMem := TRUE;
END_IF;
IF #xStop OR NOT #xInterlock OR #xFault THEN
    #xRunMem := FALSE;
END_IF;
#xRun := #xRunMem;
// 2. Контроль обратной связи
#tonFeedback(IN := #xRun AND NOT #xFeedback, PT := #tFeedbackTime);
// 3. Авария с самоподхватом
#xFault := (#tonFeedback.Q OR #xFault) AND NOT #xReset;
// 4. Счётчик пусков по фронту xRun
IF #xRun AND NOT #xEdgeMem THEN
    #iStarts := #iStarts + 1;
END_IF;
#xEdgeMem := #xRun;
"""


def starter_scl() -> Block:
    scl = Scl("Пускатель", STARTER_SCL, "Логика пускателя целиком", instances={"#tonFeedback": "TON"})
    return Block(
        "FB",
        "FB_StarterScl",
        104,
        lang="SCL",
        title="Пускатель насоса (SCL)",
        comment=STARTER_DESCRIPTION,
        family="Drives",
        sections=starter_sections(),
        units=[scl_unit(scl)],
    )


# ---------------------------------------------------------------------------
# FB_PumpInterlockLad и FC_ClampPctLad
# ---------------------------------------------------------------------------

PUMP_DESCRIPTION = """Блокировки насоса II подъёма по уровню в РЧВ и давлению в коллекторе (LAD).
1. xLowLevel := iLevel_cm < iLevelMin_cm.  2. xHighPress := iPressure_kPa > iPressureMax_kPa.
3. Если xLowLevel OR xHighPress — установить xAlarmLatch (S).
4. Если xAck AND NOT xLowLevel AND NOT xHighPress — сбросить xAlarmLatch (R).
5. Обслуживание: при xMaint прыжок вперёд к метке NoAuto (сети 6-7 не выполняются).
6. xPumpOn := xAutoReq AND NOT xAlarmLatch.
7. По фронту xPumpOn (P_TRIG, бит xRunEdge): iRunCount := iRunCount + 1 (ADD Int); xCountOk := ENO сложения
   (ENO = 0 при переполнении Int: 32767 + 1).
8. Метка NoAuto: при xMaint сбросить xPumpOn (R).
9. При xPumpOn — цепочка трёх вызовов FC_ClampPctLad через EN/ENO: iStage1 := clamp(iLevel_cm, 0, 100);
   iStage2 := clamp(iStage1, 10, 90); iSetpoint_pct := clamp(iStage2, 20, 80); xChainOk := ENO третьего вызова.
10. При NOT xPumpOn: iSetpoint_pct := 0 (MOVE).
11. xAlarm := xAlarmLatch.  12. xRunMem := xRunEdge (бит памяти фронта читается в другой сети)."""


def pump_interlock_lad() -> Block:
    nets: list[Net] = []
    n = Net("Низкий уровень в РЧВ")
    lt = n.part("Lt", templates=[("SrcType", "Type", "Int")])
    n.wire("rail", (lt, "pre"))
    n.operand_in(lt, "in1", "#iLevel_cm")
    n.operand_in(lt, "in2", "#iLevelMin_cm")
    n.coil((lt, "out"), "#xLowLevel")
    nets.append(n)
    n = Net("Высокое давление в коллекторе")
    gt = n.part("Gt", templates=[("SrcType", "Type", "Int")])
    n.wire("rail", (gt, "pre"))
    n.operand_in(gt, "in1", "#iPressure_kPa")
    n.operand_in(gt, "in2", "#iPressureMax_kPa")
    n.coil((gt, "out"), "#xHighPress")
    nets.append(n)
    n = Net("Защёлка аварии: установка")
    n.coil(n.orr(n.contact("rail", "#xLowLevel"), n.contact("rail", "#xHighPress")), "#xAlarmLatch", "SCoil")
    nets.append(n)
    n = Net("Защёлка аварии: квитирование")
    ack = n.contact(n.contact(n.contact("rail", "#xAck"), "#xLowLevel", neg=True), "#xHighPress", neg=True)
    n.coil(ack, "#xAlarmLatch", "RCoil")
    nets.append(n)
    n = Net("Обслуживание: прыжок к NoAuto")
    jmp = n.part("Jump")
    n.wire(n.contact("rail", "#xMaint"), (jmp, "in"))
    n.operand_in(jmp, "operand", "label:NoAuto")
    nets.append(n)
    n = Net("Автоматический режим")
    n.coil(n.contact(n.contact("rail", "#xAutoReq"), "#xAlarmLatch", neg=True), "#xPumpOn")
    nets.append(n)
    n = Net("Счётчик включений с ENO")
    pbox = n.part("PBox")
    n.wire(n.contact("rail", "#xPumpOn"), (pbox, "in"))
    n.operand_in(pbox, "bit", "#xRunEdge")
    add = n.part("Add", templates=[("SrcType", "Type", "Int"), ("Card", "Cardinality", "2")])
    n.wire((pbox, "out"), (add, "en"))
    n.operand_in(add, "in1", "#iRunCount")
    n.operand_in(add, "in2", "1")
    n.operand_out(add, "out", "#iRunCount")
    n.coil((add, "eno"), "#xCountOk")
    nets.append(n)
    n = Net("Метка NoAuto: обслуживание выключает насос")
    n.labels.append("NoAuto")
    n.coil(n.contact("rail", "#xMaint"), "#xPumpOn", "RCoil")
    nets.append(n)
    n = Net("Уставка: три вызова FC_ClampPctLad через EN/ENO")
    params = [("iIn", "Input", "Int"), ("iMin", "Input", "Int"), ("iMax", "Input", "Int"), ("Ret_Val", "Return", "Int")]
    calls = []
    src: tuple[int, str] | str = n.contact("rail", "#xPumpOn")
    for k, (val, lo, hi, out) in enumerate(
        (
            ("#iLevel_cm", "0", "100", "#iStage1"),
            ("#iStage1", "10", "90", "#iStage2"),
            ("#iStage2", "20", "80", "#iSetpoint_pct"),
        ),
        start=1,
    ):
        call = n.part("Call", call={"name": "FC_ClampPctLad", "type": "FC", "params": params})
        calls.append(call)
        n.wire(src, (call, "en"))
        n.operand_in(call, "iIn", val)
        n.operand_in(call, "iMin", lo)
        n.operand_in(call, "iMax", hi)
        n.operand_out(call, "Ret_Val", out)
        src = (call, "eno")
        del k
    n.coil(src, "#xChainOk")
    nets.append(n)
    n = Net("Насос выключен: уставка 0")
    mv = n.part("Move", disabled_eno=True, templates=[("Card", "Cardinality", "1")])
    n.wire(n.contact("rail", "#xPumpOn", neg=True), (mv, "en"))
    n.operand_in(mv, "in", "0")
    n.operand_out(mv, "out1", "#iSetpoint_pct")
    nets.append(n)
    n = Net("Авария")
    n.coil(n.contact("rail", "#xAlarmLatch"), "#xAlarm")
    nets.append(n)
    n = Net("Бит памяти фронта в другой сети")
    n.coil(n.contact("rail", "#xRunEdge"), "#xRunMem")
    nets.append(n)
    sections = [
        Section(
            "Input",
            [
                Member("xAutoReq", "Bool", "Запрос автоматики на работу"),
                Member("iLevel_cm", "Int", "Уровень в РЧВ, см"),
                Member("iLevelMin_cm", "Int", "Минимальный уровень, см", start="50"),
                Member("iPressure_kPa", "Int", "Давление в коллекторе, кПа"),
                Member("iPressureMax_kPa", "Int", "Максимальное давление, кПа", start="600"),
                Member("xAck", "Bool", "Квитирование аварии"),
                Member("xMaint", "Bool", "Режим обслуживания"),
            ],
        ),
        Section(
            "Output",
            [
                Member("xPumpOn", "Bool", "Команда насосу"),
                Member("xLowLevel", "Bool", "Низкий уровень"),
                Member("xHighPress", "Bool", "Высокое давление"),
                Member("xAlarm", "Bool", "Авария (защёлка)"),
                Member("iRunCount", "Int", "Число включений"),
                Member("xCountOk", "Bool", "ENO сложения: нет переполнения"),
                Member("iSetpoint_pct", "Int", "Уставка производительности, %"),
                Member("xChainOk", "Bool", "ENO цепочки вызовов"),
                Member("xRunMem", "Bool", "Копия бита памяти фронта"),
            ],
        ),
        Section("InOut"),
        Section(
            "Static",
            [
                Member("xAlarmLatch", "Bool", "Защёлка аварии"),
                Member("xRunEdge", "Bool", "Бит памяти фронта xPumpOn"),
                Member("iStage1", "Int", "Уставка после первого ограничения"),
                Member("iStage2", "Int", "Уставка после второго ограничения"),
            ],
        ),
        Section("Temp"),
        Section("Constant"),
    ]
    return Block(
        "FB",
        "FB_PumpInterlockLad",
        110,
        lang="LAD",
        title="Блокировки насоса по уровню и давлению (LAD)",
        comment=PUMP_DESCRIPTION,
        family="Drives",
        sections=sections,
        units=[lad_unit(x) for x in nets],
    )


def clamp_pct_lad() -> Block:
    nets: list[Net] = []
    n = Net("Значение по умолчанию")
    mv = n.part("Move", disabled_eno=True, templates=[("Card", "Cardinality", "1")])
    n.wire("rail", (mv, "en"))
    n.operand_in(mv, "in", "#iIn")
    n.operand_out(mv, "out1", "#Ret_Val")
    nets.append(n)
    n = Net("Выше максимума")
    gt = n.part("Gt", templates=[("SrcType", "Type", "Int")])
    n.wire("rail", (gt, "pre"))
    n.operand_in(gt, "in1", "#iIn")
    n.operand_in(gt, "in2", "#iMax")
    mv = n.part("Move", disabled_eno=True, templates=[("Card", "Cardinality", "1")])
    n.wire((gt, "out"), (mv, "en"))
    n.operand_in(mv, "in", "#iMax")
    n.operand_out(mv, "out1", "#Ret_Val")
    nets.append(n)
    n = Net("Ниже минимума")
    lt = n.part("Lt", templates=[("SrcType", "Type", "Int")])
    n.wire("rail", (lt, "pre"))
    n.operand_in(lt, "in1", "#iIn")
    n.operand_in(lt, "in2", "#iMin")
    mv = n.part("Move", disabled_eno=True, templates=[("Card", "Cardinality", "1")])
    n.wire((lt, "out"), (mv, "en"))
    n.operand_in(mv, "in", "#iMin")
    n.operand_out(mv, "out1", "#Ret_Val")
    nets.append(n)
    sections = [
        Section(
            "Input",
            [
                Member("iIn", "Int", "Значение"),
                Member("iMin", "Int", "Нижний предел"),
                Member("iMax", "Int", "Верхний предел"),
            ],
        ),
        Section("Output"),
        Section("InOut"),
        Section("Temp"),
        Section("Constant"),
        Section("Return", [Member("Ret_Val", "Int")]),
    ]
    return Block(
        "FC",
        "FC_ClampPctLad",
        111,
        lang="LAD",
        title="Ограничение значения пределами (LAD)",
        comment="Результат: iIn, ограниченный снизу iMin и сверху iMax (сначала верхний предел, затем нижний). "
        "ENO не пишется: ENO = EN.",
        family="Utils",
        sections=sections,
        units=[lad_unit(x) for x in nets],
    )


# ---------------------------------------------------------------------------
# DB_Process и UDT_Valve
# ---------------------------------------------------------------------------


def udt_valve() -> Block:
    return Block(
        "PlcStruct",
        "UDT_Valve",
        0,
        title="Задвижка",
        comment="Состояние задвижки для HMI и STL",
        sections=[
            Section(
                "None",
                [
                    Member("xOpen", "Bool", "Открыта"),
                    Member("xClosed", "Bool", "Закрыта"),
                    Member("iPos_pct", "Int", "Положение, %"),
                ],
            )
        ],
    )


def db_process() -> Block:
    return Block(
        "GlobalDB",
        "DB_Process",
        20,
        title="Технологические данные (стандартный доступ)",
        comment="Неоптимизированный DB: STL S7-300 адресует члены по смещению (Offset)",
        layout="Standard",
        family="Plant",
        sections=[
            Section(
                "Static",
                [
                    Member("xPumpRun", "Bool", "Насос в работе", offset=0),
                    Member("iLevel_cm", "Int", "Уровень, см", offset=2),
                    Member("rFlow_m3h", "Real", "Расход, м3/ч", offset=4),
                    Member("wStatus", "Word", "Слово состояния", offset=8),
                    Member("stValve", '"UDT_Valve"', "Задвижка напорная", offset=10),
                    Member("iBatch", "Int", "Номер партии", start="1", retain=True, offset=14),
                ],
            )
        ],
    )


def all_blocks(tia: str = "V21") -> list[Block]:
    del tia  # пространства имён подставляет build_xml.render
    return [
        starter_lad(),
        starter_fbd(),
        starter_stl(),
        starter_scl(),
        pump_interlock_lad(),
        clamp_pct_lad(),
        udt_valve(),
        db_process(),
    ]


__all__ = ["STARTER_DESCRIPTION", "STARTER_SCL", "Unit", "all_blocks"]
