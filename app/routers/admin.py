from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy.exc import MultipleResultsFound
import schemas, datetime, utils
from models import *
from database import get_db

# API
router = APIRouter(
    tags=['Admin'],
    prefix="/admin"
)

# QA Result
@router.get('/qaip_data/api/table_data/{year}')
def get_qaip_table(year: int, db: Session = Depends(get_db)):
    qaips = db.query(QAIP).filter(
        QAIP.prj.has(year=year)
    ).all()

    res = []

    for q in qaips:
        cats    = utils.qa_to_category_str(q)
        stages  = utils.qa_to_stage_str(q)
        delivs  = utils.qa_to_delivs_str(q)

        res.append({
            "id"            : str(q.id),
            "QAType"        : q.qa_type.name,
            "auditProject"  : q.prj.name,
            "TL"            : q.TL,
            "divisionHead"  : q.DH,
            "result"        : q.qa_grading_result.name,
            "category"      : ", ".join(cats),
            "stage"         : ", ".join(stages),
            "deliverable"   : ", ".join(delivs),
            "noOfIssues"    : len(delivs),
            "QASample"      : q.qa_sample
        })
    
    return res

@router.delete('/qaip_data/api/table_data')
def delete_qaip_table_entry(req: schemas.QAIPInHiCoupling, db: Session = Depends(get_db)):
    qaip = db.query(QAIP).filter(
        QAIP.id == req.id
    )

    if not qaip.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')
    
    qaip.delete()
    db.commit()

    return {'details': 'Deleted'}

# Budget
@router.get('/budget_data/api/table_data/{year}/{month}')
def get_budget_table(year: int, month: int, db: Session = Depends(get_db)):
    cats = [
        "Staff Expense",
        "Staff Expense (Salaries)",
        "Staff Training & Regional Meeting",
        "Revenue Related (Communications)",
        "IT Related (Softwares)",
        "Occupancy Related (Premises)",
        "Other Related",
        "Transport & Travel",
        "Others",
        "Direct Expense",
        "Indirect Expense"
    ]

    i = 1
    res = []
    for c in cats:
        res.append({
            "id"                : str(i),
            "expenses"          : c,
            "budgetYear"        : 0,
            "budgetMonth"       : 0,
            "budgetMonthTD"     : 0,
            "actualMonth"       : 0,
            "actualMonthTD"     : 0,
            "MTD"               : '-',
            "YTD"               : '-',
            "STDProRate"        : '-',
            "overUnderBudget"   : '-',
            "variance"          : ''
        })
        i += 1

    # Get Actual Budget
    actualBudget = db.query(MonthlyActualBudget).filter(
        MonthlyActualBudget.year == year,
        MonthlyActualBudget.month == month
    ).first()

    if actualBudget:
        res[0]["actualMonth"]   = actualBudget.staff_salaries + actualBudget.staff_training_reg_meeting
        res[1]["actualMonth"]   = actualBudget.staff_salaries
        res[2]["actualMonth"]   = actualBudget.staff_training_reg_meeting
        res[3]["actualMonth"]   = actualBudget.revenue_related
        res[4]["actualMonth"]   = actualBudget.it_related
        res[5]["actualMonth"]   = actualBudget.occupancy_related
        res[6]["actualMonth"]   = actualBudget.other_transport_travel + actualBudget.other_other
        res[7]["actualMonth"]   = actualBudget.other_transport_travel
        res[8]["actualMonth"]   = actualBudget.other_other
        res[9]["actualMonth"]   = res[0]["actualMonth"] + res[3]["actualMonth"] + res[4]["actualMonth"] + res[5]["actualMonth"] + res[6]["actualMonth"]
        res[10]["actualMonth"]  = actualBudget.indirect_expense

    actualBudgets = db.query(MonthlyActualBudget).filter(
        MonthlyActualBudget.year == year,
        MonthlyActualBudget.month <= month
    ).all()

    for a in actualBudgets:
        res[0]["actualMonthTD"]   += a.staff_salaries + a.staff_training_reg_meeting
        res[1]["actualMonthTD"]   += a.staff_salaries
        res[2]["actualMonthTD"]   += a.staff_training_reg_meeting

        res[3]["actualMonthTD"]   += a.revenue_related
        res[4]["actualMonthTD"]   += a.it_related
        res[5]["actualMonthTD"]   += a.occupancy_related

        res[6]["actualMonthTD"]   += a.other_transport_travel + a.other_other
        res[7]["actualMonthTD"]   += a.other_transport_travel
        res[8]["actualMonthTD"]   += a.other_other

        res[9]["actualMonthTD"]   += res[0]["actualMonthTD"] + res[3]["actualMonthTD"] + res[4]["actualMonthTD"] + res[5]["actualMonthTD"] + res[6]["actualMonthTD"]
        res[10]["actualMonthTD"]  += a.indirect_expense

    # Get Yearly Budget
    y = db.query(YearlyBudget).filter(
        YearlyBudget.year == year
    ).first()

    if y:
        res[0]["budgetYear"]   += y.staff_salaries + y.staff_training_reg_meeting
        res[1]["budgetYear"]   += y.staff_salaries
        res[2]["budgetYear"]   += y.staff_training_reg_meeting

        res[3]["budgetYear"]   += y.revenue_related
        res[4]["budgetYear"]   += y.it_related
        res[5]["budgetYear"]   += y.occupancy_related

        res[6]["budgetYear"]   += y.other_transport_travel + y.other_other
        res[7]["budgetYear"]   += y.other_transport_travel
        res[8]["budgetYear"]   += y.other_other

        res[9]["budgetYear"]   += res[0]["budgetYear"] + res[3]["budgetYear"] + res[4]["budgetYear"] + res[5]["budgetYear"] + res[6]["budgetYear"]
        res[10]["budgetYear"]  += y.indirect_expense

    # Get Monthly Budgets
    monthlyBudget = db.query(MonthlyBudget).filter(
        MonthlyBudget.year == year,
        MonthlyBudget.month == month
    ).first()

    if monthlyBudget:
        res[0]["budgetMonth"]   += monthlyBudget.staff_salaries + monthlyBudget.staff_training_reg_meeting
        res[1]["budgetMonth"]   += monthlyBudget.staff_salaries
        res[2]["budgetMonth"]   += monthlyBudget.staff_training_reg_meeting
        res[3]["budgetMonth"]   += monthlyBudget.revenue_related
        res[4]["budgetMonth"]   += monthlyBudget.it_related
        res[5]["budgetMonth"]   += monthlyBudget.occupancy_related
        res[6]["budgetMonth"]   += monthlyBudget.other_transport_travel + monthlyBudget.other_other
        res[7]["budgetMonth"]   += monthlyBudget.other_transport_travel
        res[8]["budgetMonth"]   += monthlyBudget.other_other
        res[9]["budgetMonth"]   += res[0]["budgetMonth"] + res[3]["budgetMonth"] + res[4]["budgetMonth"] + res[5]["budgetMonth"] + res[6]["budgetMonth"]
        res[10]["budgetMonth"]  += monthlyBudget.indirect_expense
    
    monthlyBudgets = db.query(MonthlyBudget).filter(
        MonthlyBudget.year == year,
        MonthlyBudget.month <= month
    ).all()

    for m in monthlyBudgets:
        res[0]["budgetMonthTD"]   += m.staff_salaries + m.staff_training_reg_meeting
        res[1]["budgetMonthTD"]   += m.staff_salaries
        res[2]["budgetMonthTD"]   += m.staff_training_reg_meeting
        res[3]["budgetMonthTD"]   += m.revenue_related
        res[4]["budgetMonthTD"]   += m.it_related
        res[5]["budgetMonthTD"]   += m.occupancy_related
        res[6]["budgetMonthTD"]   += m.other_transport_travel + m.other_other
        res[7]["budgetMonthTD"]   += m.other_transport_travel
        res[8]["budgetMonthTD"]   += m.other_other
        res[9]["budgetMonthTD"]   += res[0]["budgetMonthTD"] + res[3]["budgetMonthTD"] + res[4]["budgetMonthTD"] + res[5]["budgetMonthTD"] + res[6]["budgetMonthTD"]
        res[10]["budgetMonthTD"]  += m.indirect_expense

    # Process Statistics
    for r in res:
        mtd_rate = r["actualMonthTD"] / r["budgetMonthTD"] if r["budgetMonthTD"] != 0 else None
        ytd_rate = r["actualMonthTD"] / r["budgetYear"] if r["budgetYear"] != 0 else None
        std_rate = month / 12

        r["MTD"]               = "-%" if mtd_rate == None else f"{round(mtd_rate * 100)}%"
        r["YTD"]               = "-%" if ytd_rate == None else f"{round(ytd_rate * 100)}%"
        r["STDProRate"]        = f"{round(std_rate * 100)}%"
        r["overUnderBudget"]   = "-%" if ytd_rate == None else f"{round((ytd_rate - std_rate) * 100)}%"

    return res

@router.patch('/budget_data/api/table_data/{year}/{month}', status_code=status.HTTP_202_ACCEPTED)
def patch_budget_table_entry(year: int, month: int, req: schemas.BudgetTableInHiCoupling, db: Session = Depends(get_db)):
    cats = [
        "Staff Expense",
        "Staff Expense (Salaries)",
        "Staff Training & Regional Meeting",
        "Revenue Related (Communications)",
        "IT Related (Softwares)",
        "Occupancy Related (Premises)",
        "Other Related",
        "Transport & Travel",
        "Others",
        "Direct Expense",
        "Indirect Expense"
    ]

    formulated_cats = [0, 6, 9]

    # Check Expense Type
    cat_index = -1
    if not req.expenses in cats:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Given Expense field ({req.expenses}) is not allowed")
    elif cats.index(req.expenses) in formulated_cats:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Given Expense field ({req.expenses}) is formulated value (Cannot be modified)")
    else:
        cat_index = cats.index(req.expenses)

    # Set Budget Year
    yearBudget = db.query(YearlyBudget).filter(
        YearlyBudget.year == year
    )

    try:
        yearBudget_model = yearBudget.one_or_none()
    except MultipleResultsFound:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Multiple YearlyBudget entries for given year ({year}) were found!")

    if not yearBudget_model: # No YearlyBudget was found
        # Create a new Yearly Budget
        payload = {}

        for c in cats:
            payload[c] = 0

        payload[req.expenses] = req.budgetYear

        newYearBudget = YearlyBudget(
            year                        = year,
            staff_salaries              = payload["Staff Expense (Salaries)"],
            staff_training_reg_meeting  = payload["Staff Training & Regional Meeting"],
            revenue_related             = payload["Revenue Related (Communications)"],
            it_related                  = payload["IT Related (Softwares)"],
            occupancy_related           = payload["Occupancy Related (Premises)"],
            other_transport_travel      = payload["Transport & Travel"],
            other_other                 = payload["Others"],
            indirect_expense            = payload["Indirect Expense"]
        )

        db.add(newYearBudget)
        db.commit()
        db.refresh(newYearBudget)
    else: # Existing YearlyBudget was found 
        stored_data = jsonable_encoder(yearBudget_model)
        stored_model = schemas.YearlyBudgetIn(**stored_data)

        payload = schemas.YearlyBudgetIn()

        if req.expenses == cats[1]:
            payload.staff_salaries = req.budgetYear
        elif req.expenses == cats[2]:
            payload.staff_training_reg_meeting = req.budgetYear
        elif req.expenses == cats[3]:
            payload.revenue_related = req.budgetYear
        elif req.expenses == cats[4]:
            payload.it_related = req.budgetYear
        elif req.expenses == cats[5]:
            payload.occupancy_related = req.budgetYear
        elif req.expenses == cats[7]:
            payload.other_transport_travel = req.budgetYear
        elif req.expenses == cats[8]:
            payload.other_other = req.budgetYear
        elif req.expenses == cats[10]:
            payload.indirect_expense = req.budgetYear

        new_data = payload.dict(exclude_unset=True)
        updated = stored_model.copy(update=new_data)

        stored_data.update(updated)

        yearBudget.update(stored_data)
        db.commit()

    # Set Budget Month
    monthBudget = db.query(MonthlyBudget).filter(
        MonthlyBudget.year == year,
        MonthlyBudget.month == month
    )

    try:
        monthBudget_model = monthBudget.one_or_none()
    except MultipleResultsFound:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Multiple MonthBudget entries for given year/month ({year}/{month}) were found!")

    if not monthBudget_model: # No MonthlyBudget was found
        # Create a new Yearly Budget
        payload = {}

        for c in cats:
            payload[c] = 0

        payload[req.expenses] = req.budgetMonth

        newMonthBudget = MonthlyBudget(
            year                        = year,
            month                       = month,
            staff_salaries              = payload["Staff Expense (Salaries)"],
            staff_training_reg_meeting  = payload["Staff Training & Regional Meeting"],
            revenue_related             = payload["Revenue Related (Communications)"],
            it_related                  = payload["IT Related (Softwares)"],
            occupancy_related           = payload["Occupancy Related (Premises)"],
            other_transport_travel      = payload["Transport & Travel"],
            other_other                 = payload["Others"],
            indirect_expense            = payload["Indirect Expense"]
        )

        db.add(newMonthBudget)
        db.commit()
        db.refresh(newMonthBudget)
    else: # Existing MonthlyBudget was found 
        stored_data = jsonable_encoder(monthBudget_model)
        stored_model = schemas.MonthlyBudgetIn(**stored_data)

        payload = schemas.MonthlyBudgetIn()

        if req.expenses == cats[1]:
            payload.staff_salaries = req.budgetYear
        elif req.expenses == cats[2]:
            payload.staff_training_reg_meeting = req.budgetYear
        elif req.expenses == cats[3]:
            payload.revenue_related = req.budgetYear
        elif req.expenses == cats[4]:
            payload.it_related = req.budgetYear
        elif req.expenses == cats[5]:
            payload.occupancy_related = req.budgetYear
        elif req.expenses == cats[7]:
            payload.other_transport_travel = req.budgetYear
        elif req.expenses == cats[8]:
            payload.other_other = req.budgetYear
        elif req.expenses == cats[10]:
            payload.indirect_expense = req.budgetYear

        new_data = payload.dict(exclude_unset=True)
        updated = stored_model.copy(update=new_data)

        stored_data.update(updated)

        monthBudget.update(stored_data)
        db.commit()

    
    # Set Actual Month
    actualMonthBudget = db.query(MonthlyActualBudget).filter(
        MonthlyActualBudget.year == year,
        MonthlyActualBudget.month == month
    )

    try:
        actualMonthBudget_model = actualMonthBudget.one_or_none()
    except MultipleResultsFound:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Multiple ActualMonthBudget entries for given year/month ({year}/{month}) were found!")

    if not actualMonthBudget_model: # No ActualMonthlyBudget was found
        # Create a new Actual Monthly Budget
        payload = {}

        for c in cats:
            payload[c] = 0

        payload[req.expenses] = req.actualMonth

        newActualMonthBudget = MonthlyActualBudget(
            year                        = year,
            month                       = month,
            staff_salaries              = payload["Staff Expense (Salaries)"],
            staff_training_reg_meeting  = payload["Staff Training & Regional Meeting"],
            revenue_related             = payload["Revenue Related (Communications)"],
            it_related                  = payload["IT Related (Softwares)"],
            occupancy_related           = payload["Occupancy Related (Premises)"],
            other_transport_travel      = payload["Transport & Travel"],
            other_other                 = payload["Others"],
            indirect_expense            = payload["Indirect Expense"],
            remark                      = ""
        )

        db.add(newActualMonthBudget)
        db.commit()
        db.refresh(newActualMonthBudget)
    else: # Existing ActualMonthlyBudget was found 
        stored_data = jsonable_encoder(actualMonthBudget_model)
        stored_model = schemas.MonthlyActualBudgetIn(**stored_data)

        payload = schemas.MonthlyActualBudgetIn()

        if req.expenses == cats[1]:
            payload.staff_salaries = req.budgetYear
        elif req.expenses == cats[2]:
            payload.staff_training_reg_meeting = req.budgetYear
        elif req.expenses == cats[3]:
            payload.revenue_related = req.budgetYear
        elif req.expenses == cats[4]:
            payload.it_related = req.budgetYear
        elif req.expenses == cats[5]:
            payload.occupancy_related = req.budgetYear
        elif req.expenses == cats[7]:
            payload.other_transport_travel = req.budgetYear
        elif req.expenses == cats[8]:
            payload.other_other = req.budgetYear
        elif req.expenses == cats[10]:
            payload.indirect_expense = req.budgetYear

        new_data = payload.dict(exclude_unset=True)
        updated = stored_model.copy(update=new_data)

        stored_data.update(updated)

        actualMonthBudget.update(stored_data)
        db.commit()

# CSF
@router.get('/csf_data/api/table_data/{year}')
def get_csf_table(year: int, db: Session = Depends(get_db)):
    prjs = db.query(Project).filter(
        Project.year == year
    ).all()

    prj_ids = [p.id for p in prjs]

    csfs = db.query(CSF).filter(
        CSF.prj_id.in_(prj_ids)
    ).all()

    res = []

    for c in csfs:
        sum_atp = c.atp_1 + c.atp_2 + c.atp_3 + c.atp_4 + c.atp_5 + c.atp_6
        avg_atp = round(sum_atp / 6, 2)

        sum_ac = c.ac_1 + c.ac_2 + c.ac_3 + c.ac_4 + c.ac_5 + c.ac_6
        avg_ac = round(sum_ac / 6, 2)

        sum_paw = c.paw_1 + c.paw_2 + c.paw_3
        avg_paw = round(sum_paw / 3, 2)       

        avg = round((avg_ac + avg_atp + avg_paw)/3, 2)

        res.append({
            'id'                : str(c.id),
            'division_project'  : c.prj.div.name,
            'auditProject'      : str(c.prj_id),
            'clientName'        : c.client_name,
            'unitJabatan'       : c.client_unit,
            'TL'                : c.tl.name,
            'CSFDate'           : utils.date_to_str(c.csf_date),
            'atp1'              : c.atp_1,
            'atp2'              : c.atp_2,
            'atp3'              : c.atp_3,
            'atp4'              : c.atp_4,
            'atp5'              : c.atp_5,
            'atp6'              : c.atp_6,
            'atpOverall'        : avg_atp,
            'ac1'               : c.ac_1,
            'ac2'               : c.ac_2,
            'ac3'               : c.ac_3,
            'ac4'               : c.ac_4,
            'ac5'               : c.ac_5,
            'ac6'               : c.ac_6,
            'acOverall'         : avg_ac,
            'paw1'              : c.paw_1,
            'paw2'              : c.paw_2,
            'paw3'              : c.paw_3,
            'pawOverall'        : avg_paw,
            'overall'           : avg,
            'division_by_inv'   : c.by_invdiv_div.name
        })

    return res

@router.post('/csf_data/api/table_data', status_code=status.HTTP_201_CREATED)
def create_csf_table_entry(req: schemas.CSFInHiCoupling, db: Session = Depends(get_db)):
    invdiv_id = utils.div_str_to_divID(req.division_by_inv)
    
    if not invdiv_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Div Name not found')

    tl_emp = db.query(Employee).filter(Employee.name == req.TL)
    tl_id = tl_emp.first().id if tl_emp.first() else 1

    prj_id = utils.str_to_int_or_None(req.auditProject)
    if not prj_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Audit Project must be an ID')
    
    prj = db.query(Project).filter(Project.id == prj_id)
    if not prj.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Audit Project must be an ID of an existing project')
    
    new_csf = CSF(
        client_name         = req.clientName,
        client_unit         = req.unitJabatan,
        csf_date            = utils.str_to_datetime(req.CSFDate),
        atp_1               = req.atp1,
        atp_2               = req.atp2,
        atp_3               = req.atp3,
        atp_4               = req.atp4,
        atp_5               = req.atp5,
        atp_6               = req.atp6,
        ac_1                = req.ac1,
        ac_2                = req.ac2,
        ac_3                = req.ac3,
        ac_4                = req.ac4,
        ac_5                = req.ac5,
        ac_6                = req.ac6,
        paw_1               = req.paw1,
        paw_2               = req.paw2,
        paw_3               = req.paw3,

        prj_id              = prj_id,
        tl_id               = tl_id,
        by_invdiv_div_id    = invdiv_id
    )

    db.add(new_csf)
    db.commit()
    db.refresh(new_csf)

    return new_csf

@router.patch('/csf_data/api/table_data/{id}', status_code=status.HTTP_202_ACCEPTED)
def patch_csf_table_entry(id: int, req: schemas.CSFInHiCoupling, db: Session = Depends(get_db)):
    csf = db.query(CSF).filter(
        CSF.id == id
    )

    if not csf.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')
    
    stored_data = jsonable_encoder(csf.first())
    stored_model = schemas.CSFIn(**stored_data)

    # Data Validation
    invdiv_id = utils.div_str_to_divID(req.division_by_inv)
    
    if not invdiv_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Div Name not found')

    tl_emp = db.query(Employee).filter(Employee.name == req.TL)
    tl_id = tl_emp.first().id if tl_emp.first() else 1

    prj_id = utils.str_to_int_or_None(req.auditProject)
    if not prj_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Audit Project must be an ID')
    
    prj = db.query(Project).filter(Project.id == prj_id)
    if not prj.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Audit Project must be an ID of an existing project')
    
    dataIn = schemas.CSF(
        client_name         = req.clientName,
        client_unit         = req.unitJabatan,
        csf_date            = utils.str_to_datetime(req.CSFDate),
        atp_1               = req.atp1,
        atp_2               = req.atp2,
        atp_3               = req.atp3,
        atp_4               = req.atp4,
        atp_5               = req.atp5,
        atp_6               = req.atp6,
        ac_1                = req.ac1,
        ac_2                = req.ac2,
        ac_3                = req.ac3,
        ac_4                = req.ac4,
        ac_5                = req.ac5,
        ac_6                = req.ac6,
        paw_1               = req.paw1,
        paw_2               = req.paw2,
        paw_3               = req.paw3,

        prj_id              = prj_id,
        tl_id               = tl_id,
        by_invdiv_div_id    = invdiv_id
    )

    new_data = dataIn.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    csf.update(stored_data)
    db.commit()
    return updated

@router.delete('/csf_data/api/table_data/{id}')
def delete_csf_table_entry(id: int, db: Session = Depends(get_db)):
    c = db.query(CSF).filter(
        CSF.id == id
    )

    if not c.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')
    
    c.delete()
    db.commit()

    return {'details': 'Deleted'}

# Employee
@router.get('/employee_data/api/table_data')
def get_employee_table(db: Session = Depends(get_db)):
    emps = db.query(Employee).all()

    res = []

    for e in emps:
        as_of_now       = datetime.date.today().strftime("%m/%d/%Y")
        age             = utils.get_year_diff_to_now(e.date_of_birth)
        gen             = utils.get_gen(e.date_of_birth)
        auditUOBYears   = utils.get_year_diff_to_now(e.date_first_uob)

        # Process Certs
        certs = [
            "SMR", "CISA", "CEH", "ISO", "CHFI", 
            "IDEA", "QualifiedIA", "CBIA", "CIA", "CPA", "CA", "Others"]

        cert_res = []

        for c in certs:
            cert_res.append({
                'title': c,
                'value': 0
            })

        for c in e.emp_certifications:
            # SMR (Levels)
            smr_level = utils.extract_SMR_level(c.cert_name)
            
            if smr_level: # SMR
                cert_res[0]['value'] = smr_level
            elif c.cert_name in certs:
                index = utils.find_index(cert_res, 'title', c.cert_name)
                cert_res[index]['value'] = 1
            else:
                cert_res[-1]["value"] += 1

        smr_lvl = cert_res[0]['value']
        smr_str = f"Level {smr_lvl}" if smr_lvl else "-"

        res.append({
            "id"                          : e.id,
            "staffNIK"                    : e.staff_id,
            "staffName"                   : e.name,
            "email"                       : e.email,
            "role"                        : e.role.name,
            "divison"                     : e.part_of_div.name,
            "stream"                      : e.div_stream,
            "corporateTitle"              : e.corporate_title,
            "corporateGrade"              : e.corporate_grade,
            "dateOfBirth"                 : e.date_of_birth.strftime("%m/%d/%Y"),
            "dateStartFirstEmployment"    : e.date_first_employment.strftime("%m/%d/%Y"),
            "dateJoinUOB"                 : e.date_first_uob.strftime("%m/%d/%Y"),
            "dateJoinIAFunction"          : e.date_first_ia.strftime("%m/%d/%Y"),
            "asOfNow"                     : as_of_now,
            "age"                         : age,
            "gen"                         : gen,
            "gender"                      : e.gender,
            "auditUOBExp"                 : auditUOBYears,
            "auditNonUOBExp"              : e.year_audit_non_uob,
            "totalAuditExp"               : e.year_audit_non_uob + auditUOBYears,
            "educationLevel"              : e.edu_level,
            "educationMajor"              : e.edu_major,
            "educationCategory"           : e.edu_category,
            "RMGCertification"            : smr_str,
            "CISA"                        : cert_res[1]['value'],
            "CEH"                         : cert_res[2]['value'],
            "ISO"                         : cert_res[3]['value'],
            "CHFI"                        : cert_res[4]['value'],
            "IDEA"                        : cert_res[5]['value'],
            "QualifiedIA"                 : cert_res[6]['value'],
            "CBIA"                        : cert_res[7]['value'],
            "CIA"                         : cert_res[8]['value'],
            "CPA"                         : cert_res[9]['value'],
            "CA"                          : cert_res[10]['value'],
            "IABackgground"               : e.ia_background,
            "EABackground"                : e.ea_background,
            "active"                      : e.active
        })

    return res

@router.post('/employee_data/api/table_data')
def create_employee_table_entry(req: schemas.EmployeeInHiCoupling, db: Session = Depends(get_db)):
    div_id = utils.div_str_to_divID(req.divison)
    role_id = utils.role_str_to_id(req.role)

    new_emp = Employee(
        name    = req.staffName,
        email   = req.email,
        pw      = "pass",

        staff_id                = req.staffNIK,
        div_stream              = req.stream,
        corporate_title         = req.corporateTitle,
        corporate_grade         = req.corporateGrade,
        date_of_birth           = utils.str_to_datetime(req.dateOfBirth),
        date_first_employment   = utils.str_to_datetime(req.dateStartFirstEmployment),
        date_first_uob          = utils.str_to_datetime(req.dateJoinUOB),
        date_first_ia           = utils.str_to_datetime(req.dateJoinIAFunction),
        gender                  = req.gender,
        year_audit_non_uob      = req.auditNonUOBExp,
        edu_level               = req.educationLevel,
        edu_major               = req.educationMajor,
        edu_category            = req.educationCategory,
        ia_background           = req.IABackgground,
        ea_background           = req.EABackground,
        active                  = req.active,

        div_id = div_id,
        role_id= role_id
    )

    db.add(new_emp)
    db.commit()
    db.refresh(new_emp)

    return new_emp

@router.patch('/employee_data/api/table_data/{id}')
def patch_employee_table_entry(id: int, req: schemas.EmployeeInHiCoupling, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(
        Employee.id == req.staffID
    )

    if not emp.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')
    
    stored_data = jsonable_encoder(emp.first())
    stored_model = schemas.EmployeeIn(**stored_data)

    dataIn = schemas.Employee(
        name    = req.staffName,
        email   = req.email,
        pw      = emp.first().pw,

        staff_id                = req.staffNIK,
        div_stream              = req.stream,
        corporate_title         = req.corporateTitle,
        corporate_grade         = req.corporateGrade,
        date_of_birth           = utils.str_to_datetime(req.dateOfBirth),
        date_first_employment   = utils.str_to_datetime(req.dateStartFirstEmployment),
        date_first_uob          = utils.str_to_datetime(req.dateJoinUOB),
        date_first_ia           = utils.str_to_datetime(req.dateJoinIAFunction),
        gender                  = req.gender,
        year_audit_non_uob      = req.auditNonUOBExp,
        edu_level               = req.educationLevel,
        edu_major               = req.educationMajor,
        edu_category            = req.educationCategory,
        ia_background           = req.IABackgground,
        ea_background           = req.EABackground,
        active                  = req.active,

        div_id = utils.div_str_to_divID(req.divison),
        role_id = utils.role_str_to_id(req.role)
    )

    new_data = dataIn.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    emp.update(stored_data)
    db.commit()
    return updated

@router.delete('/employee_data/api/table_data/{id}')
def delete_employee_table_entry(id: int, db: Session = Depends(get_db)):
    e = db.query(Employee).filter(
        Employee.id == id
    )

    if not e.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')
    
    e.delete()
    db.commit()

    return {'details': 'Deleted'}

# Training
@router.get('/training_data/api/table_data/{year}')
def get_training_table(year: int, db: Session = Depends(get_db)):
    startDate   = datetime.date(year,1,1)
    endDate     = datetime.date(year,12,31)
    
    training = db.query(Training).filter(
        Training.date >= startDate,
        Training.date <= endDate
    ).all()

    res = []

    for t in training:
        divison = t.employee.part_of_div.name if t.employee else ""
        emp_name= t.employee.name if t.employee else ""
        emp_nik = t.employee.staff_id if t.employee else ""

        res.append({
            "id"                : str(t.id),
            "division"          : divison,
            "name"              : emp_name,
            "nik"               : emp_nik,
            "trainingTitle"     : t.name,
            "date"              : t.date.strftime("%m/%d/%Y"),
            "numberOfHours"     : t.duration_hours,
            "budget"            : t.budget,
            "costRealization"   : t.realization,
            "chargedByFinance"  : t.charged_by_fin,
            "mandatoryFrom"     : t.mandatory_from,
            "remark"            : t.remark
        })

    return res

@router.post('/training_data/api/table_data/')
def create_training_table_entry(req: schemas.TrainingInHiCoupling, db: Session = Depends(get_db)):    
    emp = db.query(Employee).filter(
        Employee.staff_id == req.nik
    )

    if not emp.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    emp_id = emp.first().id

    new_train = Training(
        name            = req.trainingTitle,
        date            = datetime.datetime.strptime(req.date, "%m/%d/%Y"),
        duration_hours  = req.numberOfHours,
        proof           = False,
        budget          = req.budget,
        realization     = req.costRealization,
        charged_by_fin  = req.chargedByFinance,
        remark          = req.remark,
        mandatory_from  = req.mandatoryFrom,

        emp_id          = emp_id
    )

    db.add(new_train)
    db.commit()
    db.refresh(new_train)

    return new_train

@router.patch('/training_data/api/table_data/{id}')
def patch_training_table_entry(id: int, req: schemas.TrainingInHiCoupling, db: Session = Depends(get_db)):    
    training = db.query(Training).filter(
        Training.id == id
    )

    if not training.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')
    
    stored_data = jsonable_encoder(training.first())
    stored_model = schemas.TrainingIn(**stored_data)
    
    # Get emp_id from NIK
    emp = db.query(Employee).filter(
        Employee.staff_id == req.nik
    )
        
    emp_id = emp.first().id if emp.first() else 0

    dataIn = schemas.Training(
        name            = req.trainingTitle,
        date            = datetime.datetime.strptime(req.date, "%m/%d/%Y"),
        duration_hours  = req.numberOfHours,
        proof           = False,

        budget          = req.budget,
        realization     = req.costRealization,
        charged_by_fin  = req.chargedByFinance,
        remark          = req.remark,
        mandatory_from  = req.mandatoryFrom,

        emp_id          = emp_id
    )

    new_data = dataIn.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    training.update(stored_data)
    db.commit()
    return updated

@router.delete('/training_data/api/table_data/{id}')
def delete_training_table_entry(id: int, db: Session = Depends(get_db)):
    t = db.query(Training).filter(
        Training.id == id
    )

    if not t.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')
    
    t.delete()
    db.commit()

    return {'details': 'Deleted'}

# Audit Project
@router.get('/audit_project_data/api/table_data/{year}')
def get_project_table(year: int, db: Session = Depends(get_db)):
    projects = db.query(Project).filter(
        Project.year == year
    ).all()

    res = []

    for p in projects:
        res.append({
            "id"        : str(p.id),
            "auditPlan" : p.name,
            "division"  : p.div.name,
            "status"    : p.status.name,
            "useOfDA"   : p.used_DA,
            "year"      : p.year,


            "is_carried_over" : p.is_carried_over,
            "timely_report"   : p.timely_report,
            "completion_PA"   : p.completion_PA
        })

    return res

@router.post('/audit_project_data/api/table_data')
def create_project_table_entry(req: schemas.ProjectInHiCoupling, db: Session = Depends(get_db)):
    divs    = ["WBGM", "RBA", "BRDS", "TAD", "PPA"]
    statuses= ["Not Started", "Planning", "Fieldwork", "Reporting", "Completed"]

    div_id = divs.index(req.division)+1
    status_id = statuses.index(req.status)+1

    new_prj = Project(
        name            = req.auditPlan,
        used_DA         = req.useOfDA,
        completion_PA   = req.completion_PA,
        is_carried_over = req.is_carried_over,
        timely_report   = req.timely_report,
        year            = req.year,

        status_id       = status_id,
        div_id          = div_id,
    )

    db.add(new_prj)
    db.commit()
    db.refresh(new_prj)

    return new_prj

@router.patch('/audit_project_data/api/table_data/{id}')
def patch_project_table_entry(id: int,req: schemas.ProjectInHiCoupling, db: Session = Depends(get_db)):
    divs = ["WBGM", "RBA", "BRDS", "TAD", "PPA"]
    statuses= ["Not Started", "Planning", "Fieldwork", "Reporting", "Completed"]

    prj = db.query(Project).filter(
        Project.id == id
    )

    if not prj.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')
    
    stored_data = jsonable_encoder(prj.first())
    stored_model = schemas.ProjectIn(**stored_data)
    
    div_id      = divs.index(req.division)+1
    status_id   = statuses.index(req.status)+1

    dataIn = schemas.ProjectIn(
        name            = req.auditPlan,
        used_DA         = req.useOfDA,
        completion_PA   = req.completion_PA,
        is_carried_over = req.is_carried_over,
        timely_report   = req.timely_report,
        year            = req.year,

        status_id       = status_id,
        div_id          = div_id
    )

    new_data = dataIn.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    prj.update(stored_data)
    db.commit()
    return updated

@router.delete('/audit_project_data/api/table_data/{id}')
def delete_project_table_entry(id: int, db: Session = Depends(get_db)):
    prj = db.query(Project).filter(
        Project.id == id
    )

    if not prj.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')
    
    prj.delete()
    db.commit()

    return {'details': 'Deleted'}

# Social Contribution
@router.get('/audit_contribution_data/api/table_data/{year}')
def get_contrib_table(year: int, db: Session = Depends(get_db)):
    startDate   = datetime.date(year,1,1)
    endDate     = datetime.date(year,12,31)

    contribs = db.query(SocialContrib).filter(
        SocialContrib.date >= startDate,
        SocialContrib.date <= endDate
    ).all()

    res = []

    for c in contribs:
        res.append({
            "id"        : str(c.id),
            "division"  : c.div.name,
            "category"  : c.social_type.name,
            "title"     : c.topic_name,
            "date"      : c.date.strftime("%m/%d/%Y")
        })

    return res

@router.post('/audit_contribution_data/api/table_data')
def create_contrib_table_entry(req: schemas.SocialContribHiCouplingIn, db: Session = Depends(get_db)):
    divs = ["WBGM", "RBA", "BRDS", "TAD", "PPA"]
    types = ["Audit News", "MyUOB", "Audit Bulletin"]

    div_id = divs.index(req.division)+1

    new_con = SocialContrib(
        date            = datetime.datetime.strptime(req.date, "%m/%d/%Y"),
        topic_name      = req.title,
        div_id          = divs.index(req.division) + 1,
        social_type_id  = types.index(req.category) + 1
    )

    db.add(new_con)
    db.commit()
    db.refresh(new_con)

    return new_con

@router.patch('/audit_contribution_data/api/table_data/{id}')
def patch_contrib_table_entry(id: int,req: schemas.SocialContribHiCouplingIn, db: Session = Depends(get_db)):
    divs = ["WBGM", "RBA", "BRDS", "TAD", "PPA"]
    types = ["Audit News", "MyUOB", "Audit Bulletin"]

    contrib = db.query(SocialContrib).filter(
        SocialContrib.id == id
    )

    if not contrib.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')
    
    stored_data = jsonable_encoder(contrib.first())
    stored_model = schemas.SocialContribIn(**stored_data)
    
    div_id = divs.index(req.division)+1
    social_type_id  =types.index(req.category)+1

    dataIn = schemas.SocialContribIn(
        date            = datetime.datetime.strptime(req.date, "%m/%d/%Y"),
        topic_name      = req.title,
        div_id          = div_id,
        social_type_id  = social_type_id
    )

    new_data = dataIn.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    contrib.update(stored_data)
    db.commit()
    return updated

@router.delete('/audit_contribution_data/api/table_data/{id}')
def delete_contrib_table_entry(id: int, db: Session = Depends(get_db)):
    contrib = db.query(SocialContrib).filter(
        SocialContrib.id == id
    )

    if not contrib.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')
    
    contrib.delete()
    db.commit()

    return {'details': 'Deleted'}

# BUSU Engagement Table
@router.get('/busu_data/api/table_data/{year}')
def get_busu_table(year: int, db: Session = Depends(get_db)):
    startDate   = datetime.date(year,1,1)
    endDate     = datetime.date(year,12,31)

    engs = db.query(BUSUEngagement).filter(
        BUSUEngagement.date >= startDate,
        BUSUEngagement.date <= endDate
    ).all()

    res = []
    
    for e in engs:
        res.append({
            "id"        : str(e.id),
            "division"  : e.div.name,
            "WorRM"     : e.eng_type.name,
            "activity"  : e.activity_name,
            "date"      : e.date.strftime("%m/%d/%Y")
        })
    
    return res

@router.post('/busu_data/api/table_data/')
def create_busu_table_entry(req: schemas.BUSUEngagementInHiCoupling, db: Session = Depends(get_db)):
    divs = ["WBGM", "RBA", "BRDS", "TAD", "PPA"]
    eng_types = ["Regular Meeting", "Workshop"]

    div_id = divs.index(req.division)+1

    new_eng = BUSUEngagement(
        activity_name   = req.activity,
        date            = datetime.datetime.strptime(req.date, "%m/%d/%Y"),
        proof           = False,
        
        eng_type_id     = eng_types.index(req.WorRM) + 1,

        div_id          = divs.index(req.division) + 1 
    )

    db.add(new_eng)
    db.commit()
    db.refresh(new_eng)

    return new_eng

@router.patch('/busu_data/api/table_data/{id}')
def patch_busu_table_entry(id:int, req: schemas.BUSUEngagementInHiCoupling, db: Session = Depends(get_db)):
    eng = db.query(BUSUEngagement).filter(
        BUSUEngagement.id == id
    ) 

    if not eng.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    stored_data = jsonable_encoder(eng.first())
    stored_model = schemas.BUSUEngagementIn(**stored_data)

    divs = ["WBGM", "RBA", "BRDS", "TAD", "PPA"]
    eng_types = ["Regular Meeting", "Workshop"]
    div_id =  divs.index(req.division) + 1

    dataIn = schemas.BUSUEngagementIn(
        activity_name   = req.activity,
        date            = datetime.datetime.strptime(req.date, "%m/%d/%Y"),
        proof           = False,

        eng_type_id     = eng_types.index(req.WorRM) + 1,

        div_id          = divs.index(req.division) + 1
    )

    new_data = dataIn.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    eng.update(stored_data)
    db.commit()
    return updated

@router.delete('/busu_data/api/table_data/{id}')
def delete_busu_table_entry(id:int, db: Session = Depends(get_db)):
    eng = db.query(BUSUEngagement).filter(
        BUSUEngagement.id == id
    )

    if not eng.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    eng.delete()
    db.commit()

    return {'details': 'Deleted'}

# Attrition Table
@router.get('/attrition_data/api/table_data/{year}')
def get_attr_table(year: int, db: Session = Depends(get_db)):
    attrs = db.query(YearlyAttrition).filter(
        YearlyAttrition.year == year
    )

    divs = ["WBGM", "RBA", "BRDS", "TAD", "PPA"]
    res = []

    # Init result dict
    for div in divs:
        res.append({
            "id"              : "",
            "division"        : div,
            "totalBudgetHC"   : 0,
            "totalHCNewYear"  : 0,
            "join"            : 0,
            "resign"          : 0,
            "transfer"        : 0,
            "attritionRate"   : "",
            "CurrentHC"       : 0,
        })

    for a in attrs:
        index = utils.find_index(res, "division", a.div.name)

        attr_rate = (a.resigned_count + a.transfer_count) / a.start_headcount
        attr_rate_str = str(round(attr_rate*100, 2)) + '%'

        curr_hc = a.start_headcount + a.joined_count - (a.resigned_count + a.transfer_count)

        res[index]['id']             = str(a.id)
        res[index]['totalBudgetHC']  = a.budget_headcount
        res[index]['totalHCNewYear'] = a.start_headcount
        res[index]['join']           = a.joined_count
        res[index]['resign']         = a.resigned_count
        res[index]['transfer']       = a.transfer_count
        res[index]['attritionRate']  = attr_rate_str
        res[index]['CurrentHC']      = curr_hc

    return res

@router.post('/attrition_data/api/table_data/{year}')
def create_attr_table_entry(year: int, req: schemas.YearlyAttritionInHiCoupling, db: Session = Depends(get_db)):
    divs = ["WBGM", "RBA", "BRDS", "TAD", "PPA"]

    div_id = divs.index(req.division)+1

    new_attr = YearlyAttrition(
        year                = year,
        start_headcount     = req.totalHCNewYear,
        budget_headcount    = req.totalBudgetHC,
        joined_count        = req.join,
        resigned_count      = req.resign,
        transfer_count      = req.transfer,
        div_id              = div_id
    )

    db.add(new_attr)
    db.commit()
    db.refresh(new_attr)

    return new_attr

@router.patch('/attrition_data/api/table_data/{id}', status_code=status.HTTP_202_ACCEPTED)
def patch_attr_entry(id:int, req: schemas.YearlyAttritionInHiCoupling, db: Session = Depends(get_db)):
    attr = db.query(YearlyAttrition).filter(
        YearlyAttrition.id == id
    )

    if not attr.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    stored_data = jsonable_encoder(attr.first())
    stored_model = schemas.YearlyAttritionIn(**stored_data)

    divs = ["WBGM", "RBA", "BRDS", "TAD", "PPA"]
    div_id =  divs.index(req.division) + 1

    dataIn = schemas.YearlyAttritionIn(
        start_headcount = req.totalHCNewYear,
        budget_headcount= req.totalBudgetHC,
        joined_count    = req.join,
        resigned_count  = req.resign,
        transfer_count  = req.transfer,
        div_id          = div_id
    )

    new_data = dataIn.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    attr.update(stored_data)
    db.commit()
    return updated

@router.delete('/attrition_data/api/table_data/{id}', status_code=status.HTTP_202_ACCEPTED)
def delete_attr_entry(id:int, db: Session = Depends(get_db)):
    attr = db.query(YearlyAttrition).filter(
        YearlyAttrition.id == id
    )

    if not attr.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    attr.delete()
    db.commit()

    return {'details': 'Deleted'}

# Util
@router.get('/api/title_project/{year}')
def get_project_titles(year:int, db: Session = Depends(get_db)):
    prjs = db.query(Project).filter(
        Project.year == year
    )

    res = []
    for p in prjs:
        res.append({
            'id'            : str(p.id),
            'project_title' : p.name
        })

    return res