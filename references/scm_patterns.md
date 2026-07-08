# SCM Topology Patterns

## Network Structures

### Linear Chain
```
Supplier → Producer → Distributor → Retailer → Customer
```
Simplest topology. Use for single-product, single-channel flows.

### Convergent (Many-to-One)
```
Supplier₁ ↘
Supplier₂ → Producer → Distributor
Supplier₃ ↗
```
Multiple suppliers feeding one producer. Use `Combine` block.

### Divergent (One-to-Many)
```
              → Wholesaler₁
Producer → Distributor → Wholesaler₂
              → Retailer₁
```
One producer serving multiple channels. Use `SelectOutput5` or `Split`.

### Network (Many-to-Many)
```
S₁ → P₁ → D₁ → R₁
  ↘   ↗    ↘   ↗
S₂ → P₂ → D₂ → R₂
```
Full mesh with cross-connections. Requires explicit routing logic.

## Relationship Type Mappings

| Relationship | From Actor | To Actor | PML Pattern |
|--------------|-----------|----------|-------------|
| supplies | Supplier | Producer | `Source >> Queue >> ResourceTask` |
| produces_for | Producer | Distributor | `ResourceTask >> Delay` |
| distributes_to | Distributor | Wholesaler/Retailer | `Delay >> SelectOutput` |
| sells_to | Retailer | Customer | `Service >> Sink` |
| partners_with | Any | Any | Shared `ResourcePool` |
| competes_with | Any | Any | Parallel paths to same `Sink` |

## Capacity Modeling

### Storage Capacity (Suppliers)
```python
# Maps to Source rate and Queue capacity
storage_kg = actor['capacities'][0]['value']  # e.g., 10000 kg
arrival_rate = storage_kg / simulation_time   # kg per minute
queue_capacity = storage_kg / avg_batch_size  # buffer slots
```

### Production Capacity (Producers)
```python
# Maps to ResourcePool and task parallelism
units_per_day = actor['productionCapacity']   # e.g., 1000
pool_capacity = units_per_day // 100          # parallel workers/machines
task_time = 480 / units_per_day               # minutes per unit
```

### Transport Capacity (Distributors)
```python
# Maps to Delay capacity
transport_kg = actor['transportCapacity']     # e.g., 20000 kg
concurrent_shipments = transport_kg // 1000   # parallel capacity
```

## Pricing Rule Integration

### Fixed Pricing
```python
def apply_fixed_pricing(entity, rule):
    entity.attributes['cost'] = rule['basePrice'] * entity.attributes.get('quantity', 1)
```

### Tiered Pricing
```python
def apply_tiered_pricing(entity, rule):
    qty = entity.attributes.get('quantity', 1)
    for tier in rule['tiers']:
        if tier['minQuantity'] <= qty <= tier.get('maxQuantity', float('inf')):
            entity.attributes['cost'] = tier['price'] * qty
            break
```

### Percentage Markup
```python
def apply_markup(entity, rule):
    base_cost = entity.attributes.get('cost', 0)
    entity.attributes['cost'] = base_cost * (1 + rule['percentage'] / 100)
```

## Cooperative Structures

### Primary Cooperative (Natural Persons)
```python
# Individual actors pooling resources
coop_members = [a for a in actors if 'coop1' in [m['cooperativeId'] for m in a.get('cooperativeMemberships', [])]]
shared_pool = ResourcePool("coop_shared", capacity=sum_capacities(coop_members), engine=engine)
```

### Secondary Cooperative (Primary Coops)
```python
# Federations of primary cooperatives
# Model as hierarchical resource pools
```

### Tertiary Cooperative (Secondary Coops)
```python
# National/international federations
# Model as aggregate capacity constraints
```

## Common Simulation Scenarios

### Demand Surge
```python
# Increase arrival rate mid-simulation
def demand_surge(engine, source, multiplier, start_time, duration):
    original_rate = source.rate
    engine.schedule(start_time, lambda: setattr(source, 'rate', original_rate * multiplier))
    engine.schedule(start_time + duration, lambda: setattr(source, 'rate', original_rate))
```

### Supply Disruption
```python
# Temporarily disable a supplier
def supply_disruption(engine, source, start_time, duration):
    engine.schedule(start_time, lambda: setattr(source, 'rate', 0))
    engine.schedule(start_time + duration, lambda: setattr(source, 'rate', source.original_rate))
```

### Capacity Expansion
```python
# Add capacity to a resource pool
def expand_capacity(engine, pool, additional, start_time):
    engine.schedule(start_time, lambda: pool.set_capacity(pool.capacity + additional))
```

## Bullwhip Effect Analysis

The bullwhip effect amplifies demand variability upstream. Measure by comparing variance ratios:

```python
def bullwhip_ratio(source_stats, sink_stats):
    """Calculate bullwhip amplification factor."""
    source_var = source_stats.get('arrival_variance', 0)
    sink_var = sink_stats.get('departure_variance', 0)
    return source_var / sink_var if sink_var > 0 else float('inf')
```

Mitigation strategies:
1. **Information sharing**: Reduce lead times
2. **Vendor-managed inventory**: Centralize demand visibility
3. **Smaller batches**: Reduce `Batch` size
4. **Stable pricing**: Avoid promotional demand spikes
