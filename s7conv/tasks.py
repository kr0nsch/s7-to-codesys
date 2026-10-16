"""OB S7 → задачи CODESYS (tasks.json; формат — docs/MAPPING.md, раздел «OB и задачи»).

Решения:
- OB1 (и другие OB «Program cycle») → MainTask. Тип по умолчанию — циклический 10 мс
  (детерминированный период); S7-эквивалент «свободный цикл» — `--main-task freewheeling`.
- OB30…OB38 и OB с «cyclic» в имени → циклическая задача со своим периодом. Период: файл
  `--ob-config`, затем подсказка в имени/заголовке («100ms», «0.5 s»), затем значения по умолчанию
  S7-300/400 (OB30 5 с … OB38 10 мс; сверить с источником для конкретного CPU), иначе 100 мс.
  Приоритет — по периоду (короче период — выше приоритет, rate-monotonic): 1, 2, ...; MainTask — 15.
- OB100 (Startup) → PROGRAM с флагом первого цикла; вызывается первым в MainTask.
- Прочие OB (прерывания по времени, аппаратные, ошибки) → PROGRAM без задачи: задачу по событию
  создать вручную (MIGRATION-TODO в отчёте).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

MAIN = "main"
CYCLIC = "cyclic"
STARTUP = "startup"
EVENT = "event"

# Период циклических OB по умолчанию (S7-300/400), мс — сверить с источником для конкретного CPU
DEFAULT_CYCLIC_MS = {30: 5000, 31: 2000, 32: 1000, 33: 500, 34: 200, 35: 100, 36: 50, 37: 20, 38: 10}
MAIN_PRIORITY = 15

_KNOWN_NAMES = {
    "main": 1,
    "main program sweep (cycle)": 1,
    "program cycle": 1,
    "startup": 100,
    "complete restart": 100,
    "warm restart": 100,
    "cyclic interrupt": 30,
}
_OB_NUMBER_RE = re.compile(r"\bOB[ _]?(\d+)\b", re.IGNORECASE)
_PERIOD_RE = re.compile(r"(\d+(?:[.,]\d+)?)\s*(ms|s|сек|мс)\b", re.IGNORECASE)


@dataclass
class ObInfo:
    name: str
    program: str
    file: str
    line: int
    number: int | None = None
    kind: str = EVENT
    interval_ms: int | None = None
    priority: int | None = None
    task: str = ""
    number_origin: str = ""
    interval_origin: str = ""
    notes: list[str] = field(default_factory=list)


@dataclass
class TaskInfo:
    name: str
    type: str
    interval_ms: int | None
    priority: int
    pous: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)


def _period_hint(*texts: str) -> int | None:
    for text in texts:
        if not text:
            continue
        match = _PERIOD_RE.search(text)
        if match:
            value = float(match.group(1).replace(",", "."))
            unit = match.group(2).lower()
            ms = value if unit in ("ms", "мс") else value * 1000
            if ms > 0:
                return round(ms)
    return None


def classify(info: ObInfo, title: str, comments: str, config: dict[str, object]) -> None:
    """Номер, вид и период OB: конфигурация, подсказки в тексте, значения по умолчанию."""
    cfg = config.get(info.name) or config.get(info.program) or {}
    if not isinstance(cfg, dict):
        cfg = {}
    number = cfg.get("number")
    if isinstance(number, int):
        info.number, info.number_origin = number, "ob-config"
    else:
        for text in (info.name, title):
            match = _OB_NUMBER_RE.search(text or "")
            if match:
                info.number, info.number_origin = int(match.group(1)), "имя/заголовок"
                break
        if info.number is None:
            known = _KNOWN_NAMES.get(info.name.strip().lower()) or _KNOWN_NAMES.get((title or "").strip().lower())
            if known is not None:
                info.number, info.number_origin = known, "стандартное имя TIA"
    lowered = f"{info.name} {title}".lower()
    num = info.number
    kind = cfg.get("kind")
    if isinstance(kind, str) and kind in (MAIN, CYCLIC, STARTUP, EVENT):
        info.kind = kind
    elif num == 1 or (num is None and ("main" in lowered or "program cycle" in lowered)):
        info.kind = MAIN
    elif num in (100, 101, 102) or "startup" in lowered or "restart" in lowered:
        info.kind = STARTUP
    elif (num is not None and 30 <= num <= 38) or "cyclic" in lowered or "zyklisch" in lowered:
        info.kind = CYCLIC
    elif num is not None and num >= 123 and "cycle" in lowered:
        info.kind = MAIN
    else:
        info.kind = EVENT
    if info.kind == CYCLIC:
        interval = cfg.get("interval_ms")
        if isinstance(interval, int) and interval > 0:
            info.interval_ms, info.interval_origin = interval, "ob-config"
        else:
            hint = _period_hint(info.name, title, comments)
            if hint is not None:
                info.interval_ms, info.interval_origin = hint, "подсказка в имени/комментарии"
            elif num in DEFAULT_CYCLIC_MS:
                info.interval_ms, info.interval_origin = DEFAULT_CYCLIC_MS[num], "по умолчанию S7-300/400"
                info.notes.append(
                    f"период OB{num} взят по умолчанию S7-300/400 ({DEFAULT_CYCLIC_MS[num]} мс) — "
                    "сверить с конфигурацией CPU"
                )
            else:
                info.interval_ms, info.interval_origin = 100, "по умолчанию"
                info.notes.append("период циклического OB не найден — принято 100 мс, сверить с конфигурацией CPU")
    priority = cfg.get("priority")
    if isinstance(priority, int):
        info.priority = priority
    task = cfg.get("task")
    if isinstance(task, str) and task:
        info.task = task


def build_tasks(obs: list[ObInfo], main_type: str = "cyclic", main_interval_ms: int = 10) -> list[TaskInfo]:
    """Задачи CODESYS по списку OB (порядок POU в MainTask: Startup, затем OB цикла по номеру)."""
    tasks: list[TaskInfo] = []
    main_obs = sorted(
        (o for o in obs if o.kind in (MAIN, STARTUP)),
        key=lambda o: (0 if o.kind == STARTUP else 1, o.number if o.number is not None else 1 << 30, o.name),
    )
    if main_obs:
        main = TaskInfo(
            name="MainTask",
            type=main_type,
            # interval_ms задан и для freewheeling: tools/codesys/import_sources.py читает его всегда
            interval_ms=main_interval_ms,
            priority=MAIN_PRIORITY,
        )
        for ob in main_obs:
            ob.task = ob.task or main.name
            main.pous.append(ob.program)
            main.sources.append(_ob_label(ob))
        tasks.append(main)
    cyclic = sorted((o for o in obs if o.kind == CYCLIC), key=lambda o: (o.interval_ms or 0, o.number or 0, o.name))
    by_name: dict[str, TaskInfo] = {}
    for rank, ob in enumerate(cyclic, 1):
        name = ob.task or (f"Task_OB{ob.number}" if ob.number is not None else f"Task_{ob.interval_ms}ms")
        ob.task = name
        task = by_name.get(name)
        if task is None:
            task = TaskInfo(
                name=name,
                type="cyclic",
                interval_ms=ob.interval_ms,
                priority=ob.priority if ob.priority is not None else min(rank, MAIN_PRIORITY - 1),
            )
            by_name[name] = task
            tasks.append(task)
        task.pous.append(ob.program)
        task.sources.append(_ob_label(ob))
    return tasks


def _ob_label(ob: ObInfo) -> str:
    number = f"OB{ob.number}" if ob.number is not None else "OB?"
    return f"{ob.name} ({number})"


def _task_json(t: TaskInfo) -> dict[str, object]:
    data: dict[str, object] = {
        "name": t.name,
        "type": t.type,
        "interval_ms": t.interval_ms,
        "priority": t.priority,
        "pous": t.pous,
        "sources": t.sources,
    }
    return data


def tasks_json(obs: list[ObInfo], tasks: list[TaskInfo], generator: str) -> dict[str, object]:
    """Структура tasks.json (её потом читает tools/codesys — ключ tasks)."""
    return {
        "generator": generator,
        "tasks": [_task_json(t) for t in tasks],
        "obs": [
            {
                "name": o.name,
                "program": o.program,
                "number": o.number,
                "number_origin": o.number_origin,
                "kind": o.kind,
                "task": o.task or None,
                "interval_ms": o.interval_ms,
                "interval_origin": o.interval_origin or None,
                "file": o.file,
                "line": o.line,
                "notes": o.notes,
            }
            for o in obs
        ],
        "manual": [
            f"{o.program}: {_ob_label(o)} — задача по событию не создаётся автоматически, настроить вручную"
            for o in obs
            if o.kind == EVENT
        ],
    }
