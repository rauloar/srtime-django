"""
Integration test for Flexible Processor Phase 1 & 2
Run: python -m core.domain.flexible.test_integration
"""
from datetime import datetime, timedelta

from core.domain.flexible.types import Punch, FlexPolicy
from core.domain.flexible.work_block import WorkBlock
from core.domain.flexible.parsing import validate_punches, build_work_blocks
from core.domain.flexible.gaps import analyze_gaps
from core.domain.flexible.structure import apply_structural_splits, resolve_attribution


def test_phase1_phase2():
    """Full integration test."""
    print("=" * 60)
    print("FLEXIBLE PROCESSOR - PHASE 1 & 2 TEST")
    print("=" * 60)
    
    # Create test data (use past date to avoid future timestamp validation)
    base = datetime(2025, 1, 15, 8, 0, 0)  # 08:00 on a past date
    punches = [
        Punch(1, base, "DEV1"),                           # 08:00 IN
        Punch(2, base + timedelta(hours=4), "DEV1"),      # 12:00 OUT
        Punch(3, base + timedelta(hours=5), "DEV1"),      # 13:00 IN
        Punch(4, base + timedelta(hours=9), "DEV1"),      # 17:00 OUT
    ]
    
    print(f"\nInput: {len(punches)} punches")
    for p in punches:
        print(f"  {p.timestamp.strftime('%H:%M')} - Punch #{p.id}")
    
    # Phase 1: Validation
    print("\n--- PHASE 1: VALIDATION ---")
    warnings = validate_punches(punches)
    print(f"Validation warnings: {warnings if warnings else 'None'}")
    assert len(warnings) == 0, "Unexpected validation warnings"
    print("✓ Validation passed")
    
    # Phase 1: Build blocks
    print("\n--- PHASE 1: BUILD BLOCKS ---")
    blocks, parse_warnings = build_work_blocks(punches)
    print(f"Blocks created: {len(blocks)}")
    for b in blocks:
        if b.is_complete:
            print(f"  Block: {b.start_time.strftime('%H:%M')}-{b.end_time.strftime('%H:%M')} = {b.duration_minutes}min")
        else:
            print(f"  Block: {b.start_time.strftime('%H:%M')}-? (incomplete)")
    print(f"Parse warnings: {parse_warnings if parse_warnings else 'None'}")
    assert len(blocks) == 2, f"Expected 2 blocks, got {len(blocks)}"
    assert blocks[0].duration_minutes == 240, f"Expected 240min, got {blocks[0].duration_minutes}"
    print("✓ Block building passed")
    
    # Phase 2: Gap analysis
    print("\n--- PHASE 2: GAP ANALYSIS ---")
    policy = FlexPolicy()
    gap_result = analyze_gaps(blocks, policy)
    print(f"Gaps found: {gap_result.gap_count}")
    for g in gap_result.gaps:
        print(f"  Gap: {g.start.strftime('%H:%M')}-{g.end.strftime('%H:%M')} = {g.duration_minutes}min")
    print(f"Total gap time: {gap_result.total_gap_minutes}min")
    assert gap_result.gap_count == 1, f"Expected 1 gap, got {gap_result.gap_count}"
    assert gap_result.total_gap_minutes == 60, f"Expected 60min gap, got {gap_result.total_gap_minutes}"
    print("✓ Gap analysis passed")
    
    # Phase 2: Attribution
    print("\n--- PHASE 2: ATTRIBUTION ---")
    attributed = resolve_attribution(blocks)
    for b in attributed:
        print(f"  Block attributed to: {b.attribution_date}")
    assert all(b.attribution_date == base.date() for b in attributed)
    print("✓ Attribution passed")
    
    # Test overnight split
    print("\n--- PHASE 2: OVERNIGHT SPLIT ---")
    overnight_punches = [
        Punch(10, datetime(2025, 1, 15, 22, 0, 0), "DEV1"),  # 22:00
        Punch(11, datetime(2025, 1, 16, 6, 0, 0), "DEV1"),    # 06:00 next day
    ]
    overnight_blocks, _ = build_work_blocks(overnight_punches)
    assert overnight_blocks[0].is_overnight, "Expected overnight block"
    print(f"  Overnight block: {overnight_blocks[0].duration_minutes}min")
    
    policy_split = FlexPolicy(force_midnight_split=True)
    split_blocks, split_warnings = apply_structural_splits(overnight_blocks, policy_split)
    print(f"  After split: {len(split_blocks)} blocks")
    for b in split_blocks:
        print(f"    {b.start_time.strftime('%Y-%m-%d %H:%M')}-{b.end_time.strftime('%H:%M')} = {b.duration_minutes}min")
    assert len(split_blocks) == 2, f"Expected 2 split blocks, got {len(split_blocks)}"
    print("✓ Overnight split passed")
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED ✓")
    print("=" * 60)


if __name__ == "__main__":
    test_phase1_phase2()
