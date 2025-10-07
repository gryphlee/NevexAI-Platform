from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, Form
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
import pandas as pd
import bcrypt
from typing import List, Dict, Any
from sqlalchemy import create_engine, text
import io
import json
import os
from fastapi.middleware.cors import CORSMiddleware
import joblib
import numpy as np

# --- App Initialization ---
app = FastAPI(
    title="Student Intervention System API",
    description="The backend service for handling data, authentication, and analysis.",
    version="1.0.0"
)

# --- CORS MIDDLEWARE SETUP ---
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- File Paths & DB Engine ---
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(ROOT_DIR, 'data')
RESOURCES_FILE = os.path.join(DATA_DIR, 'resources.json')
RULES_FILE = os.path.join(DATA_DIR, 'rules.json')
METRICS_FILE = os.path.join(DATA_DIR, 'metrics_config.json')
CASES_FILE = os.path.join(DATA_DIR, 'cases.json')
DB_URI = f'sqlite:///{os.path.join(ROOT_DIR, "university.db")}'
engine = create_engine(DB_URI)
STREAMLIT_APP_URL = "http://localhost:8501"

os.makedirs(DATA_DIR, exist_ok=True)


# --- Pydantic Models ---
class Token(BaseModel):
    access_token: str
    token_type: str

class Student(BaseModel):
    student_id: int = 0
    quiz_avg: int = 0
    assignment_submissions: int = 0
    attendance_percentage: int = 0
    lms_hours: int = 0
    at_risk: int = 0
    at_risk_status: str = "N/A"
    parent_username: str | None = None
    department: str | None = None
    year_level: str | None = None
    week: int | None = None

class UserIn(BaseModel):
    username: str
    password: str
    role: str
    student_id: str | None = None

class Resource(BaseModel):
    title: str
    link: str
    type: str
    tags: List[str]

class Rule(BaseModel):
    conditions: List[Dict[str, Any]]
    action: str

class Metric(BaseModel):
    name: str
    type: str

class LinkParentRequest(BaseModel):
    student_id: int
    parent_username: str

 

# --- Helper Functions ---
def verify_password(plain_password, hashed_password_str):
    if isinstance(hashed_password_str, str):
        hashed_password_bytes = hashed_password_str.encode('utf-8')
    else:
        hashed_password_bytes = hashed_password_str
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password_bytes)

def get_user(username: str):
    try:
        query = text("SELECT * FROM users WHERE username = :username")
        with engine.connect() as connection:
            users_df = pd.read_sql(query, connection, params={"username": username})
        if not users_df.empty:
            return users_df.iloc[0]
    except Exception as e:
        print(f"Error getting user from DB: {e}")
    return None

def load_json(filepath, default_data):
    try:
        with open(filepath, 'r') as f: return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError): return default_data

def save_json(filepath, data):
    with open(filepath, 'w') as f: json.dump(data, f, indent=4)

# --- API Endpoints ---

@app.get("/")
async def root():
    return {"message": "Nevex AI Backend is running."}

@app.post("/token", response_model=Token)
async def login_for_streamlit_app(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user(form_data.username)
    if user is None or not verify_password(form_data.password, user['password']):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    
    student_id_val = user.get('student_id', '')
    access_token = f"{user['username']}:{user['role']}:{'' if pd.isna(student_id_val) else student_id_val}"
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/login-redirect")
async def login_for_redirect(username: str = Form(...), password: str = Form(...)):
    user = get_user(username)
    if user is None or not verify_password(password, user['password']):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    
    return RedirectResponse(url=STREAMLIT_APP_URL, status_code=status.HTTP_303_SEE_OTHER)

# --- USER MANAGEMENT ENDPOINTS ---
@app.get("/users")
async def get_all_users():
    try:
        users_df = pd.read_sql('users', engine)
        return users_df[['username', 'role', 'student_id']].fillna('N/A').to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not fetch users: {e}")

@app.post("/users")
async def create_user(user: UserIn):
    try:
        check_query = text("SELECT username FROM users WHERE username = :username")
        with engine.connect() as connection:
            existing_user = pd.read_sql(check_query, connection, params={"username": user.username})
        if not existing_user.empty:
            raise HTTPException(status_code=400, detail="Username already exists")
        hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
        new_user_data = {
            'username': user.username, 
            'password': hashed_password.decode('utf-8'), 
            'role': user.role, 
            'student_id': user.student_id if user.student_id else None
        }
        new_user_df = pd.DataFrame([new_user_data])
        new_user_df.to_sql('users', engine, if_exists='append', index=False)
        return {"message": f"User '{user.username}' created successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create user: {e}")

@app.delete("/users/{username}")
async def delete_user(username: str):
    try:
        user_to_delete = get_user(username)
        if user_to_delete is None:
            raise HTTPException(status_code=404, detail="User not found")
        delete_query = text("DELETE FROM users WHERE username = :username")
        with engine.connect() as connection:
            connection.execute(delete_query, {"username": username})
            connection.commit()
        return {"message": f"User '{username}' deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete user: {e}")

# --- STUDENT DATA ENDPOINTS ---
@app.get("/students", response_model=List[Student])
async def get_all_students():
    try:
        students_df = pd.read_sql('students', engine)
        model_fields = Student.model_fields.keys()
        for col in model_fields:
            if col not in students_df.columns:
                default_value = Student.model_fields[col].default
                students_df[col] = default_value
        students_df.fillna({'quiz_avg': 0, 'assignment_submissions': 0, 'attendance_percentage': 0, 'lms_hours': 0, 'at_risk': 0, 'at_risk_status': 'N/A'}, inplace=True)
        return students_df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not retrieve student data: {e}")

@app.post("/students/upload")
async def upload_students_data(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        new_df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        updated_count = 0; inserted_count = 0
        with engine.connect() as connection:
            trans = connection.begin()
            for index, row in new_df.iterrows():
                student_id = row['student_id']
                exists_query = text("SELECT 1 FROM students WHERE student_id = :sid")
                result = connection.execute(exists_query, {"sid": student_id}).scalar_one_or_none()
                row_dict = {k: (v.item() if hasattr(v, 'item') else v) for k, v in row.items()}
                if result:
                    update_stmt = text("UPDATE students SET quiz_avg = :quiz_avg, assignment_submissions = :assignment_submissions, attendance_percentage = :attendance_percentage, lms_hours = :lms_hours, department = :department, year_level = :year_level, at_risk_status = :at_risk_status WHERE student_id = :student_id")
                    connection.execute(update_stmt, row_dict); updated_count += 1
                else:
                    insert_stmt = text(f"INSERT INTO students ({', '.join(row.index)}) VALUES ({', '.join([f':{col}' for col in row.index])})")
                    connection.execute(insert_stmt, row_dict); inserted_count += 1
            trans.commit()
        return {"message": f"Import complete! {inserted_count} new students added, {updated_count} existing students updated."}
    except Exception as e:
        import traceback; print(traceback.format_exc()); raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to process file: {str(e)}")

@app.post("/students/link-parent")
async def link_parent_to_student(request: LinkParentRequest):
    try:
        with engine.connect() as connection:
            trans = connection.begin()
            df = pd.read_sql_table('students', connection)
            if 'parent_username' not in df.columns: df['parent_username'] = None
            df['student_id'] = df['student_id'].astype(int)
            if request.student_id not in df['student_id'].values: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student ID not found")
            df.loc[df['student_id'] == request.student_id, 'parent_username'] = request.parent_username
            df.to_sql('students', connection, if_exists='replace', index=False)
            trans.commit()
        return {"message": f"Successfully linked Student ID {request.student_id} to Parent '{request.parent_username}'"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to link accounts: {e}")

# --- OTHER MANAGEMENT ENDPOINTS ---
@app.get("/resources", response_model=List[Resource])
async def get_resources(): return load_json(RESOURCES_FILE, [])
@app.post("/resources")
async def save_resources(resources: List[Resource]): save_json(RESOURCES_FILE, [res.model_dump() for res in resources]); return {"message": "Resources saved successfully."}
@app.get("/rules", response_model=List[Rule])
async def get_rules(): return load_json(RULES_FILE, [])
@app.post("/rules")
async def save_rules(rules: List[Rule]): save_json(RULES_FILE, [rule.model_dump() for rule in rules]); return {"message": "Rules saved successfully."}
@app.get("/metrics", response_model=List[Metric])
async def get_metrics():
    default_metrics = [{"name": "quiz_avg", "type": "Numerical"}, {"name": "attendance_percentage", "type": "Numerical"}, {"name": "assignment_submissions", "type": "Numerical"}, {"name": "lms_hours", "type": "Numerical"}, {"name": "department", "type": "Categorical"}, {"name": "year_level", "type": "Categorical"}]
    return load_json(METRICS_FILE, default_metrics)
@app.post("/metrics")
async def save_metrics(metrics: List[Metric]): save_json(METRICS_FILE, [metric.model_dump() for metric in metrics]); return {"message": "Metrics saved successfully."}
@app.get("/api/dashboard-stats")
async def get_dashboard_stats(): return { "successRate": 73, "interventionSpeed": 2.1, "agentSuccessRate": 87, "agentPerformance": { "activeAgents": "20+", "specializations": { "math": 87, "empathy": 81, "data": 79, "resource": 85 } }, "detectionVsManual": "6x", "multiAgentDebates": 143 }

 







