// Parameterized query templates, not a multi-query executable script.
// Current confirmed assertions for attendees of a particular event.
MATCH (p:Person)-[:ATTENDS]->(e:Event {id:$event_id}),
      (a:Assertion)-[:HAS_SUBJECT]->(p),
      (a)-[:SUPPORTED_BY]->(s:Source)
WHERE a.status = 'confirmed'
  AND a.valid_from <= $as_of
  AND (a.valid_to IS NULL OR a.valid_to > $as_of)
  AND (a.scope_type = 'person' OR (a.scope_type = 'event' AND a.scope_id = $event_id))
RETURN p.id, p.name, a.id, a.predicate, a.value_json, a.version, s.id, s.artifact_ref
LIMIT 50;

// Plans affected by a corrected or forgotten assertion.
MATCH (plan:Plan)-[:BASED_ON]->(a:Assertion {id:$assertion_id})
RETURN plan.id, plan.revision, a.id LIMIT 50;

// Explain a particular plan decision through its stored evidence.
MATCH path=(plan:Plan {id:$plan_id})-[:BASED_ON]->(a:Assertion)-[:SUPPORTED_BY]->(s:Source)
RETURN path LIMIT 20;

// Calendar overlap. Provider ownership is already enforced through graph selection.
MATCH (e:Event)
WHERE e.starts_at < $proposed_end AND e.ends_at > $proposed_start
RETURN e.id, e.name, e.starts_at, e.ends_at LIMIT 20;
