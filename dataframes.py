import pandas as pd
import numpy as np
from datetime import datetime
import psycopg2
from sqlalchemy import create_engine
from decouple import config
import matplotlib.pyplot as plt
import seaborn as sns
import os
from urllib.parse import quote_plus

def get_database_connection():
    try:
        DB_NAME = config('DB_NAME')
        DB_USER = config('DB_USER')
        DB_PASSWORD = quote_plus(config('DB_PASSWORD'))
        DB_HOST = config('DB_HOST', default='localhost')
        DB_PORT = config('DB_PORT', default='5432')
        
        connection_string = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
        
        engine = create_engine(connection_string)
        print("Database connection established successfully!")
        return engine
    
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def load_data(engine):
    print("\n1. LOADING 500,000 ROWS OF DATA...")
    
    query = """
    SELECT 
        s.*,
        array_agg(DISTINCT sub.subject_name) as subjects,
        array_agg(DISTINCT ss.grade) as grades
    FROM students s
    LEFT JOIN student_subjects ss ON s.student_id = ss.student_id
    LEFT JOIN subjects sub ON ss.subject_id = sub.subject_id
    GROUP BY s.student_id, s.name, s.age, s.grade_level, 
             s.enrollment_date, s.gpa, s.attendance_rate
    """
    
    df = pd.read_sql_query(query, engine)
    print(f"Loaded {len(df):,} records successfully!")
    return df

def describe_dataset(df):
    print("\n2. DESCRIBING DATASET...")
    
    # Basic information
    print("\nBasic Information:")
    print(df.info())
    
    # Numerical statistics
    print("\nNumerical Statistics:")
    print(df.describe())
    
    # Null values
    print("\nNull Values Count:")
    print(df.isnull().sum())
    
    # Create visualizations directory
    if not os.path.exists('visualizations'):
        os.makedirs('visualizations')
    
    # GPA Distribution
    plt.figure(figsize=(10, 6))
    sns.histplot(data=df, x='gpa', bins=50)
    plt.title('GPA Distribution')
    plt.savefig('visualizations/gpa_distribution.png')
    plt.close()
    
    # Age vs GPA
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df, x='grade_level', y='gpa')
    plt.title('GPA by Grade Level')
    plt.savefig('visualizations/gpa_by_grade.png')
    plt.close()
    
    return df

def handle_null_values(df):
    print("\n3. HANDLING NULL VALUES...")
    
    print("Null values before:")
    print(df.isnull().sum())
    
    # Handle numerical nulls
    df['gpa'] = df['gpa'].fillna(df['gpa'].mean())
    df['attendance_rate'] = df['attendance_rate'].fillna(df['attendance_rate'].median())
    
    print("\nNull values after:")
    print(df.isnull().sum())
    
    return df

def preprocess_data(df):
    print("\n4. PREPROCESSING DATA...")
    
    # Convert enrollment_date to datetime if it's not already
    df['enrollment_date'] = pd.to_datetime(df['enrollment_date'])
    
    # Calculate days since enrollment
    df['days_enrolled'] = (datetime.now() - df['enrollment_date']).dt.days
    
    # Calculate number of subjects per student
    df['num_subjects'] = df['subjects'].apply(len)
    
    # Convert grades to GPA points
    grade_points = {'A': 4.0, 'B': 3.0, 'C': 2.0, 'D': 1.0, 'F': 0.0}
    df['average_grade_points'] = df['grades'].apply(
        lambda x: sum(grade_points[grade] for grade in x) / len(x)
    )
    
    return df

def create_features(df):
    print("\n5. CREATING NEW FEATURES...")
    
    # Academic performance categories
    df['academic_status'] = pd.qcut(df['gpa'], 
                                  q=4, 
                                  labels=['Poor', 'Fair', 'Good', 'Excellent'])
    
    # Attendance categories
    df['attendance_category'] = pd.qcut(df['attendance_rate'], 
                                      q=3, 
                                      labels=['Low', 'Medium', 'High'])
    
    # Age groups
    df['age_group'] = pd.cut(df['age'], 
                            bins=[14, 16, 18, 22], 
                            labels=['Junior', 'Intermediate', 'Senior'])
    
    # Performance score (combining GPA, attendance, and grades)
    df['performance_score'] = (
        df['gpa'] * 0.4 + 
        df['attendance_rate'] * 0.3 + 
        df['average_grade_points'] * 0.3
    )
    
    # Create visualization of new features
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=df, x='academic_status', y='performance_score')
    plt.title('Performance Score by Academic Status')
    plt.savefig('visualizations/performance_by_status.png')
    plt.close()
    
    print("\nNew features created:")
    print("- academic_status (Poor/Fair/Good/Excellent)")
    print("- attendance_category (Low/Medium/High)")
    print("- age_group (Junior/Intermediate/Senior)")
    print("- performance_score (Combined metric)")
    print("- days_enrolled")
    print("- num_subjects")
    print("- average_grade_points")
    
    return df

def main():
    # Connect to database
    engine = get_database_connection()
    if engine is None:
        return
    
    # Load data
    df = load_data(engine)
    
    # Describe dataset
    df = describe_dataset(df)
    
    # Handle null values
    df = handle_null_values(df)
    
    # Preprocess data
    df = preprocess_data(df)
    
    # Create features
    df = create_features(df)
    
    # Save processed dataset
    print("\nSaving processed dataset...")
    df.to_csv('processed_student_data.csv', index=False)
    print("Data saved to 'processed_student_data.csv'")
    
    print("\nFinal dataset shape:", df.shape)
    print("\nVisualization plots saved in 'visualizations' directory")

if __name__ == "__main__":
    main() 