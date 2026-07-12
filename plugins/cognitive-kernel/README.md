# cognitive-kernel

Build and operate cognitive development kernels based on Plan 9, Inferno-OS, and OpenCog architectures with distributed inference and daemon management.

**Version:** 0.1.0 | **Category:** Cognitive Computing | **Tags:** `kernel` `plan9` `distributed` `inference` `opencog`

---

## Description

`cognitive-kernel` provides tooling for constructing and running AI/cognitive computing infrastructure. Build kernel variants (Plan 9 namespace-based or Inferno-OS limbo-based), configure distributed inference pipelines across compute nodes, manage cluster topology, and operate the PIE-NN cognitive service daemon that exposes JSON-RPC endpoints for cognitive modules.

---

## Tools

| Tool | Description | Required Parameters |
|---|---|---|
| `cogkernel_build` | Build a cognitive kernel (Plan 9 or Inferno-OS) | `type` |
| `cogkernel_distributed_inference` | Configure/run distributed inference across nodes | `command` |
| `cogkernel_cluster` | Configure and monitor compute clusters | `action` |
| `cogkernel_daemon` | Manage cognitive service daemons (PIE-NN) | `action` |

### `cogkernel_build` types
- `plan9` — Plan 9 namespace-based kernel
- `inferno` — Inferno-OS limbo-based kernel

### `cogkernel_distributed_inference` commands
- `setup` — Configure inference pipeline
- `run` — Start distributed inference
- `status` — Check inference status
- `stop` — Stop inference

### `cogkernel_cluster` actions
- `init` — Initialize cluster from project config
- `validate` — Validate cluster configuration
- `status` — Report cluster status
- `monitor` — Continuous cluster monitoring

### `cogkernel_daemon` actions
- `start` — Start the PIE-NN daemon
- `test` — Run functional tests against the running daemon
- `status` — Check daemon health via JSON-RPC

---

## Usage Examples

### Build a Plan 9 cognitive kernel
```
cogkernel_build(type="plan9", config="configs/plan9-default.yaml")
```

### Set up distributed inference across two nodes
```
cogkernel_distributed_inference(command="setup", nodes="192.168.1.10,192.168.1.11", model="opencog-pln")
```

### Initialize a compute cluster
```
cogkernel_cluster(action="init", config="projects/my-cog-system")
```
Reads cluster configuration from the project directory and provisions compute nodes.

### Start and verify the PIE-NN daemon
```
cogkernel_daemon(action="start", socket="/tmp/pie_nn.sock")
cogkernel_daemon(action="status", socket="/tmp/pie_nn.sock")
```

---

## Dependencies

None

---

## Scripts

Python scripts in `scripts/`:
- `cognitive_plan9kernel.py` — Plan 9 kernel builder
- `cognitive_devkernel.py` — Inferno-OS kernel builder
- `distributed_inference.py` — distributed inference configuration
- `configure_cluster.py` — cluster initialization and validation
- `cluster_monitor.py` — continuous cluster monitoring
- `test_daemon.py` — PIE-NN daemon functional tests
- `run_daemon.sh` — daemon startup script
