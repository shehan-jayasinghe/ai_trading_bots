export type WorkflowCreate = {
  name: string;
  trading_pair: string;
  trading_type: string;
  starting_time: string;
  one_day_minimum_trade: string;
};

export type Workflow = {
  id: string;
  user_id: string;
  name: string;
  trading_pair: string;
  trading_type: string;
  status: string;
  starting_time: string | null;
  one_day_minimum_trade: string | null;
  created_at: string | null;
};
