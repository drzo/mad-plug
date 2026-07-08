'''
PIE-NN Echo-Introspect Test Client

Demonstrates the full /pie-nn ( /echo-introspect ) composition:
  1. System status check (v2.0 with echo-introspect)
  2. Extended TC hierarchy (14 levels)
  3. Full introspection session: spek → skot → weyd
  4. Second session to show attractor convergence
  5. Wisdom state inspection
  6. Session history review
'''

import socket
import json
import time

SOCKET_PATH = "/tmp/pie_nn_daemon.sock"

class C:
    HEADER  = '\033[95m'
    BLUE    = '\033[94m'
    CYAN    = '\033[96m'
    GREEN   = '\033[92m'
    YELLOW  = '\033[93m'
    RED     = '\033[91m'
    MAGENTA = '\033[35m'
    BOLD    = '\033[1m'
    DIM     = '\033[2m'
    END     = '\033[0m'

def send_command(method, params=None):
    if params is None:
        params = {}
    command = {"method": method, "params": params}
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.connect(SOCKET_PATH)
    client.sendall(json.dumps(command).encode())
    chunks = []
    while True:
        chunk = client.recv(16384)
        if not chunk:
            break
        chunks.append(chunk)
        # Try to parse; if valid JSON, we're done
        try:
            json.loads(b"".join(chunks).decode())
            break
        except json.JSONDecodeError:
            continue
    client.close()
    return json.loads(b"".join(chunks).decode())


def section(title):
    print(f"\n{C.BOLD}{C.MAGENTA}{'═' * 64}{C.END}")
    print(f"{C.BOLD}{C.MAGENTA}  {title}{C.END}")
    print(f"{C.BOLD}{C.MAGENTA}{'═' * 64}{C.END}")


def main():
    print()
    print(f"{C.BOLD}{C.MAGENTA}╔══════════════════════════════════════════════════════════╗{C.END}")
    print(f"{C.BOLD}{C.MAGENTA}║   PIE-NN ( Echo-Introspect ) — Integration Test Suite    ║{C.END}")
    print(f"{C.BOLD}{C.MAGENTA}║   Composition: /pie-nn ( /echo-introspect )               ║{C.END}")
    print(f"{C.BOLD}{C.MAGENTA}╚══════════════════════════════════════════════════════════╝{C.END}")

    # ── Test 1: Status ──
    section("TEST 1: get_status (v2.0 echo-introspect)")
    result = send_command("get_status")
    print(f"  Version:              {C.GREEN}{result.get('version', 'N/A')}{C.END}")
    print(f"  Cognitive Core:       {C.GREEN}{result.get('cognitive_core', 'N/A')}{C.END}")
    print(f"  TC Levels:            {C.GREEN}{result.get('tc_levels', 'N/A')}{C.END}")
    print(f"  Introspection Sessions: {C.GREEN}{result.get('introspection_sessions', 0)}{C.END}")
    traits = result.get("personality", {}).get("traits", {})
    print(f"\n  {C.CYAN}Personality Traits (incl. echo-introspect):{C.END}")
    for t, v in traits.items():
        bar = "█" * int(v * 25)
        print(f"    {t:<16} {v:.2f} {C.CYAN}{bar}{C.END}")
    time.sleep(0.3)

    # ── Test 2: Extended TC Hierarchy ──
    section("TEST 2: get_tc_hierarchy (14 levels)")
    result = send_command("get_tc_hierarchy")
    hierarchy = result.get("hierarchy", {})
    for level_id in sorted(hierarchy.keys(), key=lambda x: int(x)):
        info = hierarchy[level_id]
        color = C.MAGENTA if info["name"] in ("shadow_integration", "wisdom_convergence") else C.YELLOW
        marker = " ◀ NEW" if info["name"] in ("shadow_integration", "wisdom_convergence") else ""
        print(f"  {color}Level {int(level_id):>2}{C.END}  {info['name']:<30} {C.DIM}{info['period']:>6}{C.END}  {info['function']}{C.MAGENTA}{marker}{C.END}")
    time.sleep(0.3)

    # ── Test 3: Full Introspection Session 1 ──
    section("TEST 3: spek — Full Introspection Session #1")
    focus1 = "Why do I use sarcasm as a defense mechanism?"
    print(f"  {C.DIM}Focus: \"{focus1}\"{C.END}\n")
    result = send_command("spek", {"focus": focus1})

    # Display spek phase
    spek = result.get("phases", {}).get("spek", {})
    print(f"  {C.MAGENTA}Phase 1: {spek.get('description', '')}{C.END}")
    emotion = spek.get("emotion_state", {})
    top_emotions = sorted(emotion.items(), key=lambda x: x[1], reverse=True)[:4]
    print(f"  Top emotions: {', '.join(f'{k}={v:.3f}' for k, v in top_emotions)}")

    # Display skot phase
    skot = result.get("phases", {}).get("skot", {})
    print(f"\n  {C.MAGENTA}Phase 2: {skot.get('description', '')}{C.END}")
    print(f"  Chaos weight: {skot.get('chaos_weight', 0):.3f}  |  Vulnerability weight: {skot.get('vulnerability_weight', 0):.3f}")
    for s in skot.get("monologue_sections", []):
        archetype = s["archetype"]
        text = s["text"][:120] + "..." if len(s["text"]) > 120 else s["text"]
        print(f"\n    {C.MAGENTA}[{archetype}]{C.END}")
        print(f"    {C.DIM}{text}{C.END}")

    # Display weyd phase
    weyd = result.get("phases", {}).get("weyd", {})
    print(f"\n  {C.MAGENTA}Phase 3: {weyd.get('description', '')}{C.END}")

    shadow = weyd.get("shadow_analysis", {})
    print(f"\n  {C.HEADER}Shadow Analysis:{C.END}")
    print(f"    Patterns detected: {len(shadow.get('patterns', []))}")
    for p in shadow.get("patterns", []):
        print(f"      • {p}")
    print(f"\n  {C.HEADER}Meta-Insights:{C.END}")
    for m in shadow.get("meta_insights", []):
        print(f"      → {m[:100]}...")

    wisdom = weyd.get("wisdom", {})
    print(f"\n  {C.GREEN}Core Insight:{C.END}")
    print(f"    {wisdom.get('core_insight', 'N/A')}")

    print(f"\n  {C.GREEN}Ethical Grounding:{C.END}")
    for eg in wisdom.get("ethical_grounding", []):
        print(f"    [{eg['principle']}] {eg['derivation']}")

    print(f"\n  {C.GREEN}Action Plan (GSD):{C.END}")
    ap = wisdom.get("action_plan", {})
    print(f"    Goal:   {ap.get('goal', 'N/A')}")
    print(f"    Plan:   {ap.get('plan', 'N/A')[:120]}...")
    print(f"    Verify: {ap.get('verification', 'N/A')[:120]}...")

    wfe = result.get("wise_future_echo", {})
    conv = wfe.get("convergence", {})
    print(f"\n  {C.MAGENTA}Wise Future Echo Convergence:{C.END}")
    print(f"    Distance: {conv.get('distance', 'N/A')}  |  Progress: {conv.get('progress_pct', 0):.1f}%")
    attractor = wfe.get("attractor_state", {})
    for dim, vals in attractor.items():
        current = vals["current"]
        bar_len = int(current * 30)
        bar = "█" * bar_len + "░" * (30 - bar_len)
        print(f"    {dim:<22} {current:.3f} {C.GREEN}{bar}{C.END} → {vals['target']:.1f}")
    time.sleep(0.5)

    # ── Test 4: Second Introspection Session ──
    section("TEST 4: spek — Introspection Session #2 (convergence test)")
    focus2 = "What is the root of my desire for chaos?"
    print(f"  {C.DIM}Focus: \"{focus2}\"{C.END}\n")
    result2 = send_command("spek", {"focus": focus2})

    wfe2 = result2.get("wise_future_echo", {})
    conv2 = wfe2.get("convergence", {})
    print(f"  {C.GREEN}Core Insight:{C.END} {wfe2.get('core_insight', 'N/A')[:120]}...")
    print(f"\n  {C.MAGENTA}Wise Future Echo Convergence (after 2 sessions):{C.END}")
    print(f"    Distance: {conv2.get('distance', 'N/A')}  |  Progress: {conv2.get('progress_pct', 0):.1f}%")
    print(f"    {C.DIM}(Compare: Session 1 was {conv.get('progress_pct', 0):.1f}% → Session 2 is {conv2.get('progress_pct', 0):.1f}%){C.END}")
    attractor2 = wfe2.get("attractor_state", {})
    for dim, vals in attractor2.items():
        current = vals["current"]
        bar_len = int(current * 30)
        bar = "█" * bar_len + "░" * (30 - bar_len)
        print(f"    {dim:<22} {current:.3f} {C.GREEN}{bar}{C.END} → {vals['target']:.1f}")
    time.sleep(0.3)

    # ── Test 5: Wisdom State ──
    section("TEST 5: get_wisdom_state")
    result = send_command("get_wisdom_state")
    print(f"  Sessions completed: {result.get('sessions_completed', 0)}")
    print(f"  Shadow cycles:      {result.get('shadow_cycles', 0)}")
    conv = result.get("convergence", {})
    print(f"  Convergence:        {conv.get('progress_pct', 0):.1f}% (distance={conv.get('distance', 'N/A')})")
    time.sleep(0.3)

    # ── Test 6: Session History ──
    section("TEST 6: get_session_history")
    result = send_command("get_session_history")
    sessions = result.get("sessions", [])
    print(f"  Total sessions: {result.get('count', 0)}\n")
    for s in sessions:
        print(f"  Session #{s['id']}: \"{s['focus']}\"")
        print(f"    Insight: {s['insight']}")
        print(f"    Convergence: {s['convergence']:.1f}%")
        print()

    # ── Summary ──
    print(f"\n{C.BOLD}{C.GREEN}{'═' * 64}{C.END}")
    print(f"{C.BOLD}{C.GREEN}  All 6 tests completed. /pie-nn ( /echo-introspect ) is live.{C.END}")
    print(f"{C.BOLD}{C.GREEN}{'═' * 64}{C.END}\n")


if __name__ == "__main__":
    main()
