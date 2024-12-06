from fastapi import FastAPI, Path, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import pandas as pd
import numpy as np
from datetime import datetime
import random

app = FastAPI()


# Generate synthetic data for 500,000 students
def generate_sample_data():
    np.random.seed(42)
    num_records = 500000

    subjects = [
        "Math",
        "Physics",
        "Chemistry",
        "Biology",
        "History",
        "English",
        "Computer Science",
    ]
    grades = ["A", "B", "C", "D", "F"]

    data = {
        "student_id": range(1, num_records + 1),
        "name": [f"Student_{i}" for i in range(1, num_records + 1)],
        "age": np.random.randint(15, 22, num_records),
        "grade_level": np.random.randint(9, 13, num_records),
        "enrollment_date": [
            datetime.now().date() - pd.Timedelta(days=np.random.randint(0, 1000))
            for _ in range(num_records)
        ],
        "gpa": np.random.uniform(2.0, 4.0, num_records),
        "attendance_rate": np.random.uniform(0.7, 1.0, num_records),
        "subjects": [
            [random.choice(subjects) for _ in range(random.randint(3, 6))]
            for _ in range(num_records)
        ],
        "grades": [
            [random.choice(grades) for _ in range(random.randint(3, 6))]
            for _ in range(num_records)
        ],
    }

    # Introduce some null values
    data["gpa"] = [None if random.random() < 0.05 else x for x in data["gpa"]]
    data["attendance_rate"] = [
        None if random.random() < 0.05 else x for x in data["attendance_rate"]
    ]

    return pd.DataFrame(data)


# Initialize the dataset
df = generate_sample_data()


# Data preprocessing functions
def preprocess_data():
    global df
    # Handle null values
    df["gpa"].fillna(df["gpa"].mean(), inplace=True)
    df["attendance_rate"].fillna(df["attendance_rate"].median(), inplace=True)

    # Create new features
    df["academic_status"] = df["gpa"].apply(
        lambda x: "Good" if x >= 3.0 else "Needs Improvement"
    )
    df["attendance_status"] = df["attendance_rate"].apply(
        lambda x: "Regular" if x >= 0.8 else "Irregular"
    )

    return {"message": "Data preprocessing completed successfully"}


# New Pydantic models
class Subject(BaseModel):
    name: str
    grade: str


class Student(BaseModel):
    name: str
    age: int
    grade_level: int
    subjects: List[Subject]
    gpa: Optional[float] = None
    attendance_rate: Optional[float] = None


# New endpoints
@app.get("/dataset/description")
def get_dataset_description():
    return {
        "total_records": len(df),
        "columns": list(df.columns),
        "summary_statistics": df.describe().to_dict(),
        "null_values": df.isnull().sum().to_dict(),
    }


@app.get("/dataset/sample")
def get_dataset_sample(n: int = 10):
    return df.head(n).to_dict(orient="records")


@app.post("/dataset/preprocess")
def perform_preprocessing():
    return preprocess_data()


@app.get("/students/performance")
def get_student_performance(min_gpa: Optional[float] = None):
    if min_gpa:
        filtered_df = df[df["gpa"] >= min_gpa]
        return {
            "total_students": len(filtered_df),
            "average_gpa": filtered_df["gpa"].mean(),
            "average_attendance": filtered_df["attendance_rate"].mean(),
        }
    return {
        "total_students": len(df),
        "average_gpa": df["gpa"].mean(),
        "average_attendance": df["attendance_rate"].mean(),
    }
