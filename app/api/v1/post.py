from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.post import SysPost
from app.models.user import SysUser
from app.schemas.common import success
from app.schemas.post import PostCreate, PostOut, PostUpdate

router = APIRouter()


def _check_tenant(current_user: SysUser, target_tenant_id: str) -> None:
    if current_user.user_type != 0 and target_tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="无权访问其他租户的数据")


@router.get("/list")
async def list_posts(
    page: int = 1,
    page_size: int = 10,
    tenant_id: str | None = None,
    post_name: str | None = None,
    status: int | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    q = select(SysPost).where(SysPost.deleted == 0)
    if current_user.user_type == 0:
        if tenant_id:
            q = q.where(SysPost.tenant_id == tenant_id)
    else:
        q = q.where(SysPost.tenant_id == current_user.tenant_id)
    if post_name:
        q = q.where(SysPost.post_name.like(f"%{post_name}%"))
    if status is not None:
        q = q.where(SysPost.status == status)

    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar()
    items = (await db.execute(q.order_by(SysPost.post_sort, SysPost.id).offset((page - 1) * page_size).limit(page_size))).scalars().all()
    return success({"total": total, "items": [PostOut.model_validate(i) for i in items]})


@router.get("/get/{id}")
async def get_post(id: int, db: AsyncSession = Depends(get_db), current_user: SysUser = Depends(get_current_user)):
    post = (await db.execute(select(SysPost).where(SysPost.id == id, SysPost.deleted == 0))).scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="岗位不存在")
    _check_tenant(current_user, post.tenant_id)
    return success(PostOut.model_validate(post))


@router.post("/create")
async def create_post(data: PostCreate, db: AsyncSession = Depends(get_db), current_user: SysUser = Depends(get_current_user)):
    _check_tenant(current_user, data.tenant_id)
    post = SysPost(**data.model_dump())
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return success(PostOut.model_validate(post))


@router.put("/update/{id}")
async def update_post(id: int, data: PostUpdate, db: AsyncSession = Depends(get_db), current_user: SysUser = Depends(get_current_user)):
    post = (await db.execute(select(SysPost).where(SysPost.id == id, SysPost.deleted == 0))).scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="岗位不存在")
    _check_tenant(current_user, post.tenant_id)
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(post, k, v)
    await db.commit()
    await db.refresh(post)
    return success(PostOut.model_validate(post))


@router.delete("/delete/{id}")
async def delete_post(id: int, db: AsyncSession = Depends(get_db), current_user: SysUser = Depends(get_current_user)):
    post = (await db.execute(select(SysPost).where(SysPost.id == id, SysPost.deleted == 0))).scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="岗位不存在")
    _check_tenant(current_user, post.tenant_id)
    post.deleted = 1
    await db.commit()
    return success(msg="删除成功")
