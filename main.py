# PHẦN 1: BÁO CÁO LỖI
# Lỗi 1: Tạo hồ sơ cho người dùng không tồn tại
# Dữ liệu test
# POST /users/99/profile

# {
#     "full_name": "Lê Văn A",
#     "phone": "0909999999",
#     "address": "TP.HCM"
# }
# Kết quả thực tế: Tạo hồ sơ thành công.
# Kết quả mong đợi: Báo lỗi "Người dùng không tồn tại".
# Nguyên nhân: Chưa kiểm tra user_id có tồn tại trong danh sách users.
# Code sửa:
# user = next(
#     (user for user in users if user["id"] == user_id),
#     None
# )

# if user is None:
#     raise HTTPException(
#         status_code=404,
#         detail="Người dùng không tồn tại"
#     )
# Lỗi 2: Một người dùng có thể tạo nhiều hồ sơ
# Dữ liệu test
# POST /users/1/profile

# {
#     "full_name": "Nguyễn Văn An",
#     "phone": "0908888888",
#     "address": "Hà Nội"
# }
# Kết quả thực tế: Vẫn tạo được hồ sơ mới.
# Kết quả mong đợi: Báo lỗi "Người dùng đã có hồ sơ".
# Nguyên nhân: Kiểm tra profile["id"] == user_id thay vì profile["user_id"] == user_id.
# Code sửa:
# existing_profile = next(
#     (
#         profile
#         for profile in profiles
#         if profile["user_id"] == user_id
#     ),
#     None
# )
# Lỗi 3: Trùng số điện thoại
# Dữ liệu test
# POST /users/2/profile

# {
#     "full_name": "Trần Thị Bình",
#     "phone": "0901000001",
#     "address": "Đà Nẵng"
# }
# Kết quả thực tế: Vẫn tạo được hồ sơ.
# Kết quả mong đợi: Báo lỗi "Số điện thoại đã được sử dụng".
# Nguyên nhân: Chỉ kiểm tra số điện thoại trong cùng một user_id, trong khi yêu cầu là không được trùng trong toàn hệ thống.
# Code sửa:
# duplicated_phone = next(
#     (
#         profile
#         for profile in profiles
#         if profile["phone"] == profile_data.phone
#     ),
#     None
# )

# PHẦN 2: SOURCE CODE ĐÃ SỬA
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()


class UserProfileCreate(BaseModel):
    full_name: str
    phone: str
    address: str | None = None


users = [
    {
        "id": 1,
        "username": "nguyenvanan",
        "email": "an@gmail.com"
    },
    {
        "id": 2,
        "username": "tranthibinh",
        "email": "binh@gmail.com"
    }
]


profiles = [
    {
        "id": 10,
        "full_name": "Nguyễn Văn An",
        "phone": "0901000001",
        "address": "Hà Nội",
        "user_id": 1
    }
]


@app.get("/users")
def get_users():
    return users


@app.get("/profiles")
def get_profiles():
    return profiles


@app.post(
    "/users/{user_id}/profile",
    status_code=status.HTTP_201_CREATED
)
def create_profile(
    user_id: int,
    profile_data: UserProfileCreate
):

    user = next(
        (user for user in users if user["id"] == user_id),
        None
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="Người dùng không tồn tại"
        )

    existing_profile = next(
        (
            profile
            for profile in profiles
            if profile["user_id"] == user_id
        ),
        None
    )

    if existing_profile:
        raise HTTPException(
            status_code=409,
            detail="Người dùng đã có hồ sơ"
        )

    duplicated_phone = next(
        (
            profile
            for profile in profiles
            if profile["phone"] == profile_data.phone
        ),
        None
    )

    if duplicated_phone:
        raise HTTPException(
            status_code=409,
            detail="Số điện thoại đã được sử dụng"
        )

    new_profile = {
        "id": len(profiles) + 1,
        "full_name": profile_data.full_name,
        "phone": profile_data.phone,
        "address": profile_data.address,
        "user_id": user_id
    }

    profiles.append(new_profile)

    return new_profile