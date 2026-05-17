export type WorkflowStatus = "draft" | "edit" | "completed" | "run";

export type WorkflowCreate = {
  name: string;
  trading_pair: string;
  trading_type: string;
  starting_time: string;
  one_day_minimum_trade: string;
  deriv_app_id?: string;
  deriv_api_token?: string;
};

export type WorkflowUpdate = Partial<WorkflowCreate>;

export type WorkflowLastTrade = {
  run_id?: string;
  trade_id?: string | null;
  status?: string;
  direction?: string | null;
  stake?: number;
  symbol?: string;
  source?: string;
  contract_id?: string;
  error?: string;
};

export type Workflow = {
  id: string;
  user_id: string;
  name: string;
  trading_pair: string;
  trading_type: string;
  status: WorkflowStatus;
  starting_time: string | null;
  one_day_minimum_trade: string | null;
  created_at: string | null;
  deriv_app_id: string | null;
  has_deriv_api_token: boolean;
  last_trade_result: WorkflowLastTrade | null;
};
