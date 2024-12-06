from faker import Faker
import psycopg2
from decouple import config
import random
from datetime import datetime, timedelta
import numpy as np
from tqdm import tqdm

# Initialize Faker
fake = Faker()

def get_database_connection():
    try:
        # Get database credentials from .env
        DB_NAME = config('DB_NAME')
        DB_USER = config('DB_USER')
        DB_PASSWORD = config('DB_PASSWORD')
        DB_HOST = config('DB_HOST', default='localhost')
        DB_PORT = config('DB_PORT', default='5432')
        
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        print("Database connection established successfully!")
        return conn
    
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def generate_student_data(num_records=500000):
    print("\nGenerating student data...")
    
    # Prepare the SQL statement
    insert_student = """
    INSERT INTO students (name, age, grade_level, enrollment_date, gpa, attendance_rate)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    
    students_data = []
    for _ in tqdm(range(num_records)):
        # Generate random student data
        name = fake.name()
        age = random.randint(15, 22)
        grade_level = random.randint(9, 12)
        
        # Generate enrollment date within last 4 years
        enrollment_date = fake.date_between(
            start_date=datetime.now() - timedelta(days=4*365),
            end_date=datetime.now()
        )
        
        # Generate GPA and attendance rate with some null values
        gpa = None if random.random() < 0.05 else round(random.uniform(2.0, 4.0), 2)
        attendance_rate = None if random.random() < 0.05 else round(random.uniform(0.7, 1.0), 2)
        
        students_data.append((name, age, grade_level, enrollment_date, gpa, attendance_rate))
    
    return insert_student, students_data

def generate_subjects():
    subjects = [
        'Mathematics',
        'Physics',
        'Chemistry',
        'Biology',
        'History',
        'English',
        'Computer Science',
        'Literature',
        'Geography',
        'Economics'
    ]
    
    insert_subject = "INSERT INTO subjects (subject_name) VALUES (%s)"
    subjects_data = [(subject,) for subject in subjects]
    
    return insert_subject, subjects_data

def generate_student_subjects(cursor, num_students):
    print("\nGenerating student-subject relationships...")
    
    # Get all subject IDs
    cursor.execute("SELECT subject_id FROM subjects")
    subject_ids = [row[0] for row in cursor.fetchall()]
    
    insert_student_subject = """
    INSERT INTO student_subjects (student_id, subject_id, grade)
    VALUES (%s, %s, %s)
    """
    
    student_subjects_data = []
    grades = ['A', 'B', 'C', 'D', 'F']
    
    for student_id in tqdm(range(1, num_students + 1)):
        # Each student takes 3-6 random subjects
        num_subjects = random.randint(3, 6)
        chosen_subjects = random.sample(subject_ids, num_subjects)
        
        for subject_id in chosen_subjects:
            grade = random.choices(grades, weights=[0.2, 0.3, 0.3, 0.15, 0.05])[0]
            student_subjects_data.append((student_id, subject_id, grade))
    
    return insert_student_subject, student_subjects_data

def main():
    # Connect to database
    conn = get_database_connection()
    if conn is None:
        return
    
    cursor = conn.cursor()
    
    try:
        # Generate and insert subjects
        print("\nInserting subjects...")
        insert_subject, subjects_data = generate_subjects()
        cursor.executemany(insert_subject, subjects_data)
        
        # Generate and insert students
        print("\nInserting students...")
        insert_student, students_data = generate_student_data(500000)
        cursor.executemany(insert_student, students_data)
        
        # Generate and insert student-subject relationships
        insert_student_subject, student_subjects_data = generate_student_subjects(cursor, 500000)
        print("\nInserting student-subject relationships...")
        cursor.executemany(insert_student_subject, student_subjects_data)
        
        # Commit the changes
        conn.commit()
        print("\nData generation completed successfully!")
        
        # Print some statistics
        cursor.execute("SELECT COUNT(*) FROM students")
        student_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM subjects")
        subject_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM student_subjects")
        relationship_count = cursor.fetchone()[0]
        
        print(f"\nGenerated:")
        print(f"- {student_count:,} students")
        print(f"- {subject_count} subjects")
        print(f"- {relationship_count:,} student-subject relationships")
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main() 