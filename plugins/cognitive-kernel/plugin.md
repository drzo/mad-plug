---
name: cognitive-kernel
description: >
  Build and operate cognitive development kernels — Plan 9, Inferno-OS, and OpenCog-based
  systems for distributed inference, process management, and self-aware computation.
  Includes cluster configuration, monitoring, and daemon management.
tools:
  - scripts/cognitive_devkernel.py
  - scripts/cognitive_plan9kernel.py
  - scripts/distributed_inference.py
  - scripts/configure_cluster.py
  - scripts/cluster_monitor.py
  - scripts/run_daemon.sh
  - scripts/pie_nn_daemon.py
  - scripts/test_daemon.py
resources:
  - deep-tree-echo-core-self/
  - AUTOGNOSIS/
---

# Cognitive Kernel Plugin

Provides tools for building and operating cognitive development kernels —
systems that combine OS-level primitives with AI inference capabilities.

## Capabilities

- **Build kernels** — Plan 9 and Inferno-OS cognitive development environments
- **Distributed inference** — Configure and run multi-node inference clusters
- **Cluster management** — Configure, monitor, and operate compute clusters
- **Daemon operations** — Start, test, and manage cognitive service daemons
- **Self-aware computation** — Deep Tree Echo and Autognosis frameworks

## Usage

Invoke when the user asks about:
- Cognitive architecture setup ("configure a cognitive kernel")
- Distributed AI ("set up distributed inference across nodes")
- Cluster operations ("monitor my cluster", "configure workers")
- Daemon management ("start the PIE-NN daemon", "test the service")
- Self-referential systems ("implement deep tree echo", "autognosis")

## Related Frameworks

- `deep-tree-echo-core-self/` — Core self-referential cognitive framework
- `AUTOGNOSIS/` — Self-awareness and introspection system
