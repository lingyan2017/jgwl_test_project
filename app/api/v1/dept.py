from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.dept import SysDept
from app.models.user import SysUser
from app.schemas.common import success
from app.schemas.dept import DeptCreate, DeptOut, DeptUpdate

router = APIRouter()


def _check_tenant(current_user: SysUser, target_tenant_id: str) -> None:
    if current_user.user_type != 0 and target_tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="无权访问其他租户的数据")


def build_tree(depts: list[SysDept], parent_id: int = 0) -> list[dict]:
    result = []
    for d in depts:
        if d.parent_id == parent_id:
            node = DeptOut.model_validate(d).model_dump()
            node["children"] = build_tree(depts, d.id)
            result.append(node)
    return sorted(result, key=lambda x: x["order_num"])


@router.get("/tree")
async def dept_tree(
    tenant_id: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    q = select(SysDept).where(SysDept.deleted == 0, SysDept.status == 1)
    if current_user.user_type == 0:
        if tenant_id:
            q = q.where(SysDept.tenant_id == tenant_id)
    else:
        q = q.where(SysDept.tenant_id == current_user.tenant_id)
    depts = (await db.execute(q)).scalars().all()
    return success(build_tree(list(depts)))


@router.get("/list")
async def list_depts(
    page: int = 1,
    page_size: int = 10,
    tenant_id: str | None = None,
    dept_name: str | None = None,
    status: int | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    q = select(SysDept).where(SysDept.deleted == 0)
    if current_user.user_type == 0:
        if tenant_id:
            q = q.where(SysDept.tenant_id == tenant_id)
    else:
        q = q.where(SysDept.tenant_id == current_user.tenant_id)
    if dept_name:
        q = q.where(SysDept.dept_name.like(f"%{dept_name}%"))
    if status is not None:
        q = q.where(SysDept.status == status)

    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar()
    items = (await db.execute(q.order_by(SysDept.order_num, SysDept.id).offset((page - 1) * page_size).limit(page_size))).scalars().all()
    return success({"total": total, "items": [DeptOut.model_validate(i) for i in items]})


@router.get("/get/{id}")
async def get_dept(id: int, db: AsyncSession = Depends(get_db), current_user: SysUser = Depends(get_current_user)):
    dept = (await db.execute(select(SysDept).where(SysDept.id == id, SysDept.deleted == 0))).scalar_one_or_none()
    if not dept:
        raise HTTPException(status_code=404, detail="部门不存在")
    _check_tenant(current_user, dept.tenant_id)
    return success(DeptOut.model_validate(dept))


@router.post("/create")
async def create_dept(data: DeptCreate, db: AsyncSession = Depends(get_db), current_user: SysUser = Depends(get_current_user)):
    _check_tenant(current_user, data.tenant_id)
    dept = SysDept(**data.model_dump())
    db.add(dept)
    await db.commit()
    await db.refresh(dept)
    return success(DeptOut.model_validate(dept))


@router.put("/update/{id}")
async def update_dept(id: int, data: DeptUpdate, db: AsyncSession = Depends(get_db), current_user: SysUser = Depends(get_current_user)):
    dept = (await db.execute(select(SysDept).where(SysDept.id == id, SysDept.deleted == 0))).scalar_one_or_none()
    if not dept:
        raise HTTPException(status_code=404, detail="部门不存在")
    _check_tenant(current_user, dept.tenant_id)
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(dept, k, v)
    await db.commit()
    await db.refresh(dept)
    return success(DeptOut.model_validate(dept))


@router.delete("/delete/{id}")
async def delete_dept(id: int, db: AsyncSession = Depends(get_db), current_user: SysUser = Depends(get_current_user)):
    dept = (await db.execute(select(SysDept).where(SysDept.id == id, SysDept.deleted == 0))).scalar_one_or_none()
    if not dept:
        raise HTTPException(status_code=404, detail="部门不存在")
    _check_tenant(current_user, dept.tenant_id)
    dept.deleted = 1
    await db.commit()
    return success(msg="删除成功")
