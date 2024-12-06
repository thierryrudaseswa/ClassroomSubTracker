from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import psycopg2
from decouple import config
from typing import List, Optional
from pydantic import BaseModel

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for response
class Student(BaseModel):
    student_id: int
    name: str
    age: int
    grade_level: int
    enrollment_date: str
    gpa: float
    attendance_rate: float
    subjects: List[str]
    grades: List[str]
    academic_status: str
    performance_score: float

def get_database_connection():
    return psycopg2.connect(
        dbname=config('DB_NAME'),
        user=config('DB_USER'),
        password=config('DB_PASSWORD'),
        host=config('DB_HOST'),
        port=config('DB_PORT')
    )

@app.get("/")
def read_root():
    return {"message": "Student Data API"}

@app.get("/students", response_model=List[Student])
async def get_students(
    page: int = 1, 
    limit: int = 10,
    search: Optional[str] = None,
    min_gpa: Optional[float] = None,
    max_gpa: Optional[float] = None
):
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        
        # Base query
        query = """
        SELECT 
            s.*,
            array_agg(DISTINCT sub.subject_name) as subjects,
            array_agg(DISTINCT ss.grade) as grades
        FROM students s
        LEFT JOIN student_subjects ss ON s.student_id = ss.student_id
        LEFT JOIN subjects sub ON ss.subject_id = sub.subject_id
        """
        
        # Add WHERE clauses based on filters
        where_clauses = []
        params = []
        
        if search:
            where_clauses.append("s.name ILIKE %s")
            params.append(f"%{search}%")
            
        if min_gpa is not None:
            where_clauses.append("s.gpa >= %s")
            params.append(min_gpa)
            
        if max_gpa is not None:
            where_clauses.append("s.gpa <= %s")
            params.append(max_gpa)
            
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
            
        # Add GROUP BY and pagination
        query += """
        GROUP BY s.student_id, s.name, s.age, s.grade_level, 
                 s.enrollment_date, s.gpa, s.attendance_rate
        ORDER BY s.student_id
        LIMIT %s OFFSET %s
        """
        
        # Add pagination parameters
        params.extend([limit, (page - 1) * limit])
        
        # Execute query
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Convert to list of dictionaries
        students = []
        for row in rows:
            student = {
                "student_id": row[0],
                "name": row[1],
                "age": row[2],
                "grade_level": row[3],
                "enrollment_date": str(row[4]),
                "gpa": float(row[5]) if row[5] else None,
                "attendance_rate": float(row[6]) if row[6] else None,
                "subjects": row[7] if row[7] else [],
                "grades": row[8] if row[8] else [],
                "academic_status": get_academic_status(row[5]),
                "performance_score": calculate_performance_score(row[5], row[6])
            }
            students.append(student)
            
        return students
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        conn.close()

def get_academic_status(gpa):
    if gpa is None:
        return "Unknown"
    gpa = float(gpa)
    if gpa >= 3.5:
        return "Excellent"
    elif gpa >= 3.0:
        return "Good"
    elif gpa >= 2.5:
        return "Fair"
    else:
        return "Poor"

def calculate_performance_score(gpa, attendance):
    if gpa is None or attendance is None:
        return None
    return (float(gpa) * 0.7) + (float(attendance) * 0.3)

@app.get("/students/stats")
async def get_stats():
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        
        # Get basic statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_students,
                AVG(gpa) as avg_gpa,
                AVG(attendance_rate) as avg_attendance,
                COUNT(DISTINCT grade_level) as grade_levels
            FROM students
        """)
        
        stats = cursor.fetchone()
        
        return {
            "total_students": stats[0],
            "average_gpa": float(stats[1]) if stats[1] else None,
            "average_attendance": float(stats[2]) if stats[2] else None,
            "grade_levels": stats[3]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 