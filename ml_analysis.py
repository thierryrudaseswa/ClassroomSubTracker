import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
import os

def load_and_analyze_data():
    # 1. Generate and Return 500,000 rows of data
    np.random.seed(42)
    num_records = 500000
    
    subjects = ['Math', 'Physics', 'Chemistry', 'Biology', 'History', 'English', 'Computer Science']
    grades = ['A', 'B', 'C', 'D', 'F']
    
    data = {
        'student_id': range(1, num_records + 1),
        'name': [f'Student_{i}' for i in range(1, num_records + 1)],
        'age': np.random.randint(15, 22, num_records),
        'grade_level': np.random.randint(9, 13, num_records),
        'enrollment_date': [datetime.now().date() - pd.Timedelta(days=np.random.randint(0, 1000)) 
                          for _ in range(num_records)],
        'gpa': np.random.uniform(2.0, 4.0, num_records),
        'attendance_rate': np.random.uniform(0.7, 1.0, num_records),
    }
    
    # Introduce some null values
    data['gpa'] = [None if np.random.random() < 0.05 else x for x in data['gpa']]
    data['attendance_rate'] = [None if np.random.random() < 0.05 else x for x in data['attendance_rate']]
    
    df = pd.DataFrame(data)
    return df

def describe_dataset(df):
    # 2. Describe the dataset
    description = {
        'basic_info': {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'column_names': list(df.columns),
            'data_types': df.dtypes.to_dict()
        },
        'null_values': df.isnull().sum().to_dict(),
        'numerical_statistics': df.describe().to_dict()
    }
    
    print("\nDataset Description:")
    print(f"Total Records: {description['basic_info']['total_rows']}")
    print(f"Total Columns: {description['basic_info']['total_columns']}")
    print("\nNull Values:")
    for col, count in description['null_values'].items():
        print(f"{col}: {count}")
    
    return description

def handle_null_values(df):
    # 3. Find and replace null values
    numerical_imputer = SimpleImputer(strategy='mean')
    
    # Handle numerical columns
    numerical_columns = ['gpa', 'attendance_rate']
    df[numerical_columns] = numerical_imputer.fit_transform(df[numerical_columns])
    
    return df

def preprocess_data(df):
    # 4. Perform basic preprocessing
    
    # Convert enrollment_date to numeric (days since earliest date)
    df['days_enrolled'] = (pd.to_datetime(df['enrollment_date']) - 
                          pd.to_datetime(df['enrollment_date']).min()).dt.days
    
    # Scale numerical features
    scaler = StandardScaler()
    numerical_columns = ['age', 'gpa', 'attendance_rate', 'days_enrolled']
    df[numerical_columns] = scaler.fit_transform(df[numerical_columns])
    
    return df

def create_features(df):
    # 5. Create new features
    
    # Academic performance categories
    df['academic_status'] = pd.qcut(df['gpa'], q=4, labels=['Poor', 'Fair', 'Good', 'Excellent'])
    
    # Attendance categories
    df['attendance_category'] = pd.qcut(df['attendance_rate'], q=3, 
                                      labels=['Low', 'Medium', 'High'])
    
    # Age groups
    df['age_group'] = pd.cut(df['age'], bins=[14, 16, 18, 22], 
                            labels=['Junior', 'Intermediate', 'Senior'])
    
    # Create performance score
    df['performance_score'] = (df['gpa'] + df['attendance_rate']) / 2
    
    return df

def create_visualizations(df):
    # Create a directory for plots if it doesn't exist
    if not os.path.exists('plots'):
        os.makedirs('plots')
    
    # Set the style
    plt.style.use('seaborn')
    
    # 1. Distribution of GPA
    plt.figure(figsize=(10, 6))
    sns.histplot(data=df, x='gpa', bins=50)
    plt.title('Distribution of GPA')
    plt.savefig('plots/gpa_distribution.png')
    plt.close()
    
    # 2. Attendance Rate vs GPA
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df.sample(1000), x='gpa', y='attendance_rate')
    plt.title('Attendance Rate vs GPA')
    plt.savefig('plots/attendance_vs_gpa.png')
    plt.close()
    
    # 3. Age Distribution by Academic Status
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=df, x='academic_status', y='age')
    plt.title('Age Distribution by Academic Status')
    plt.savefig('plots/age_by_academic_status.png')
    plt.close()
    
    # 4. Performance Score Distribution
    plt.figure(figsize=(10, 6))
    sns.histplot(data=df, x='performance_score', bins=50)
    plt.title('Distribution of Performance Scores')
    plt.savefig('plots/performance_distribution.png')
    plt.close()

def main():
    # Load data
    print("Loading dataset...")
    df = load_and_analyze_data()
    
    # Describe dataset
    print("\nAnalyzing dataset...")
    description = describe_dataset(df)
    
    # Handle null values
    print("\nHandling null values...")
    df = handle_null_values(df)
    
    # Preprocess data
    print("\nPreprocessing data...")
    df = preprocess_data(df)
    
    # Create features
    print("\nCreating new features...")
    df = create_features(df)
    
    print("\nCreating visualizations...")
    create_visualizations(df)
    print("Visualizations saved in 'plots' directory")
    
    # Save processed dataset
    print("\nSaving processed dataset...")
    df.to_csv('processed_student_data.csv', index=False)
    
    # Print final shape
    print(f"\nFinal dataset shape: {df.shape}")
    print("Features created:", [col for col in df.columns if col not in ['student_id', 'name']])

if __name__ == "__main__":
    main() 