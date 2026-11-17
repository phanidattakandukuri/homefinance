from datetime import date, timedelta
import csv
import io
import zipfile
from xml.sax.saxutils import escape as xml_escape
import fitz
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.v1.dependencies import authorize_member_view, current_user, household_member
from app.db.session import get_db
from app.models.analytics import FinancialSnapshot, SnapshotAudit
from app.models.transaction import Transaction, Category
from app.models.household import HouseholdMember
from app.models.auth import User
from app.schemas.analytics import DashboardResponse, SnapshotResponse
from app.services.analytics import dashboard
router=APIRouter(prefix="/households/{household_id}/analytics",tags=["analytics"])
def period(period_type, start, end):
    today=date.today()
    if period_type == "current_month": return today.replace(day=1), today
    if period_type == "previous_month":
        first=today.replace(day=1); prev=first-timedelta(days=1); return prev.replace(day=1), prev
    if period_type == "calendar_year": return today.replace(month=1,day=1), today
    if period_type == "financial_year": return date(today.year if today.month >= 4 else today.year-1,4,1), today
    if not start or not end: raise HTTPException(422,"start and end are required")
    return start,end
@router.get("/household",response_model=DashboardResponse)
def household_dashboard(household_id:UUID, period_type:str="current_month", start:date|None=None,end:date|None=None,user:User=Depends(current_user),db:Session=Depends(get_db)):
    household_member(household_id,db,user); s,e=period(period_type,start,end); return dashboard(db,household_id,s,e)
@router.get("/members/{member_id}",response_model=DashboardResponse)
def member_dashboard(household_id:UUID,member_id:UUID,period_type:str="current_month",start:date|None=None,end:date|None=None,user:User=Depends(current_user),db:Session=Depends(get_db)):
    authorize_member_view(household_id, member_id, db, user); s,e=period(period_type,start,end); return dashboard(db,household_id,s,e,member_id)
@router.post("/snapshots",response_model=SnapshotResponse)
def create_snapshot(household_id:UUID,start:date,end:date,reason:str="scheduled",user:User=Depends(current_user),db:Session=Depends(get_db)):
    household_member(household_id,db,user); existing=db.scalar(select(FinancialSnapshot).where(FinancialSnapshot.household_id==household_id,FinancialSnapshot.period_start==start,FinancialSnapshot.period_end==end))
    if existing: raise HTTPException(409,"Snapshot already exists; use controlled recalculation")
    x=FinancialSnapshot(household_id=household_id,period_start=start,period_end=end,payload=dashboard(db,household_id,start,end),recalculation_reason=reason); db.add(x); db.flush(); return {"id":x.id,"period_start":start,"period_end":end,"payload":x.payload,"calculated_at":str(x.calculated_at)}
@router.get("/snapshots")
def snapshots(household_id:UUID,user:User=Depends(current_user),db:Session=Depends(get_db)):
    household_member(household_id,db,user); return db.scalars(select(FinancialSnapshot).where(FinancialSnapshot.household_id==household_id).order_by(FinancialSnapshot.period_start.desc())).all()

@router.get("/export/transactions.csv")
def export_transactions(household_id: UUID, start: date | None = None, end: date | None = None, member_id: UUID | None = None, user: User = Depends(current_user), db: Session = Depends(get_db)):
    actor = household_member(household_id, db, user)
    if actor.role not in {"owner", "admin"}:
        member_id = actor.id
    query = select(Transaction, Category.name, HouseholdMember.display_name).join(Category, Transaction.category_id == Category.id).join(HouseholdMember, Transaction.member_id == HouseholdMember.id).where(Transaction.household_id == household_id, Transaction.is_void.is_(False))
    if start: query = query.where(Transaction.transaction_date >= start)
    if end: query = query.where(Transaction.transaction_date <= end)
    if member_id: query = query.where(Transaction.member_id == member_id)
    output = io.StringIO(); writer = csv.writer(output)
    writer.writerow(["transaction_id", "date", "member", "type", "category", "amount", "currency", "merchant", "description", "payment_method", "source", "reference_number"])
    for tx, category, member in db.execute(query.order_by(Transaction.transaction_date.desc(), Transaction.created_at.desc())):
        writer.writerow([str(tx.id), tx.transaction_date.isoformat(), member, tx.transaction_type, category, str(tx.amount), tx.currency, tx.merchant or "", tx.description or "", tx.payment_method or "", tx.source or "", tx.reference_number or ""])
    output.seek(0)
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers={"Content-Disposition": f"attachment; filename=homefin-transactions-{household_id}.csv"})

def _transaction_export_rows(household_id, start, end, member_id, user, db):
    actor = household_member(household_id, db, user)
    if actor.role not in {"owner", "admin"}:
        member_id = actor.id
    query = select(Transaction, Category.name, HouseholdMember.display_name).join(Category, Transaction.category_id == Category.id).join(HouseholdMember, Transaction.member_id == HouseholdMember.id).where(Transaction.household_id == household_id, Transaction.is_void.is_(False))
    if start: query = query.where(Transaction.transaction_date >= start)
    if end: query = query.where(Transaction.transaction_date <= end)
    if member_id: query = query.where(Transaction.member_id == member_id)
    headers = ["transaction_id", "date", "member", "type", "category", "amount", "currency", "merchant", "description", "payment_method", "source", "reference_number"]
    rows = [headers]
    for tx, category, member in db.execute(query.order_by(Transaction.transaction_date.desc(), Transaction.created_at.desc())):
        rows.append([str(tx.id), tx.transaction_date.isoformat(), member, tx.transaction_type, category, str(tx.amount), tx.currency, tx.merchant or "", tx.description or "", tx.payment_method or "", tx.source or "", tx.reference_number or ""])
    return rows

@router.get("/export/transactions.xlsx")
def export_transactions_xlsx(household_id: UUID, start: date | None = None, end: date | None = None, member_id: UUID | None = None, user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = _transaction_export_rows(household_id, start, end, member_id, user, db)
    def cell(value):
        return f'<c t="inlineStr"><is><t>{xml_escape(str(value))}</t></is></c>'
    sheet_rows = "".join(f'<row r="{i}">{"".join(cell(value) for value in row)}</row>' for i, row in enumerate(rows, 1))
    content_types = '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>'
    workbook = '<?xml version="1.0" encoding="UTF-8"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Transactions" sheetId="1" r:id="rId1"/></sheets></workbook>'.replace("spreadsheetml/2006", "spreadsheetml/2006")
    rels = '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>'
    workbook_rels = '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>'
    sheet = f'<?xml version="1.0" encoding="UTF-8"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>{sheet_rows}</sheetData></worksheet>'
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types)
        archive.writestr("_rels/.rels", rels)
        archive.writestr("xl/workbook.xml", workbook)
        archive.writestr("xl/_rels/workbook.xml.rels", workbook_rels)
        archive.writestr("xl/worksheets/sheet1.xml", sheet)
    return StreamingResponse(iter([output.getvalue()]), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": f"attachment; filename=homefin-transactions-{household_id}.xlsx"})

@router.get("/export/transactions.pdf")
def export_transactions_pdf(household_id: UUID, start: date | None = None, end: date | None = None, member_id: UUID | None = None, user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = _transaction_export_rows(household_id, start, end, member_id, user, db)
    document = fitz.open()
    page = document.new_page(width=595, height=842)
    y = 42
    page.insert_text((40, y), "HomeFin AI — Transaction Report", fontsize=16, color=(0.08, 0.13, 0.24))
    y += 24
    page.insert_text((40, y), f"Household: {household_id}    Rows: {max(len(rows) - 1, 0)}", fontsize=9)
    y += 24
    for index, row in enumerate(rows):
        if index == 0:
            line = "Date | Member | Type | Category | Amount | Currency"
        else:
            line = " | ".join([row[1], row[2], row[3], row[4], row[5], row[6]])
        if len(line) > 105:
            line = line[:102] + "..."
        page.insert_text((40, y), line, fontsize=7.5, fontname="courier")
        y += 13
        if y > 805 and index < len(rows) - 1:
            page = document.new_page(width=595, height=842)
            y = 42
    output = document.tobytes()
    document.close()
    return StreamingResponse(iter([output]), media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=homefin-transactions-{household_id}.pdf"})
