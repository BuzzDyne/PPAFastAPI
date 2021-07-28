from typing import List, Optional
from pydantic import BaseModel
import datetime

class Division(BaseModel):
    name:str

class DivisionIn(BaseModel):
    name:Optional[str]

class ShowDivision(BaseModel):
    name:str

    class Config():
        orm_mode = True

class Employee(BaseModel):
    name                    :str
    email                   :str
    pw                      :str
    staff_id                :str
    div_stream              :str
    corporate_title         :str
    corporate_grade         :str
    date_of_birth           :datetime.date
    date_first_employment   :datetime.date
    date_first_uob          :datetime.date
    date_first_ia           :datetime.date
    gender                  :str
    year_audit_non_uob      :int
    edu_level               :str
    edu_major               :str
    edu_category            :str
    ia_background           :bool
    ea_background           :bool
    div_id                  :int

class EmployeeIn(BaseModel):
    name                    :Optional[str]
    email                   :Optional[str]
    pw                      :Optional[str]
    staff_id                :Optional[str]
    div_stream              :Optional[str]
    corporate_title         :Optional[str]
    corporate_grade         :Optional[str]
    date_of_birth           :Optional[datetime.date]
    date_first_employment   :Optional[datetime.date]
    date_first_uob          :Optional[datetime.date]
    date_first_ia           :Optional[datetime.date]
    gender                  :Optional[str]
    year_audit_non_uob      :Optional[int]
    edu_level               :Optional[str]
    edu_major               :Optional[str]
    edu_category            :Optional[str]
    ia_background           :Optional[bool]
    ea_background           :Optional[bool]
    div_id                  :Optional[int]

class ShowEmployee(BaseModel):
    name:str
    email:str
    part_of_div:ShowDivision

    class Config():
        orm_mode = True

class ShowEmployeeOnly(BaseModel):
    name:str
    email:str

    class Config():
        orm_mode = True

class Certification(BaseModel):
    cert_name   :str
    cert_proof  :bool
    emp_id      :int

class CertificationIn(BaseModel):
    cert_name   :Optional[str]
    cert_proof  :Optional[bool]
    emp_id      :Optional[int]

class Login(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Trainings
class Training(BaseModel):
    name:str
    duration_days:float
    date:datetime.date
    proof:bool
    emp_id:int

class TrainingIn(BaseModel):
    name: Optional[str]
    duration_days: Optional[float]
    date: Optional[datetime.date]
    proof: Optional[bool]
    emp_id: Optional[int]

class ShowTraining(BaseModel):
    name:str
    duration_days:float
    date:datetime.date
    proof:bool
    emp_id:int
    employee: ShowEmployeeOnly
    
    class Config():
        orm_mode = True

class TrainingTarget(BaseModel):
    year:int
    target_days:float
    emp_id:int

class TrainingTargetIn(BaseModel):
    year:Optional[int]
    target_days:Optional[float]
    emp_id:Optional[int]

class TrainingBudget(BaseModel):
    budget          :float
    realization     :float
    charged_by_fin  :float

    training_id     :int

class TrainingBudgetIn(BaseModel):
    budget          :Optional[float]
    realization     :Optional[float]
    charged_by_fin  :Optional[float]

    training_id     :Optional[int]

class DebugParent(BaseModel):
    first_name:str
    last_name:str

class DebugParentIn(BaseModel):
    first_name:Optional[str]
    last_name:Optional[str]

# Social Contributions
class SocialType(BaseModel):
    name        :str

class SocialTypeIn(BaseModel):
    name        :Optional[str]

class ShowSocialType(BaseModel):
    name        :str

    class Config():
        orm_mode = True

class SocialContrib(BaseModel):
    date        :datetime.date
    topic_name  :str
    div_id      :int
    social_type_id:int

class SocialContribIn(BaseModel):
    date        :Optional[datetime.date]
    topic_name  :Optional[str]
    div_id      :Optional[int]
    social_type_id:Optional[int]

class ShowSocialContrib(BaseModel):
    date        :str
    topic_name  :str
    div         :ShowDivision
    social_type :ShowSocialType

    class Config():
        orm_mode = True

# Attrition
class MonthlyAttrition(BaseModel):
    joined_count    :int
    resigned_count  :int
    transfer_count  :int
    month           :int
    year            :int

    div_id          :int

class MonthlyAttritionIn(BaseModel):
    joined_count    :Optional[int]
    resigned_count  :Optional[int]
    transfer_count  :Optional[int]
    month           :Optional[int]
    year            :Optional[int]

    div_id          :Optional[int]

class YearlyAttritionConst(BaseModel):
    year                :int
    start_headcount     :int
    budget_headcount    :int
    
    div_id              :int

class YearlyAttritionConstIn(BaseModel):
    year                :Optional[int]
    start_headcount     :Optional[int]
    budget_headcount    :Optional[int]
    
    div_id              :Optional[int]

# BUSU Engagement
class EngagementType(BaseModel):
    name :str

class EngagementTypeIn(BaseModel):
    name :Optional[str]

class BUSUEngagement(BaseModel):
    activity_name   : str
    date            : datetime.date
    proof           : bool

    eng_type_id     : int

    div_id          : int

class BUSUEngagementIn(BaseModel):
    activity_name   : Optional[str]
    date            : Optional[datetime.date]
    proof           : Optional[bool]

    eng_type_id     : Optional[int]

    div_id          : Optional[int]

# Audit Projects
class ProjectStatus(BaseModel):
    name: str

class ProjectStatusIn(BaseModel):
    name: Optional[str]

class Project(BaseModel):
    name            :str
    used_DA         :bool
    completion_PA   :bool
    is_carried_over :bool
    timely_report   :bool
    year            :int

    status_id       :int
    div_id          :int

class ProjectIn(BaseModel):
    name            :Optional[str]
    used_DA         :Optional[bool]
    completion_PA   :Optional[bool]
    is_carried_over :Optional[bool]
    timely_report   :Optional[bool]
    year            :Optional[int]

    status_id       :Optional[int]
    div_id          :Optional[int]

# Budgets
class MonthlyBudget(BaseModel):
    year                        :int
    month                       :int
    staff_salaries              :float
    staff_training_reg_meeting  :float
    revenue_related             :float
    it_related                  :float
    occupancy_related           :float
    other_transport_travel      :float
    other_other                 :float
    indirect_expense            :float

class MonthlyBudgetIn(BaseModel):
    year                        :Optional[int]
    month                       :Optional[int]
    staff_salaries              :Optional[float]
    staff_training_reg_meeting  :Optional[float]
    revenue_related             :Optional[float]
    it_related                  :Optional[float]
    occupancy_related           :Optional[float]
    other_transport_travel      :Optional[float]
    other_other                 :Optional[float]
    indirect_expense            :Optional[float]

class MonthlyActualBudget(BaseModel):
    year                        :int
    month                       :int
    staff_salaries              :float
    staff_training_reg_meeting  :float
    revenue_related             :float
    it_related                  :float
    occupancy_related           :float
    other_transport_travel      :float
    other_other                 :float
    indirect_expense            :float

class MonthlyActualBudgetIn(BaseModel):
    year                        :Optional[int]
    month                       :Optional[int]
    staff_salaries              :Optional[float]
    staff_training_reg_meeting  :Optional[float]
    revenue_related             :Optional[float]
    it_related                  :Optional[float]
    occupancy_related           :Optional[float]
    other_transport_travel      :Optional[float]
    other_other                 :Optional[float]
    indirect_expense            :Optional[float]

# QAIP
class QAIP(BaseModel):
    qaip_type                   :str
    project_name                :str
    qa_result                   :int

    qaf_category_clarity        :bool
    qaf_category_completeness   :bool
    qaf_category_consistency    :bool
    qaf_category_others         :bool
    qaf_stage_planning          :bool
    qaf_stage_fieldwork         :bool
    qaf_stage_reporting         :bool
    qaf_stage_post_audit_act    :bool
    qaf_deliverables_1a         :bool
    qaf_deliverables_1b         :bool
    qaf_deliverables_1c         :bool
    qaf_deliverables_1d         :bool
    qaf_deliverables_1e         :bool
    qaf_deliverables_1f         :bool
    qaf_deliverables_1g         :bool
    qaf_deliverables_1h         :bool
    qaf_deliverables_1i         :bool
    qaf_deliverables_1j         :bool
    qaf_deliverables_1k         :bool
    qaf_deliverables_2          :bool
    qaf_deliverables_3          :bool
    qaf_deliverables_4          :bool
    qaf_deliverables_5          :bool
    qaf_deliverables_6          :bool
    qaf_deliverables_7          :bool
    issue_count                 :int
    qa_sample                   :bool

    tl_id                       :int

class QAIPIn(BaseModel):
    qaip_type                   :Optional[str]
    project_name                :Optional[str]
    qa_result                   :Optional[int]

    qaf_category_clarity        :Optional[bool]
    qaf_category_completeness   :Optional[bool]
    qaf_category_consistency    :Optional[bool]
    qaf_category_others         :Optional[bool]
    qaf_stage_planning          :Optional[bool]
    qaf_stage_fieldwork         :Optional[bool]
    qaf_stage_reporting         :Optional[bool]
    qaf_stage_post_audit_act    :Optional[bool]
    qaf_deliverables_1a         :Optional[bool]
    qaf_deliverables_1b         :Optional[bool]
    qaf_deliverables_1c         :Optional[bool]
    qaf_deliverables_1d         :Optional[bool]
    qaf_deliverables_1e         :Optional[bool]
    qaf_deliverables_1f         :Optional[bool]
    qaf_deliverables_1g         :Optional[bool]
    qaf_deliverables_1h         :Optional[bool]
    qaf_deliverables_1i         :Optional[bool]
    qaf_deliverables_1j         :Optional[bool]
    qaf_deliverables_1k         :Optional[bool]
    qaf_deliverables_2          :Optional[bool]
    qaf_deliverables_3          :Optional[bool]
    qaf_deliverables_4          :Optional[bool]
    qaf_deliverables_5          :Optional[bool]
    qaf_deliverables_6          :Optional[bool]
    qaf_deliverables_7          :Optional[bool]
    issue_count                 :Optional[int]
    qa_sample                   :Optional[bool]

    tl_id                       :Optional[int]

class QAIPHeadDiv(BaseModel):
    div_head: str
    qaip_id : int

class QAIPHeadDivIn(BaseModel):
    div_head: Optional[str]
    qaip_id : Optional[int]

# CSF
class CSF(BaseModel):
    audit_project_name  :str
    client_name         :str
    client_unit         :str
    csf_date            :datetime.date
    atp_1               :float
    atp_2               :float
    atp_3               :float
    atp_4               :float
    atp_5               :float
    atp_6               :float
    ac_1                :float
    ac_2                :float
    ac_3                :float
    ac_4                :float
    ac_5                :float
    ac_6                :float
    paw_1               :float
    paw_2               :float
    paw_3               :float

    tl_id               :int
    by_prj_div_id       :int
    by_invdiv_div_id    :int

class CSFIn(BaseModel):
    audit_project_name  :Optional[str]
    client_name         :Optional[str]
    client_unit         :Optional[str]
    csf_date            :Optional[datetime.date]
    atp_1               :Optional[float]
    atp_2               :Optional[float]
    atp_3               :Optional[float]
    atp_4               :Optional[float]
    atp_5               :Optional[float]
    atp_6               :Optional[float]
    ac_1                :Optional[float]
    ac_2                :Optional[float]
    ac_3                :Optional[float]
    ac_4                :Optional[float]
    ac_5                :Optional[float]
    ac_6                :Optional[float]
    paw_1               :Optional[float]
    paw_2               :Optional[float]
    paw_3               :Optional[float]
    
    tl_id               :Optional[int]
    by_prj_div_id       :Optional[int]
    by_invdiv_div_id    :Optional[int]