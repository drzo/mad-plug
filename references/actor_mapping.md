# Actor-to-Block Mapping Reference

## Wodog Actor Types → CogSim PML Blocks

### Supplier (𝑆)

**Role**: Provides raw materials to producers

**Wodog Schema**:
```json
{
  "id": "s1",
  "type": "supplier",
  "capacities": [{"type": "storage", "value": 10000, "unit": "kg"}],
  "pricingRules": [...],
  "rawMaterialTypes": ["steel", "aluminum"]
}
```

**PML Mapping**:
```python
# Primary: Source block (generates material entities)
source = Source(
    name=actor['id'],
    arrival_mode=ArrivalMode.RATE,
    rate=calculate_rate(actor),
    entity_type=actor['rawMaterialTypes'][0],
    engine=engine
)

# Optional: Queue for storage buffer
buffer = Queue(
    name=f"{actor['id']}_buffer",
    capacity=actor['capacities'][0]['value'] // batch_size,
    engine=engine
)
```

**Key Attributes to Entity**:
- `supplier_id`: Actor ID
- `material_type`: From rawMaterialTypes
- `unit_cost`: From pricingRules

---

### Producer (𝑃)

**Role**: Transforms raw materials into products

**Wodog Schema**:
```json
{
  "id": "p1",
  "type": "producer",
  "productionCapacity": 1000,
  "productTypes": ["electronics", "appliances"],
  "capacities": [{"type": "production", "value": 1000, "unit": "units/day"}]
}
```

**PML Mapping**:
```python
# ResourcePool for production capacity
pool = ResourcePool(
    name=f"{actor['id']}_machines",
    capacity=actor['productionCapacity'] // 100,
    engine=engine
)

# ResourceTask for production process
task = ResourceTask(
    name=actor['id'],
    resource_pool=pool,
    task_time=lambda: rv.triangular(2.0, 8.0, 4.0),
    quantity=1,
    engine=engine
)

# Alternative: Seize-Delay-Release for finer control
seize = Seize(f"{actor['id']}_seize", resource_pool=pool, engine=engine)
process = Delay(f"{actor['id']}_process", delay_time=production_time, engine=engine)
release = Release(f"{actor['id']}_release", resource_pool=pool, engine=engine)
```

**Key Attributes to Entity**:
- `producer_id`: Actor ID
- `product_type`: From productTypes
- `production_cost`: Accumulated cost

---

### Distributor (𝐷)

**Role**: Transports goods between supply chain stages

**Wodog Schema**:
```json
{
  "id": "d1",
  "type": "distributor",
  "transportCapacity": 20000,
  "coverageArea": ["North America", "Europe"]
}
```

**PML Mapping**:
```python
# Delay for transport time
transport = Delay(
    name=actor['id'],
    delay_time=lambda: rv.triangular(
        base_time(actor),
        base_time(actor) * 3,
        base_time(actor) * 1.5
    ),
    capacity=actor['transportCapacity'] // 1000,
    engine=engine
)

# Optional: SelectOutput for geographic routing
router = SelectOutput(
    name=f"{actor['id']}_router",
    mode=SelectionMode.CONDITION,
    condition=lambda e: e.attributes.get('destination') in actor['coverageArea'],
    engine=engine
)
```

**Key Attributes to Entity**:
- `distributor_id`: Actor ID
- `transport_cost`: From pricingRules
- `destination`: Target region

---

### Wholesaler (𝑊)

**Role**: Bulk storage and distribution

**Wodog Schema**:
```json
{
  "id": "w1",
  "type": "wholesaler",
  "warehouseCapacity": 50000,
  "minimumOrderQuantity": 100
}
```

**PML Mapping**:
```python
# Queue for warehouse storage
warehouse = Queue(
    name=f"{actor['id']}_warehouse",
    capacity=actor['warehouseCapacity'] // avg_item_size,
    engine=engine
)

# Batch for order consolidation
batch = Batch(
    name=f"{actor['id']}_batch",
    batch_size=actor['minimumOrderQuantity'],
    timeout=max_wait_time,
    engine=engine
)

# Service for order processing
order_processing = Service(
    name=f"{actor['id']}_orders",
    service_time=lambda: rv.uniform(1.0, 3.0),
    capacity=num_order_processors,
    engine=engine
)
```

**Key Attributes to Entity**:
- `wholesaler_id`: Actor ID
- `batch_id`: Batch identifier
- `order_quantity`: Items in batch

---

### Retailer (𝑅)

**Role**: Sells to end consumers

**Wodog Schema**:
```json
{
  "id": "r1",
  "type": "retailer",
  "storefront": "both",
  "serviceArea": ["North America"],
  "capacities": [{"type": "shelf_space", "value": 500, "unit": "sqm"}]
}
```

**PML Mapping**:
```python
# Service for customer transactions
retail_service = Service(
    name=actor['id'],
    service_time=lambda: rv.exponential(checkout_time),
    capacity=num_registers,
    engine=engine
)

# Sink for completed sales
sales_sink = Sink(
    name=f"{actor['id']}_sales",
    engine=engine
)

# Optional: SelectOutput for channel routing (online vs physical)
if actor['storefront'] == 'both':
    channel_router = SelectOutput(
        name=f"{actor['id']}_channel",
        mode=SelectionMode.PROBABILITY,
        probability=online_ratio,
        engine=engine
    )
```

**Key Attributes to Entity**:
- `retailer_id`: Actor ID
- `sale_price`: With markup applied
- `channel`: 'online' or 'physical'

---

### Marketplace (𝑀)

**Role**: Multi-vendor platform

**Wodog Schema**:
```json
{
  "id": "m1",
  "type": "marketplace",
  "platform": "online",
  "commission": 15,
  "vendorCount": 50
}
```

**PML Mapping**:
```python
# Combine for multi-vendor input
vendor_combine = Combine(
    name=f"{actor['id']}_vendors",
    num_inputs=actor['vendorCount'],
    engine=engine
)

# SelectOutput5 for vendor routing
vendor_router = SelectOutput5(
    name=f"{actor['id']}_router",
    num_outputs=min(5, actor['vendorCount']),
    mode=SelectionMode.PROBABILITY,
    probabilities=vendor_weights,
    engine=engine
)

# Service for platform processing
platform = Service(
    name=actor['id'],
    service_time=lambda: rv.uniform(0.1, 0.5),  # Fast platform
    capacity=platform_capacity,
    engine=engine
)
```

**Key Attributes to Entity**:
- `marketplace_id`: Actor ID
- `vendor_id`: Selected vendor
- `commission`: Platform fee

---

## Relationship Type → Connection Pattern

| Relationship | Connection Code |
|--------------|-----------------|
| `supplies` | `supplier_source >> producer_queue` |
| `produces_for` | `producer_task >> distributor_delay` |
| `distributes_to` | `distributor_delay >> wholesaler_queue` or `retailer_service` |
| `sells_to` | `retailer_service >> customer_sink` |
| `partners_with` | Shared `ResourcePool` reference |
| `competes_with` | Parallel paths to same downstream block |

## Cooperative Membership → Shared Resources

```python
def create_cooperative_resources(actors, coop_id, engine):
    """Create shared resources for cooperative members."""
    members = [a for a in actors 
               if any(m['cooperativeId'] == coop_id 
                      for m in a.get('cooperativeMemberships', []))]
    
    # Aggregate capacity
    total_capacity = sum(
        sum(c['value'] for c in a.get('capacities', []))
        for a in members
    )
    
    return ResourcePool(
        name=f"coop_{coop_id}_shared",
        capacity=max(1, total_capacity // 100),
        engine=engine
    )
```
