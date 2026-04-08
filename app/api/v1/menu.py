from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, require_super_admin
from app.db.session import get_db
from app.models.menu import SysMenu
from app.schemas.common import success
from app.schemas.menu import MenuCreate, MenuOut, MenuUpdate

router = APIRouter()


def build_menu_tree(menus: list, parent_id: int = 0) -> list:
    result = []
    for m in menus:
        if m["parent_id"] == parent_id:
            m["children"] = build_menu_tree(menus, m["id"])
            result.append(m)
    return sorted(result, key=lambda x: x["order_num"])


@router.get("/tree")
async def menu_tree(db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    menus = (await db.execute(select(SysMenu).where(SysMenu.deleted == 0, SysMenu.status == 1))).scalars().all()
    data = [MenuOut.model_validate(m).model_dump() for m in menus]
    return success(build_menu_tree(data))


@router.get("/list")
async def list_menus(
    page: int = 1,
    page_size: int = 10,
    menu_name: str | None = None,
    status: int | None = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    q = select(SysMenu).where(SysMenu.deleted == 0)
    if menu_name:
        q = q.where(SysMenu.menu_name.like(f"%{menu_name}%"))
    if status is not None:
        q = q.where(SysMenu.status == status)

    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar()
    items = (await db.execute(q.order_by(SysMenu.order_num, SysMenu.id).offset((page - 1) * page_size).limit(page_size))).scalars().all()
    return success({"total": total, "items": [MenuOut.model_validate(i) for i in items]})


@router.get("/get/{id}")
async def get_menu(id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    menu = (await db.execute(select(SysMenu).where(SysMenu.id == id, SysMenu.deleted == 0))).scalar_one_or_none()
    if not menu:
        raise HTTPException(status_code=404, detail="菜单不存在")
    return success(MenuOut.model_validate(menu))


@router.post("/create")
async def create_menu(data: MenuCreate, db: AsyncSession = Depends(get_db), _=Depends(require_super_admin)):
    menu = SysMenu(**data.model_dump())
    db.add(menu)
    await db.commit()
    await db.refresh(menu)
    return success(MenuOut.model_validate(menu))


@router.put("/update/{id}")
async def update_menu(id: int, data: MenuUpdate, db: AsyncSession = Depends(get_db), _=Depends(require_super_admin)):
    menu = (await db.execute(select(SysMenu).where(SysMenu.id == id, SysMenu.deleted == 0))).scalar_one_or_none()
    if not menu:
        raise HTTPException(status_code=404, detail="菜单不存在")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(menu, k, v)
    await db.commit()
    await db.refresh(menu)
    return success(MenuOut.model_validate(menu))


@router.delete("/delete/{id}")
async def delete_menu(id: int, db: AsyncSession = Depends(get_db), _=Depends(require_super_admin)):
    menu = (await db.execute(select(SysMenu).where(SysMenu.id == id, SysMenu.deleted == 0))).scalar_one_or_none()
    if not menu:
        raise HTTPException(status_code=404, detail="菜单不存在")
    menu.deleted = 1
    await db.commit()
    return success(msg="删除成功")
