---
name: scm-des
description: Build discrete event simulations for supply chain management using CogSim PML. Use for modeling multi-actor supply chains, simulating material flows, analyzing bottlenecks, capacity planning, and optimizing logistics networks with suppliers, producers, distributors, wholesalers, and retailers.
---

# Supply Chain Discrete Event Simulation

Build process-centric simulations for supply chain networks using CogSim PML.

## Prerequisites

Run cogsim setup before first use:
```bash
python /home/ubuntu/skills/cogsim-pml/scripts/setup_cogsim.py
```

## Workflow

### 1. Define Supply Chain Topology

Map the wodog actor model to simulation entities:

| SCM Actor | Simulation Role | PML Blocks |
|-----------|-----------------|------------|
| Supplier | Material source | `Source` + entity customization |
| Producer | Processing stage | `ResourceTask`, `Service` |
| Distributor | Transport/routing | `Delay`, `SelectOutput` |
| Wholesaler | Batching/storage | `Queue`, `Batch` |
| Retailer | Demand sink | `Sink` with metrics |
| Marketplace | Multi-routing | `SelectOutput5`, `Combine` |

### 2. Model Relationships as Flow Connections

```python
# Relationship types map to connection patterns:
# supplies       → Source >> Producer
# produces_for   → Producer >> Distributor  
# distributes_to → Distributor >> Wholesaler/Retailer
# sells_to       → Retailer >> Sink (customer)
```

### 3. Create Simulation from SCM Data

```python
import sys
sys.path.insert(0, '/home/ubuntu/cogsim')
import json

from cogsim import (
    SimulationEngine, Source, Sink, Queue, Delay, Service,
    ResourcePool, ResourceTask, Seize, Release,
    SelectOutput, SelectionMode, Combine, Batch, Unbatch,
    ArrivalMode, RandomVariate
)

# Load SCM topology
with open('actors.json') as f:
    actors = json.load(f)
with open('relationships.json') as f:
    relationships = json.load(f)

engine = SimulationEngine(seed=42)
rv = RandomVariate(seed=42)
```

### 4. Build Actor Blocks

**Supplier as Source:**
```python
def create_supplier_source(actor, engine, rv):
    """Create source block from supplier actor."""
    storage = next((c for c in actor['capacities'] if c['type'] == 'storage'), None)
    rate = storage['value'] / 480 if storage else 1.0
    
    source = Source(
        actor['id'],
        arrival_mode=ArrivalMode.RATE,
        rate=rate,
        entity_type=actor['rawMaterialTypes'][0] if actor.get('rawMaterialTypes') else 'material',
        engine=engine
    )
    
    def customize(entity):
        entity.attributes['supplier_id'] = actor['id']
        entity.attributes['material_type'] = rv.choice(actor.get('rawMaterialTypes', ['generic']))
        rule = actor['pricingRules'][0] if actor.get('pricingRules') else None
        if rule and rule['type'] == 'tiered':
            entity.attributes['unit_cost'] = rule['tiers'][0]['price']
        elif rule and rule['type'] == 'fixed':
            entity.attributes['unit_cost'] = rule.get('basePrice', 0)
    
    source.set_entity_customizer(customize)
    return source
```

**Producer as ResourceTask:**
```python
def create_producer_task(actor, engine, rv):
    """Create processing task from producer actor."""
    capacity = actor.get('productionCapacity', 100)
    pool = ResourcePool(f"{actor['id']}_capacity", capacity=max(1, capacity // 100), engine=engine)
    task = ResourceTask(
        actor['id'],
        resource_pool=pool,
        task_time=lambda: rv.triangular(2.0, 8.0, 4.0),
        quantity=1,
        engine=engine
    )
    return task, pool
```

**Distributor as Delay:**
```python
def create_distributor(actor, engine, rv):
    """Create transport delay from distributor actor."""
    coverage = len(actor.get('coverageArea', []))
    base_time = 1.0 + coverage * 0.5
    delay = Delay(
        actor['id'],
        delay_time=lambda: rv.triangular(base_time, base_time * 3, base_time * 1.5),
        capacity=max(1, actor.get('transportCapacity', 10000) // 1000),
        engine=engine
    )
    return delay
```

### 5. Connect by Relationships

```python
def build_supply_chain(actors, relationships, engine, rv):
    """Build simulation from SCM topology."""
    blocks = {}
    pools = {}
    
    for actor in actors:
        if actor['type'] == 'supplier':
            blocks[actor['id']] = create_supplier_source(actor, engine, rv)
        elif actor['type'] == 'producer':
            task, pool = create_producer_task(actor, engine, rv)
            blocks[actor['id']] = task
            pools[actor['id']] = pool
        elif actor['type'] == 'distributor':
            blocks[actor['id']] = create_distributor(actor, engine, rv)
        elif actor['type'] == 'retailer':
            blocks[actor['id']] = Sink(actor['id'], engine=engine)
    
    for rel in relationships:
        if rel['status'] != 'active':
            continue
        from_block = blocks.get(rel['fromActorId'])
        to_block = blocks.get(rel['toActorId'])
        if from_block and to_block:
            from_block >> to_block
    
    return blocks, pools
```

### 6. Run and Analyze

```python
blocks, pools = build_supply_chain(actors, relationships, engine, rv)
engine.run(until=480)

for actor_id, block in blocks.items():
    stats = block.get_statistics()
    print(f"{actor_id}: {stats}")
```

## SCM-Specific Patterns

### Multi-Supplier Sourcing
```python
combine = Combine("supplier_merge", num_inputs=len(suppliers), engine=engine)
for i, supplier in enumerate(suppliers):
    supplier_source >> combine.get_input_port(f"in_{i}")
combine >> producer_task
```

### Tiered Distribution
```python
def route_by_size(entity):
    return entity.attributes.get('quantity', 0) >= 100

router = SelectOutput("tier_router", mode=SelectionMode.CONDITION, 
                      condition=route_by_size, engine=engine)
producer >> router
router.get_output_port("out_true").connect(wholesaler.get_input_port("in"))
router.get_output_port("out_false").connect(retailer.get_input_port("in"))
```

### Cooperative Pooling
```python
def create_coop_pool(coop_members, engine):
    """Shared resource pool for cooperative members."""
    total_capacity = sum(m.get('productionCapacity', 0) for m in coop_members)
    return ResourcePool("coop_pool", capacity=max(1, total_capacity // 100), engine=engine)
```

### Inventory Buffering
```python
batch = Batch("wholesale_batch", batch_size=10, timeout=60.0, engine=engine)
unbatch = Unbatch("retail_unbatch", engine=engine)
distributor >> batch >> wholesaler_storage >> unbatch >> retailer
```

## Key Metrics

| Metric | SCM Interpretation | Collection |
|--------|-------------------|------------|
| Throughput | Units delivered | `sink.count()` |
| Lead Time | Order-to-delivery | `sink.get_statistics()['average_time_in_system']` |
| Utilization | Capacity usage | `pool.get_statistics()['average_utilization']` |
| Queue Length | Backlog/WIP | `queue.get_statistics()['average_queue_length']` |
| Bullwhip | Demand amplification | Compare source rate to sink rate |

## References

- SCM topology patterns: `references/scm_patterns.md`
- Full simulation template: `templates/scm_simulation.py`
- Actor-to-block mapping: `references/actor_mapping.md`
