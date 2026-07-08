"""
Supply Chain Discrete Event Simulation Template

This template demonstrates building a complete supply chain simulation
from wodog actor/relationship JSON data using CogSim PML.

Usage:
1. Place actors.json and relationships.json in working directory
2. Run: python scm_simulation.py
3. Modify parameters in SimulationConfig for scenarios
"""

import sys
sys.path.insert(0, '/home/ubuntu/cogsim')

import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path

from cogsim import (
    SimulationEngine, Source, Sink, Queue, Delay, Service,
    ResourcePool, ResourceTask, Seize, Release,
    SelectOutput, SelectionMode, Combine, Batch, Unbatch,
    ArrivalMode, RandomVariate
)


# ============================================================================
# CONFIGURATION
# ============================================================================

@dataclass
class SimulationConfig:
    """Supply chain simulation parameters."""
    # Time parameters
    simulation_time: float = 480.0  # 8-hour shift (minutes)
    warmup_time: float = 60.0       # Warmup period
    
    # Scaling factors
    time_scale: float = 1.0         # Speed up/slow down
    capacity_scale: float = 1.0     # Scale all capacities
    
    # Stochastic parameters
    seed: int = 42
    
    # File paths
    actors_file: str = "actors.json"
    relationships_file: str = "relationships.json"
    
    # Analysis options
    verbose: bool = True
    collect_entity_history: bool = False


# ============================================================================
# ACTOR BLOCK BUILDERS
# ============================================================================

class ActorBlockBuilder:
    """Builds PML blocks from wodog actor definitions."""
    
    def __init__(self, engine: SimulationEngine, rv: RandomVariate, config: SimulationConfig):
        self.engine = engine
        self.rv = rv
        self.config = config
        self.blocks: Dict[str, Any] = {}
        self.pools: Dict[str, ResourcePool] = {}
        self.queues: Dict[str, Queue] = {}
    
    def build_supplier(self, actor: Dict) -> Source:
        """Create Source block from supplier actor."""
        # Calculate arrival rate from storage capacity
        storage = next(
            (c for c in actor.get('capacities', []) if c['type'] == 'storage'),
            {'value': 1000}
        )
        rate = (storage['value'] / self.config.simulation_time) * self.config.capacity_scale
        
        # Determine entity type
        materials = actor.get('rawMaterialTypes', ['material'])
        
        source = Source(
            name=actor['id'],
            arrival_mode=ArrivalMode.RATE,
            rate=rate,
            entity_type=materials[0] if materials else 'material',
            engine=self.engine
        )
        
        # Entity customization with pricing
        pricing_rules = actor.get('pricingRules', [])
        
        def customize(entity):
            entity.attributes['supplier_id'] = actor['id']
            entity.attributes['material_type'] = self.rv.choice(materials) if materials else 'generic'
            entity.attributes['origin_time'] = self.engine.current_time
            
            # Apply first pricing rule
            if pricing_rules:
                rule = pricing_rules[0]
                if rule['type'] == 'tiered' and rule.get('tiers'):
                    entity.attributes['unit_cost'] = rule['tiers'][0]['price']
                elif rule['type'] == 'fixed':
                    entity.attributes['unit_cost'] = rule.get('basePrice', 0)
                else:
                    entity.attributes['unit_cost'] = 0
            else:
                entity.attributes['unit_cost'] = 0
        
        source.set_entity_customizer(customize)
        self.blocks[actor['id']] = source
        return source
    
    def build_producer(self, actor: Dict) -> Tuple[ResourceTask, ResourcePool]:
        """Create ResourceTask and pool from producer actor."""
        # Production capacity determines parallelism
        capacity = actor.get('productionCapacity', 100)
        pool_size = max(1, int(capacity * self.config.capacity_scale / 100))
        
        pool = ResourcePool(
            name=f"{actor['id']}_capacity",
            capacity=pool_size,
            engine=self.engine
        )
        self.pools[actor['id']] = pool
        
        # Production time inversely related to capacity
        base_time = 480 / capacity if capacity > 0 else 5.0
        
        task = ResourceTask(
            name=actor['id'],
            resource_pool=pool,
            task_time=lambda bt=base_time: self.rv.triangular(
                bt * 0.5 * self.config.time_scale,
                bt * 2.0 * self.config.time_scale,
                bt * self.config.time_scale
            ),
            quantity=1,
            engine=self.engine
        )
        
        self.blocks[actor['id']] = task
        return task, pool
    
    def build_distributor(self, actor: Dict) -> Delay:
        """Create Delay block from distributor actor."""
        # Transport capacity determines parallelism
        transport_cap = actor.get('transportCapacity', 10000)
        capacity = max(1, int(transport_cap * self.config.capacity_scale / 1000))
        
        # Coverage area affects transport time
        coverage = len(actor.get('coverageArea', []))
        base_time = (1.0 + coverage * 0.5) * self.config.time_scale
        
        delay = Delay(
            name=actor['id'],
            delay_time=lambda bt=base_time: self.rv.triangular(bt, bt * 3, bt * 1.5),
            capacity=capacity,
            engine=self.engine
        )
        
        self.blocks[actor['id']] = delay
        return delay
    
    def build_wholesaler(self, actor: Dict) -> Queue:
        """Create Queue block from wholesaler actor."""
        warehouse_cap = actor.get('warehouseCapacity', 10000)
        capacity = max(10, int(warehouse_cap * self.config.capacity_scale / 100))
        
        queue = Queue(
            name=actor['id'],
            capacity=capacity,
            engine=self.engine
        )
        
        self.blocks[actor['id']] = queue
        self.queues[actor['id']] = queue
        return queue
    
    def build_retailer(self, actor: Dict) -> Sink:
        """Create Sink block from retailer actor."""
        sink = Sink(
            name=actor['id'],
            engine=self.engine
        )
        
        # Track sales metrics
        def on_sale(entity):
            entity.attributes['retailer_id'] = actor['id']
            entity.attributes['sale_time'] = self.engine.current_time
            
            # Apply markup pricing
            for rule in actor.get('pricingRules', []):
                if rule['type'] == 'percentage':
                    base_cost = entity.attributes.get('unit_cost', 0)
                    entity.attributes['sale_price'] = base_cost * (1 + rule['percentage'] / 100)
                    break
        
        sink.on_enter(on_sale)
        self.blocks[actor['id']] = sink
        return sink
    
    def build_marketplace(self, actor: Dict) -> Service:
        """Create Service block from marketplace actor."""
        vendor_count = actor.get('vendorCount', 10)
        capacity = max(1, vendor_count // 10)
        
        service = Service(
            name=actor['id'],
            service_time=lambda: self.rv.uniform(0.1, 0.5) * self.config.time_scale,
            capacity=capacity,
            engine=self.engine
        )
        
        self.blocks[actor['id']] = service
        return service
    
    def build_actor(self, actor: Dict) -> Any:
        """Build appropriate block for actor type."""
        actor_type = actor.get('type', '')
        
        builders = {
            'supplier': self.build_supplier,
            'producer': self.build_producer,
            'distributor': self.build_distributor,
            'wholesaler': self.build_wholesaler,
            'retailer': self.build_retailer,
            'marketplace': self.build_marketplace,
        }
        
        builder = builders.get(actor_type)
        if builder:
            return builder(actor)
        else:
            raise ValueError(f"Unknown actor type: {actor_type}")


# ============================================================================
# SUPPLY CHAIN BUILDER
# ============================================================================

class SupplyChainBuilder:
    """Builds complete supply chain simulation from topology data."""
    
    def __init__(self, config: SimulationConfig):
        self.config = config
        self.engine = SimulationEngine(seed=config.seed)
        self.rv = RandomVariate(seed=config.seed)
        self.actor_builder = ActorBlockBuilder(self.engine, self.rv, config)
        self.actors: List[Dict] = []
        self.relationships: List[Dict] = []
        self.combines: Dict[str, Combine] = {}
    
    def load_topology(self) -> None:
        """Load actors and relationships from JSON files."""
        actors_path = Path(self.config.actors_file)
        relationships_path = Path(self.config.relationships_file)
        
        if actors_path.exists():
            with open(actors_path) as f:
                self.actors = json.load(f)
        else:
            raise FileNotFoundError(f"Actors file not found: {actors_path}")
        
        if relationships_path.exists():
            with open(relationships_path) as f:
                self.relationships = json.load(f)
        else:
            raise FileNotFoundError(f"Relationships file not found: {relationships_path}")
    
    def build_actors(self) -> None:
        """Build PML blocks for all actors."""
        for actor in self.actors:
            self.actor_builder.build_actor(actor)
    
    def _count_incoming(self, actor_id: str) -> int:
        """Count incoming relationships to an actor."""
        return sum(1 for r in self.relationships 
                   if r['toActorId'] == actor_id and r['status'] == 'active')
    
    def _get_incoming_actors(self, actor_id: str) -> List[str]:
        """Get list of actors with outgoing relationships to this actor."""
        return [r['fromActorId'] for r in self.relationships 
                if r['toActorId'] == actor_id and r['status'] == 'active']
    
    def connect_relationships(self) -> None:
        """Connect blocks based on relationships."""
        # First pass: identify actors needing Combine blocks
        for actor in self.actors:
            incoming_count = self._count_incoming(actor['id'])
            if incoming_count > 1:
                combine = Combine(
                    name=f"{actor['id']}_combine",
                    num_inputs=incoming_count,
                    engine=self.engine
                )
                self.combines[actor['id']] = combine
                
                # Connect combine to actor block
                actor_block = self.actor_builder.blocks.get(actor['id'])
                if actor_block:
                    combine >> actor_block
        
        # Second pass: connect relationships
        combine_input_counters: Dict[str, int] = {}
        
        for rel in self.relationships:
            if rel['status'] != 'active':
                continue
            
            from_id = rel['fromActorId']
            to_id = rel['toActorId']
            
            from_block = self.actor_builder.blocks.get(from_id)
            to_block = self.actor_builder.blocks.get(to_id)
            
            if not from_block or not to_block:
                continue
            
            # Check if target needs combine
            if to_id in self.combines:
                combine = self.combines[to_id]
                input_idx = combine_input_counters.get(to_id, 0)
                from_block.get_output_port("out").connect(
                    combine.get_input_port(f"in_{input_idx}")
                )
                combine_input_counters[to_id] = input_idx + 1
            else:
                from_block >> to_block
    
    def build(self) -> None:
        """Build complete supply chain simulation."""
        self.load_topology()
        self.build_actors()
        self.connect_relationships()
    
    def run(self) -> Dict[str, Any]:
        """Run simulation and return results."""
        if self.config.verbose:
            print("=" * 70)
            print("SUPPLY CHAIN SIMULATION")
            print("=" * 70)
            print(f"\nTopology: {len(self.actors)} actors, {len(self.relationships)} relationships")
            print(f"Simulation time: {self.config.simulation_time} minutes")
        
        self.engine.run(until=self.config.simulation_time)
        
        return self.collect_results()
    
    def collect_results(self) -> Dict[str, Any]:
        """Collect simulation results."""
        results = {
            'actors': {},
            'resources': {},
            'queues': {},
            'summary': {}
        }
        
        # Collect per-actor statistics
        for actor_id, block in self.actor_builder.blocks.items():
            stats = block.get_statistics()
            results['actors'][actor_id] = stats
        
        # Collect resource utilization
        for pool_id, pool in self.actor_builder.pools.items():
            stats = pool.get_statistics()
            results['resources'][pool_id] = stats
        
        # Collect queue statistics
        for queue_id, queue in self.actor_builder.queues.items():
            stats = queue.get_statistics()
            results['queues'][queue_id] = stats
        
        # Calculate summary metrics
        sinks = [b for b in self.actor_builder.blocks.values() if isinstance(b, Sink)]
        if sinks:
            total_throughput = sum(s.count() for s in sinks)
            avg_lead_time = sum(
                s.get_statistics().get('average_time_in_system', 0) * s.count()
                for s in sinks
            ) / total_throughput if total_throughput > 0 else 0
            
            results['summary'] = {
                'total_throughput': total_throughput,
                'average_lead_time': avg_lead_time,
                'throughput_rate': total_throughput / self.config.simulation_time * 60,
            }
        
        return results
    
    def print_results(self, results: Dict[str, Any]) -> None:
        """Print formatted results."""
        print("\n" + "=" * 70)
        print("SIMULATION RESULTS")
        print("=" * 70)
        
        # Summary
        if results.get('summary'):
            print("\nSummary:")
            print(f"  Total throughput: {results['summary']['total_throughput']} units")
            print(f"  Average lead time: {results['summary']['average_lead_time']:.2f} minutes")
            print(f"  Throughput rate: {results['summary']['throughput_rate']:.1f} units/hour")
        
        # Resource utilization
        if results.get('resources'):
            print("\nResource Utilization:")
            for pool_id, stats in results['resources'].items():
                util = stats.get('average_utilization', 0)
                print(f"  {pool_id}: {util:.1%}")
        
        # Actor statistics
        print("\nActor Statistics:")
        for actor_id, stats in results['actors'].items():
            if 'entities_disposed' in stats:
                print(f"  {actor_id} (sink): {stats['entities_disposed']} completed, "
                      f"avg time {stats.get('average_time_in_system', 0):.1f} min")
            elif 'arrivals_generated' in stats:
                print(f"  {actor_id} (source): {stats['arrivals_generated']} generated")
            elif 'entities_exited' in stats:
                print(f"  {actor_id}: {stats['entities_exited']} processed")


# ============================================================================
# SCENARIO ANALYSIS
# ============================================================================

def run_capacity_analysis(base_config: SimulationConfig, capacity_factors: List[float]):
    """Analyze impact of capacity scaling."""
    print("\n" + "=" * 70)
    print("CAPACITY ANALYSIS")
    print("=" * 70)
    
    print(f"\n{'Scale':>8} {'Throughput':>12} {'Lead Time':>12} {'Util %':>10}")
    print("-" * 44)
    
    for factor in capacity_factors:
        config = SimulationConfig(
            simulation_time=base_config.simulation_time,
            capacity_scale=factor,
            seed=base_config.seed,
            actors_file=base_config.actors_file,
            relationships_file=base_config.relationships_file,
            verbose=False
        )
        
        builder = SupplyChainBuilder(config)
        builder.build()
        results = builder.run()
        
        summary = results.get('summary', {})
        avg_util = sum(
            r.get('average_utilization', 0) 
            for r in results.get('resources', {}).values()
        ) / max(1, len(results.get('resources', {})))
        
        print(f"{factor:>8.1f}x {summary.get('total_throughput', 0):>12} "
              f"{summary.get('average_lead_time', 0):>12.1f} {avg_util:>10.1%}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Run supply chain simulation."""
    config = SimulationConfig(
        simulation_time=480.0,
        verbose=True,
        actors_file="actors.json",
        relationships_file="relationships.json"
    )
    
    try:
        builder = SupplyChainBuilder(config)
        builder.build()
        results = builder.run()
        builder.print_results(results)
        
        # Optional: run capacity analysis
        # run_capacity_analysis(config, [0.5, 0.75, 1.0, 1.25, 1.5, 2.0])
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("\nPlease ensure actors.json and relationships.json are in the working directory.")
        print("See /home/ubuntu/worker-d-scm-extracted/wodog-main/ext/workerd-ext/ for examples.")


if __name__ == "__main__":
    main()
