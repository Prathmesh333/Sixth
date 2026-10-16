// Illustrative seed. Execute statements separately in a dedicated fixture graph.
// Validate syntax with the selected FalkorDB release before relying on it.
MERGE (u:Entity:Person {id:'alex'}) SET u.name='Alex', u.kind='Person';
MERGE (p:Entity:Person {id:'maya'}) SET p.name='Maya', p.kind='Person';
MATCH (u:Person {id:'alex'}), (p:Person {id:'maya'}) MERGE (u)-[:KNOWS]->(p);
MERGE (e:Entity:Event {id:'dinner-01'}) SET e.name='Birthday dinner', e.kind='Event', e.starts_at=1792243800000, e.ends_at=1792251000000, e.timezone='Asia/Calcutta', e.guest_count=4;
MATCH (p:Person {id:'maya'}), (e:Event {id:'dinner-01'}) MERGE (p)-[:ATTENDS]->(e);
MERGE (s:Entity:Source {id:'source-vegetarian'}) SET s.name='User message', s.kind='Source', s.artifact_ref='fixture:source-vegetarian', s.captured_at=1792125000000;
MERGE (a:Entity:Assertion {id:'fact-maya-vegetarian'}) SET a.name='Maya dietary preference', a.kind='Assertion', a.predicate='diet', a.value_json='"vegetarian"', a.status='confirmed', a.valid_from=1792125000000, a.recorded_at=1792125000000, a.scope_type='person', a.scope_id='maya', a.version=1;
MATCH (a:Assertion {id:'fact-maya-vegetarian'}), (p:Person {id:'maya'}), (s:Source {id:'source-vegetarian'}) MERGE (a)-[:HAS_SUBJECT]->(p) MERGE (a)-[:SUPPORTED_BY]->(s);
MERGE (plan:Entity:Plan {id:'plan-dinner'}) SET plan.name='Dinner plan', plan.kind='Plan', plan.revision=1;
MATCH (plan:Plan {id:'plan-dinner'}), (a:Assertion {id:'fact-maya-vegetarian'}) MERGE (plan)-[:BASED_ON]->(a);
