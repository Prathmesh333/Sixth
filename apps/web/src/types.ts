export type Theme = "dusk" | "paper" | "grove";
export type View =
  "chat" | "memory" | "plans" | "friends" | "availability" | "settings";
export interface Session {
  account: string;
  name: string;
  csrf_token: string;
  demo: boolean;
}
export interface Source {
  source_id: string;
  excerpt?: string;
  captured_at: string;
}
export interface Fact {
  id: string;
  subject_id: string;
  subject: string;
  predicate: string;
  value: string;
  version: number;
  scope_type: string;
  scope_id: string;
  recorded_at: string;
  sources: Source[];
}
export interface Ingredient {
  id: string;
  name: string;
  quantity: number;
  required: number;
  pantry: number;
  unit: string;
  amount_minor: number;
}
export interface Plan {
  id: string;
  title: string;
  conversation_id: string;
  guests: number;
  revision: number;
  recipe: {
    name: string;
    description: string;
    minutes: number;
    dairy_free: boolean;
  };
  items: Ingredient[];
  evidence_ids: string[];
  status: string;
  starts_at: string;
}
export interface Action {
  action_id: string;
  decision_id: string;
  fingerprint: string;
  plan_revision: number;
  mode: string;
  expires_at: string;
}
export interface Task {
  id: string;
  conversation_id: string;
  status: string;
  reply?: string;
  action?: Action;
  scheduling?: {
    title: string;
    starts_at?: string;
    ends_at?: string;
    action_label?: string;
    friends?: string[];
    timezone?: string;
    results?: { friend: { name: string }; status: string }[];
  };
  plan?: Plan;
  evidence?: Fact[];
  result?: { status: string; verified_at: string };
  stale?: boolean;
}
export interface Message {
  id: string;
  role: "user" | "assistant";
  text: string;
  task_id?: string;
  client_id?: string;
}
export interface Conversation {
  id: string;
  title: string;
  created_at: string;
}
export interface ConversationDetail extends Conversation {
  messages: Message[];
  tasks: Task[];
}
export interface Status {
  memory: {
    backend: string;
    connected: boolean;
    simulation: boolean;
    detail: string;
  };
  planner: { mode: string; model: string | null };
  calendar: { mode: string; connected: boolean };
  store: { mode: string };
  browser: { connected: boolean };
  voice: { connected: boolean };
}
export interface TaskEvent {
  task_id: string;
  sequence: number;
  type: string;
  payload: Record<string, unknown>;
}
