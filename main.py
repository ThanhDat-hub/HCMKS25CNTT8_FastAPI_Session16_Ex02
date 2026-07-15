# ================== PHẦN 1: BÁO CÁO LỖI ==================

# Lỗi 1: Quan hệ 1 - N (Department ↔ Employee)
# Sai:
# employees = relationship("Employee", back_populates="department_id")
# Nguyên nhân:
# back_populates phải trỏ tới relationship bên kia (department), không phải cột department_id
# Sửa:
# employees = relationship("Employee", back_populates="department")


# Lỗi 2: Quan hệ 1 - 1 (Employee ↔ Device)
# Sai:
# device = relationship("Device", back_populates="employee")
# Nguyên nhân:
# Thiếu uselist=False → bị hiểu thành 1-N
# Sửa:
# device = relationship("Device", back_populates="employee", uselist=False)
# + thêm unique=True cho employee_id


# Lỗi 3: Quan hệ N - N (Employee ↔ Project)
# Sai:
# projects = relationship("Project", back_populates="employees")
# employees = relationship("Employee", back_populates="projects")
# Nguyên nhân:
# Thiếu secondary → SQLAlchemy không biết bảng trung gian
# Sửa:
# thêm secondary=employee_project


# ================== PHẦN 2: CODE ĐÃ SỬA ==================

from sqlalchemy import Column, Integer, String, ForeignKey, Table, create_engine
from sqlalchemy.orm import relationship, sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Bảng trung gian N-N
employee_project = Table(
    "employee_project",
    Base.metadata,
    Column("employee_id", Integer, ForeignKey("employees.id"), primary_key=True),
    Column("project_id", Integer, ForeignKey("projects.id"), primary_key=True)
)

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

    # 1 - N (đã sửa)
    employees = relationship("Employee", back_populates="department")


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

    department_id = Column(Integer, ForeignKey("departments.id"))
    department = relationship("Department", back_populates="employees")

    # 1 - 1 (đã sửa)
    device = relationship("Device", back_populates="employee", uselist=False)

    # N - N (đã sửa)
    projects = relationship("Project", secondary=employee_project, back_populates="employees")


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True)
    serial_number = Column(String(50), unique=True, nullable=False)

    # unique để đảm bảo 1-1
    employee_id = Column(Integer, ForeignKey("employees.id"), unique=True)
    employee = relationship("Employee", back_populates="device")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)

    # N - N (đã sửa)
    employees = relationship("Employee", secondary=employee_project, back_populates="projects")


# ================== CHẠY ==================
if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("Đã tạo database thành công!")