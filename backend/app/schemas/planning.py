from datetime import date
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field
class BudgetCreate(BaseModel): member_id:UUID|None=None; category_id:UUID|None=None; name:str; amount:Decimal=Field(gt=0); period_start:date; period_end:date
class BudgetResponse(BudgetCreate): id:UUID; household_id:UUID; model_config={"from_attributes":True}
class GoalCreate(BaseModel): member_id:UUID|None=None; name:str; goal_type:str; target_amount:Decimal=Field(gt=0); target_date:date|None=None; current_amount:Decimal=Field(default=0,ge=0)
class GoalResponse(GoalCreate): id:UUID; household_id:UUID; is_active:bool; progress:Decimal|None=None; model_config={"from_attributes":True}
class RecurringCreate(BaseModel): member_id:UUID; category_id:UUID; name:str; transaction_type:str; amount:Decimal=Field(gt=0); frequency:str; next_run_date:date; payload:dict|None=None
