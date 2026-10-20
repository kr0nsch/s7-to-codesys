#!/usr/bin/env python3
"""Вторая матрица покрытия: правило перевода языков S7 (M3 LAD/FBD, M4 STL) → тесты, которые его проверяют.

Первая матрица (coverage_matrix.py) описывает корпус SCL. Эта привязывает каждое правило словаря элементов
LAD/FBD (s7conv/lower/net_to_ast.py, PARTS) и каждое правило токенов STL класса auto/check
(s7conv/lower/stl_tokens.py, TOKENS) к тестам pytest по имени. Тест samples/test_rules_matrix.py падает,
если у правила выпуска нет теста или тест с таким именем не найден.

    python samples/rules_matrix.py    # напечатать матрицу Markdown
"""

from __future__ import annotations

import sys

# правило → тесты (имена функций pytest); P1 — правила следующего выпуска, тест не обязателен
RULE_TESTS: dict[str, tuple[str, ...]] = {
    # M3: LAD/FBD
    "contact": ("test_series_and_branches_give_and_or", "test_random_lad_networks_match_power_flow"),
    "coil": ("test_series_and_branches_give_and_or", "test_set_reset_coils_and_negated_coil"),
    "set_reset": ("test_set_reset_coils_and_negated_coil",),
    "sr_operand": (
        "test_flipflop_with_operand_keeps_s7_order",
        "test_old_flipflop_mapping_breaks_starter_scenario",
        "test_old_sr_mapping_mutation_is_caught",
    ),
    "edge": ("test_pbox_uses_explicit_memory_bit",),
    "edge_memory": ("test_edge_memory_in_temp_is_flagged",),
    "compare": ("test_compare_with_pre_and_move_with_en",),
    "move": ("test_compare_with_pre_and_move_with_en",),
    "math": ("test_add_with_connected_eno_uses_s7compat_before_write",),
    "eno_error": ("test_add_with_connected_eno_uses_s7compat_before_write", "test_eno_mutation_is_caught"),
    "div_zero": ("test_external_samples_convert_with_expected_outcome",),
    "convert": ("test_external_samples_convert_with_expected_outcome",),
    "instruction": ("test_limit_counter_return_and_calculate_boxes",),
    "calculate": ("test_limit_counter_return_and_calculate_boxes",),
    "timer": ("test_language_corpus_suites_pass_in_simulation", "test_document_header_interface_and_units"),
    "counter": ("test_limit_counter_return_and_calculate_boxes",),
    "call": ("test_call_chain_eno_equals_en_for_plain_lad_callee",),
    "call_eno": ("test_call_chain_eno_equals_en_for_plain_lad_callee",),
    "jump": ("test_forward_jump_over_networks_becomes_if",),
    "return": ("test_limit_counter_return_and_calculate_boxes",),
    "unknown_part": ("test_unknown_part_is_todo_with_uid",),
    "wire": ("test_corrupted_xml_never_crashes",),
    "vocab_unverified": ("test_unverified_vocabulary_is_at_most_check",),
    "graph_condition": (
        "test_graph_condition_coils_become_st_assignments",
        "test_twin_and_reference_agree_on_scenarios_and_random_calls",
    ),
    # M4: STL
    "stl.logic": ("test_stl_and_before_or_and_brackets", "test_random_stl_chains_match_machine"),
    "stl.edge": ("test_stl_fp_jcn_label_becomes_if_without_jmp",),
    "stl.edge_memory": ("test_stl_edge_memory_in_temp_is_flagged",),
    "s5.timebase": (
        "test_stl_s5_timers_lower_to_s7compat_calls",
        "test_stl_s5_all_start_kinds_and_word_preset",
        "test_reference_s5_timer_matches_awlsim",
    ),
    "s5.timer": ("test_stl_s5_timers_lower_to_s7compat_calls", "test_stl_s5_read_before_write_is_frozen"),
    "s5.counter": ("test_stl_s5_counters_lower_to_s7compat_calls", "test_reference_s5_counter_matches_awlsim"),
    "stl.accu": ("test_stl_load_transfer_and_int_arithmetic", "test_zero_extension_mutation_is_caught"),
    "stl.math": ("test_stl_load_transfer_and_int_arithmetic", "test_stl_dint_real_arithmetic_and_compare"),
    "stl.compare": ("test_stl_compare_is_first_check", "test_stl_dint_real_arithmetic_and_compare"),
    "stl.call": (
        "test_language_corpus_suites_pass_in_simulation",
        "test_external_samples_convert_with_expected_outcome",
    ),
    "stl.jump_structured": ("test_stl_fp_jcn_label_becomes_if_without_jmp", "test_stl_if_else_pattern"),
    "stl.jump_pc": ("test_stl_pc_mode_is_case_in_while", "test_stl_backward_jump_falls_back_to_pc"),
    "stl.zero_extend": ("test_stl_zero_extension_is_check", "test_zero_extension_mutation_is_caught"),
    "stl.accu_high": ("test_stl_int_arithmetic_on_dint_reads_low_word_only",),
    "stl.block_end": ("test_stl_block_end_instructions",),
    "stl.nop": ("test_language_corpus_suites_pass_in_simulation",),
    "stl.mode_b": ("test_stl_mode_b_instructions_are_todo_until_p1",),
}
# Правила, проверка которых — в следующем выпуске (P1): перечислены, чтобы матрица была полной
P1_RULES = frozenset({"jump_irreducible", "instance", "stl.call_registers_1500"})


def lad_rules() -> list[str]:
    from s7conv.lower.net_to_ast import PARTS

    return sorted({p.rule for p in PARTS.values()} | {"edge_memory", "eno_error", "div_zero", "call_eno", "wire"})


def stl_rules() -> list[str]:
    from s7conv.lower.stl_tokens import TOKENS

    return sorted({t.rule for t in TOKENS.values() if t.cls in ("auto", "check")} | {"stl.zero_extend", "stl.jump_pc"})


def render() -> str:
    lines = ["| Правило | Тесты |", "|---|---|"]
    for rule in [*lad_rules(), *stl_rules()]:
        tests = RULE_TESTS.get(rule, ())
        lines.append(f"| `{rule}` | {', '.join(f'`{t}`' for t in tests) or 'P1'} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    sys.stdout.write(render())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
