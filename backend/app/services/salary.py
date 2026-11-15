from decimal import Decimal
from app.models.salary import SalaryRecord

def breakdown(record: SalaryRecord) -> dict:
    def total(*values):
        known = [v for v in values if v is not None]
        return sum(known, Decimal("0")) if len(known) == len(values) else None
    deductions = total(record.employee_pf, record.professional_tax, record.tds, record.other_deductions)
    employer = total(record.employer_pf, record.gratuity_component)
    employee = total(record.employee_pf)
    return {"salary_id": record.id, "monthly_gross": record.monthly_gross, "monthly_in_hand": record.monthly_in_hand,
            "monthly_employee_contributions": employee, "monthly_employer_contributions": employer,
            "monthly_deductions": deductions,
            "calculation_note": "Values are reported components; missing components remain unknown. No tax liability is estimated."}
