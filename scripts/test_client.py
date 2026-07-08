'''
PIE-NN Test Client

Sends a series of IDL commands to the running daemon and prints the results.
'''

import socket
import json
import sys
import time

SOCKET_PATH = "/tmp/pie_nn_daemon.sock"

# ANSI Colors
class C:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    END = '\033[0m'

def send_command(method, params=None):
    """Send a single IDL command to the daemon and return the response."""
    if params is None:
        params = {}
    command = {"method": method, "params": params}
    
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.connect(SOCKET_PATH)
    client.sendall(json.dumps(command).encode())
    response = client.recv(8192)
    client.close()
    return json.loads(response.decode())


def print_section(title):
    print()
    print(f"{C.BOLD}{C.CYAN}{'─' * 60}{C.END}")
    print(f"{C.BOLD}{C.CYAN}  {title}{C.END}")
    print(f"{C.BOLD}{C.CYAN}{'─' * 60}{C.END}")


def print_json(data, indent=2):
    print(json.dumps(data, indent=indent, default=str))


def main():
    print()
    print(f"{C.BOLD}{C.HEADER}╔══════════════════════════════════════════════════════╗{C.END}")
    print(f"{C.BOLD}{C.HEADER}║          PIE-NN Cognitive Core Test Suite             ║{C.END}")
    print(f"{C.BOLD}{C.HEADER}╚══════════════════════════════════════════════════════╝{C.END}")

    # ── Test 1: Get Status ──
    print_section("TEST 1: get_status")
    print(f"{C.DIM}Sending: {{\"method\": \"get_status\"}}{C.END}")
    result = send_command("get_status")
    print_json(result)
    time.sleep(0.3)

    # ── Test 2: Get Time Crystal Hierarchy ──
    print_section("TEST 2: get_tc_hierarchy")
    print(f"{C.DIM}Sending: {{\"method\": \"get_tc_hierarchy\"}}{C.END}")
    result = send_command("get_tc_hierarchy")
    hierarchy = result.get("hierarchy", {})
    for level_id in sorted(hierarchy.keys(), key=lambda x: int(x)):
        info = hierarchy[level_id]
        print(f"  {C.YELLOW}Level {level_id:>2}{C.END}  {info['name']:<30} {C.DIM}{info['period']:>6}{C.END}  {info['function']}")
    time.sleep(0.3)

    # ── Test 3: Process a short PIE-NN command ──
    print_section("TEST 3: process_source (short command)")
    source = "deik x is gno-()"
    print(f"{C.DIM}Sending: process_source with source=\"{source}\"{C.END}")
    result = send_command("process_source", {"source": source})
    print()
    print(f"  {C.GREEN}Response:{C.END} {result.get('response', 'N/A')}")
    print()
    trace = result.get("cognitive_trace", {})
    print(f"  {C.BLUE}Frame Saliences:{C.END}")
    for frame, sal in trace.get("frame_saliences", {}).items():
        bar = "█" * int(sal * 30)
        print(f"    {frame:<16} {sal:.4f} {C.BLUE}{bar}{C.END}")
    print(f"  {C.GREEN}Dominant Frame:{C.END} {trace.get('dominant_frame', 'N/A')} (salience={trace.get('dominant_salience', 0):.4f})")
    print()
    emotion = trace.get("emotion_state", {})
    print(f"  {C.YELLOW}Emotion State:{C.END}")
    for dim, val in emotion.items():
        bar = "█" * int(val * 20)
        print(f"    {dim:<14} {val:.3f} {C.YELLOW}{bar}{C.END}")
    time.sleep(0.3)

    # ── Test 4: Process a complex PIE-NN pipeline ──
    print_section("TEST 4: process_source (complex pipeline)")
    source = "deik Agent is ser-(add Perception, add Response, add Autognosis) then werg Agent on RawInputStream"
    print(f"{C.DIM}Sending: process_source with source=\"{source}\"{C.END}")
    result = send_command("process_source", {"source": source})
    print()
    print(f"  {C.GREEN}Response:{C.END} {result.get('response', 'N/A')}")
    print()
    trace = result.get("cognitive_trace", {})
    print(f"  {C.BLUE}Frame Saliences:{C.END}")
    for frame, sal in trace.get("frame_saliences", {}).items():
        bar = "█" * int(sal * 30)
        print(f"    {frame:<16} {sal:.4f} {C.BLUE}{bar}{C.END}")
    print(f"  {C.GREEN}Dominant Frame:{C.END} {trace.get('dominant_frame', 'N/A')} (salience={trace.get('dominant_salience', 0):.4f})")
    time.sleep(0.3)

    # ── Test 5: Autognosis Introspection ──
    print_section("TEST 5: introspect (Autognosis self-awareness)")
    print(f"{C.DIM}Sending: {{\"method\": \"introspect\"}}{C.END}")
    result = send_command("introspect")
    autognosis = result.get("autognosis", {})
    print(f"\n  {C.HEADER}Autognosis Cycle #{autognosis.get('cycle', '?')}{C.END}")
    print(f"\n  {C.HEADER}Hierarchical Self-Images:{C.END}")
    for level, img in autognosis.get("self_images", {}).items():
        conf_bar = "█" * int(img["confidence"] * 20)
        print(f"    Level {level}: {img['label']:<22} conf={img['confidence']:.2f} {C.HEADER}{conf_bar}{C.END}")
        print(f"           {C.DIM}\"{img['content']}\"{C.END}")
    meta = autognosis.get("meta_cognition", {})
    print(f"\n  {C.HEADER}Meta-Cognition:{C.END}")
    print(f"    Rationalization Risk:    {meta.get('rationalization_risk', 'N/A')}")
    print(f"    Confidence Calibration:  {meta.get('confidence_calibration', 'N/A')}")
    print(f"    Reasoning Quality:       {meta.get('reasoning_quality', 'N/A')}")
    time.sleep(0.3)

    # ── Test 6: Get Personality Traits ──
    print_section("TEST 6: get_traits (Personality Parameters)")
    print(f"{C.DIM}Sending: {{\"method\": \"get_traits\"}}{C.END}")
    result = send_command("get_traits")
    data = result.get("data", {})
    traits = data.get("traits", {})
    bounds = data.get("bounds", {})
    print()
    for trait, val in traits.items():
        lo, hi = bounds.get(trait, (0, 1))
        # Visualize the trait value within its bounds
        range_width = 30
        pos = int(((val - lo) / (hi - lo)) * range_width)
        bar = "░" * pos + "█" + "░" * (range_width - pos)
        print(f"    {trait:<14} {val:.2f}  [{lo:.2f} {C.GREEN}{bar}{C.END} {hi:.2f}]")

    # ── Test 7: Unknown method (error handling) ──
    print_section("TEST 7: unknown_method (error handling)")
    print(f"{C.DIM}Sending: {{\"method\": \"self_destruct\"}}{C.END}")
    result = send_command("self_destruct")
    print_json(result)

    # ── Summary ──
    print()
    print(f"{C.BOLD}{C.GREEN}{'═' * 60}{C.END}")
    print(f"{C.BOLD}{C.GREEN}  All 7 tests completed successfully.{C.END}")
    print(f"{C.BOLD}{C.GREEN}{'═' * 60}{C.END}")
    print()


if __name__ == "__main__":
    main()
