import React, { useState, useEffect } from 'react';
import { Table, Input, Select, Pagination, Card, Row, Col, Spin } from 'antd';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import './App.css';

const { Search } = Input;
const { Option } = Select;

function App() {
  const [students, setStudents] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [search, setSearch] = useState('');
  const [minGpa, setMinGpa] = useState(null);
  const [maxGpa, setMaxGpa] = useState(null);

  // Columns for the student table
  const columns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'Age',
      dataIndex: 'age',
      key: 'age',
    },
    {
      title: 'Grade Level',
      dataIndex: 'grade_level',
      key: 'grade_level',
    },
    {
      title: 'GPA',
      dataIndex: 'gpa',
      key: 'gpa',
      render: (gpa) => gpa?.toFixed(2) || 'N/A',
    },
    {
      title: 'Attendance Rate',
      dataIndex: 'attendance_rate',
      key: 'attendance_rate',
      render: (rate) => rate ? `${(rate * 100).toFixed(1)}%` : 'N/A',
    },
    {
      title: 'Academic Status',
      dataIndex: 'academic_status',
      key: 'academic_status',
      render: (status) => (
        <span className={`status-${status.toLowerCase()}`}>
          {status}
        </span>
      ),
    },
    {
      title: 'Subjects',
      dataIndex: 'subjects',
      key: 'subjects',
      render: (subjects) => subjects.join(', '),
    },
  ];

  // Fetch students data
  const fetchStudents = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page,
        limit: pageSize,
        ...(search && { search }),
        ...(minGpa && { min_gpa: minGpa }),
        ...(maxGpa && { max_gpa: maxGpa }),
      });

      const response = await fetch(`http://localhost:8000/students?${params}`);
      const data = await response.json();
      setStudents(data);
    } catch (error) {
      console.error('Error fetching students:', error);
    } finally {
      setLoading(false);
    }
  };

  // Fetch statistics
  const fetchStats = async () => {
    try {
      const response = await fetch('http://localhost:8000/students/stats');
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  useEffect(() => {
    fetchStudents();
    fetchStats();
  }, [page, pageSize, search, minGpa, maxGpa]);

  return (
    <div className="app">
      <h1>Student Data Dashboard</h1>

      {/* Statistics Cards */}
      {stats && (
        <Row gutter={16} className="stats-row">
          <Col span={6}>
            <Card title="Total Students">
              {stats.total_students.toLocaleString()}
            </Card>
          </Col>
          <Col span={6}>
            <Card title="Average GPA">
              {stats.average_gpa?.toFixed(2) || 'N/A'}
            </Card>
          </Col>
          <Col span={6}>
            <Card title="Average Attendance">
              {stats.average_attendance ? 
                `${(stats.average_attendance * 100).toFixed(1)}%` : 
                'N/A'}
            </Card>
          </Col>
          <Col span={6}>
            <Card title="Grade Levels">
              {stats.grade_levels}
            </Card>
          </Col>
        </Row>
      )}

      {/* Filters */}
      <div className="filters">
        <Search
          placeholder="Search by name"
          onSearch={value => {
            setSearch(value);
            setPage(1);
          }}
          style={{ width: 200 }}
        />
        <Select
          placeholder="Min GPA"
          style={{ width: 120 }}
          onChange={value => {
            setMinGpa(value);
            setPage(1);
          }}
          allowClear
        >
          {[2.0, 2.5, 3.0, 3.5].map(value => (
            <Option key={value} value={value}>{value.toFixed(1)}</Option>
          ))}
        </Select>
        <Select
          placeholder="Max GPA"
          style={{ width: 120 }}
          onChange={value => {
            setMaxGpa(value);
            setPage(1);
          }}
          allowClear
        >
          {[2.5, 3.0, 3.5, 4.0].map(value => (
            <Option key={value} value={value}>{value.toFixed(1)}</Option>
          ))}
        </Select>
      </div>

      {/* Students Table */}
      <Spin spinning={loading}>
        <Table
          dataSource={students}
          columns={columns}
          rowKey="student_id"
          pagination={false}
        />
      </Spin>

      {/* Pagination */}
      <Pagination
        current={page}
        pageSize={pageSize}
        total={stats?.total_students || 0}
        onChange={(newPage, newPageSize) => {
          setPage(newPage);
          setPageSize(newPageSize);
        }}
        showSizeChanger
        showTotal={(total, range) => 
          `${range[0]}-${range[1]} of ${total} students`
        }
      />
    </div>
  );
}

export default App; 