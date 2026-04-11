"""
资产相关API
"""
import json
import uuid
import os
import qrcode
from io import BytesIO
import base64
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func

from app.core.database import get_db
from app.core.security import get_current_user, require_permission
from app.core.config import settings
from app.models.asset import Asset, AssetRecord, AssetStatus, AssetType
from app.models.user import User
from app.schemas.asset import (
    AssetCreate,
    AssetUpdate,
    AssetResponse,
    AssetAssign,
    AssetTransfer,
    AssetRecordResponse,
    ConsumableRecordCreate,
    ConsumableRecordResponse,
    PageResponse
)

router = APIRouter()


def generate_asset_no(category_id: int = 0) -> str:
    """生成资产编码"""
    timestamp = datetime.now().strftime("%Y%m%d")
    unique_id = str(uuid.uuid4())[:6].upper()
    return f"AS{timestamp}{unique_id}"


def generate_qr_code(asset_no: str, asset_name: str) -> str:
    """生成二维码数据"""
    qr_data = {
        "asset_no": asset_no,
        "name": asset_name,
        "verify_url": f"/api/assets/scan/{asset_no}"
    }
    return json.dumps(qr_data)


@router.get("/", response_model=PageResponse)
async def list_assets(
    keyword: Optional[str] = None,
    category_id: Optional[int] = None,
    department_id: Optional[int] = None,
    user_id: Optional[int] = None,
    status: Optional[str] = None,
    asset_type: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取资产列表"""
    query = db.query(Asset)

    if keyword:
        query = query.filter(
            or_(
                Asset.name.contains(keyword),
                Asset.asset_no.contains(keyword),
                Asset.serial_no.contains(keyword)
            )
        )

    if category_id:
        query = query.filter(Asset.category_id == category_id)

    if department_id:
        query = query.filter(Asset.department_id == department_id)

    if user_id:
        query = query.filter(Asset.user_id == user_id)

    if status:
        query = query.filter(Asset.status == status)

    if asset_type:
        query = query.filter(Asset.asset_type == asset_type)

    total = query.count()
    items = query.order_by(Asset.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    # 将 ORM 对象转换为 Pydantic 模型
    item_responses = [AssetResponse.model_validate(item) for item in items]

    return PageResponse(total=total, page=page, page_size=page_size, items=item_responses)


@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取资产详情"""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


@router.get("/no/{asset_no}", response_model=AssetResponse)
async def get_asset_by_no(
    asset_no: str,
    db: Session = Depends(get_db)
):
    """通过编码获取资产（扫码专用）"""
    asset = db.query(Asset).filter(Asset.asset_no == asset_no).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


@router.post("/", response_model=AssetResponse)
async def create_asset(
    asset_data: AssetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("asset", "create"))
):
    """创建资产"""
    # 生成资产编码
    asset_no = generate_asset_no(asset_data.category_id)

    # 创建资产
    asset = Asset(
        asset_no=asset_no,
        name=asset_data.name,
        category_id=asset_data.category_id,
        asset_type=asset_data.asset_type,
        brand=asset_data.brand,
        model=asset_data.model,
        serial_no=asset_data.serial_no,
        purchase_date=asset_data.purchase_date,
        purchase_price=asset_data.purchase_price,
        warranty_end=asset_data.warranty_end,
        department_id=asset_data.department_id,
        user_id=asset_data.user_id,
        keeper_id=asset_data.keeper_id,
        location=asset_data.location,
        quantity=asset_data.quantity,
        unit=asset_data.unit,
        min_stock=asset_data.min_stock,
        current_stock=asset_data.current_stock,
        description=asset_data.description,
        remarks=asset_data.remarks,
        images=json.dumps(asset_data.images) if asset_data.images else None,
        custom_fields=asset_data.custom_fields,
        created_by=current_user.id,
        qr_code=generate_qr_code(asset_no, asset_data.name)
    )

    db.add(asset)
    db.commit()
    db.refresh(asset)

    # 记录变动
    record = AssetRecord(
        asset_id=asset.id,
        action_type="create",
        after_data=json.dumps(asset_data.model_dump(), default=str),
        description="资产创建",
        operator_id=current_user.id
    )
    db.add(record)
    db.commit()

    return asset


@router.put("/{asset_id}", response_model=AssetResponse)
async def update_asset(
    asset_id: int,
    asset_data: AssetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("asset", "update"))
):
    """更新资产"""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # 记录旧数据
    before_data = json.dumps({
        "name": asset.name,
        "category_id": asset.category_id,
        "brand": asset.brand,
        "model": asset.model,
        "status": asset.status,
        "user_id": asset.user_id,
        "department_id": asset.department_id,
        "location": asset.location
    })

    # 更新字段
    update_data = asset_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key == "images" and value is not None:
            setattr(asset, key, json.dumps(value))
        else:
            setattr(asset, key, value)

    db.commit()
    db.refresh(asset)

    # 记录变动
    record = AssetRecord(
        asset_id=asset.id,
        action_type="update",
        before_data=before_data,
        after_data=json.dumps(update_data, default=str),
        description="资产信息更新",
        operator_id=current_user.id
    )
    db.add(record)
    db.commit()

    return asset


@router.delete("/{asset_id}")
async def delete_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("asset", "delete"))
):
    """删除资产"""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    if asset.status not in [AssetStatus.STOCK, AssetStatus.SCRAPPED]:
        raise HTTPException(status_code=400, detail="Cannot delete asset in current status")

    db.delete(asset)
    db.commit()

    return {"message": "Asset deleted successfully"}


@router.post("/{asset_id}/assign", response_model=AssetResponse)
async def assign_asset(
    asset_id: int,
    assign_data: AssetAssign,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("asset", "update"))
):
    """分配资产"""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # 记录旧数据
    before_data = json.dumps({
        "user_id": asset.user_id,
        "department_id": asset.department_id,
        "keeper_id": asset.keeper_id,
        "location": asset.location,
        "status": asset.status
    })

    # 更新分配信息
    asset.user_id = assign_data.user_id
    asset.department_id = assign_data.department_id or asset.department_id
    asset.keeper_id = assign_data.keeper_id
    asset.location = assign_data.location
    asset.status = AssetStatus.IN_USE

    db.commit()
    db.refresh(asset)

    # 记录变动
    record = AssetRecord(
        asset_id=asset.id,
        action_type="assign",
        before_data=before_data,
        after_data=json.dumps(assign_data.model_dump()),
        description=f"资产分配给用户 {assign_data.user_id}",
        operator_id=current_user.id
    )
    db.add(record)
    db.commit()

    return asset


@router.post("/{asset_id}/transfer", response_model=AssetResponse)
async def transfer_asset(
    asset_id: int,
    transfer_data: AssetTransfer,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("asset", "update"))
):
    """调拨资产"""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # 记录旧数据
    before_data = json.dumps({
        "department_id": asset.department_id,
        "user_id": asset.user_id,
        "keeper_id": asset.keeper_id,
        "location": asset.location
    })

    # 更新调拨信息
    if transfer_data.target_department_id is not None:
        asset.department_id = transfer_data.target_department_id
    if transfer_data.target_user_id is not None:
        asset.user_id = transfer_data.target_user_id
    if transfer_data.target_keeper_id is not None:
        asset.keeper_id = transfer_data.target_keeper_id
    if transfer_data.target_location is not None:
        asset.location = transfer_data.target_location

    db.commit()
    db.refresh(asset)

    # 记录变动
    record = AssetRecord(
        asset_id=asset.id,
        action_type="transfer",
        before_data=before_data,
        after_data=json.dumps(transfer_data.model_dump()),
        description="资产调拨",
        operator_id=current_user.id
    )
    db.add(record)
    db.commit()

    return asset


@router.post("/{asset_id}/return", response_model=AssetResponse)
async def return_asset(
    asset_id: int,
    remarks: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("asset", "update"))
):
    """退库资产"""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # 记录旧数据
    before_data = json.dumps({
        "user_id": asset.user_id,
        "department_id": asset.department_id,
        "status": asset.status
    })

    # 退库
    asset.user_id = None
    asset.department_id = None
    asset.status = AssetStatus.STOCK

    db.commit()
    db.refresh(asset)

    # 记录变动
    record = AssetRecord(
        asset_id=asset.id,
        action_type="return",
        before_data=before_data,
        description=f"资产退库，备注：{remarks}" if remarks else "资产退库",
        operator_id=current_user.id
    )
    db.add(record)
    db.commit()

    return asset


@router.get("/{asset_id}/records", response_model=List[AssetRecordResponse])
async def get_asset_records(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取资产变动记录"""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    records = db.query(AssetRecord).filter(AssetRecord.asset_id == asset_id).order_by(
        AssetRecord.created_at.desc()
    ).all()

    return records


@router.get("/{asset_id}/qrcode")
async def get_asset_qrcode(
    asset_id: int,
    db: Session = Depends(get_db)
):
    """获取资产二维码"""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # 生成二维码图片
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(asset.qr_code)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img = img.resize((300, 300))

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return StreamingResponse(buffer, media_type="image/png")


@router.post("/{asset_id}/photos")
async def upload_asset_photos(
    asset_id: int,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("asset", "update"))
):
    """上传资产照片"""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # 获取现有图片
    existing_images = json.loads(asset.images) if asset.images else []

    # 保存新图片
    for file in files:
        if file.size > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail=f"File {file.filename} is too large")

        # 生成唯一文件名
        ext = os.path.splitext(file.filename)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}{ext}"
        relative_path = f"assets/{asset.asset_no}_{unique_filename}"
        file_path = f"{settings.UPLOAD_DIR}/{relative_path}"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # 存储可访问的 URL 路径
        existing_images.append(f"/uploads/{relative_path}")

    asset.images = json.dumps(existing_images)
    db.commit()

    return {"message": "Photos uploaded successfully", "images": existing_images}


@router.delete("/{asset_id}/photos")
async def delete_asset_photo(
    asset_id: int,
    url: str = Query(..., description="要删除的图片URL"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("asset", "update"))
):
    """删除资产照片"""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    existing_images = json.loads(asset.images) if asset.images else []

    if url not in existing_images:
        raise HTTPException(status_code=404, detail="Image not found")

    # 删除物理文件
    file_path = os.path.join(settings.UPLOAD_DIR, url.lstrip("/uploads/"))
    if os.path.exists(file_path):
        os.remove(file_path)

    # 更新数据库
    existing_images.remove(url)
    asset.images = json.dumps(existing_images) if existing_images else None
    db.commit()

    return {"message": "Photo deleted successfully", "images": existing_images}


@router.post("/{asset_id}/attachments")
async def upload_asset_attachments(
    asset_id: int,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("asset", "update"))
):
    """上传资产附件"""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # 获取现有附件
    existing_attachments = json.loads(asset.attachments) if asset.attachments else []

    # 检查附件数量限制
    if len(existing_attachments) + len(files) > 20:
        raise HTTPException(status_code=400, detail="Maximum 20 attachments allowed")

    # 支持的文件类型
    ALLOWED_TYPES = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".jpg", ".jpeg", ".png"}
    MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB

    # 保存新附件
    for file in files:
        # 检查文件类型
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ALLOWED_TYPES:
            raise HTTPException(status_code=400, detail=f"File type {ext} not allowed")

        # 检查文件大小
        if file.size > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail=f"File {file.filename} is too large (max 20MB)")

        # 生成唯一文件名
        unique_filename = f"{uuid.uuid4().hex}{ext}"
        file_dir = f"{settings.UPLOAD_DIR}/attachments/{asset.asset_no}"
        os.makedirs(file_dir, exist_ok=True)
        file_path = os.path.join(file_dir, unique_filename)

        # 保存文件
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # 添加附件信息
        from datetime import datetime
        attachment_info = {
            "name": file.filename,
            "url": f"/api/assets/attachments/{asset_id}/{unique_filename}",
            "type": ext[1:],  # 去掉点
            "size": len(content),
            "uploaded_at": datetime.utcnow().isoformat()
        }
        existing_attachments.append(attachment_info)

    asset.attachments = json.dumps(existing_attachments)
    db.commit()

    return {"message": "Attachments uploaded successfully", "attachments": existing_attachments}


@router.get("/{asset_id}/attachments")
async def list_asset_attachments(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取资产附件列表"""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    attachments = json.loads(asset.attachments) if asset.attachments else []
    return attachments


@router.delete("/{asset_id}/attachments/{filename}")
async def delete_asset_attachment(
    asset_id: int,
    filename: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("asset", "update"))
):
    """删除资产附件"""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    attachments = json.loads(asset.attachments) if asset.attachments else []

    # 找到要删除的附件
    attachment_to_delete = None
    for att in attachments:
        if filename in att.get("url", ""):
            attachment_to_delete = att
            break

    if not attachment_to_delete:
        raise HTTPException(status_code=404, detail="Attachment not found")

    # 删除物理文件
    file_path = os.path.join(settings.UPLOAD_DIR, "attachments", asset.asset_no, filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    # 从列表中移除
    attachments = [att for att in attachments if filename not in att.get("url", "")]
    asset.attachments = json.dumps(attachments) if attachments else None
    db.commit()

    return {"message": "Attachment deleted successfully"}


@router.get("/attachments/{asset_id}/{filename}")
async def download_attachment(
    asset_id: int,
    filename: str,
    db: Session = Depends(get_db)
):
    """下载资产附件"""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    file_path = os.path.join(settings.UPLOAD_DIR, "attachments", asset.asset_no, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    # 获取原始文件名
    attachments = json.loads(asset.attachments) if asset.attachments else []
    original_name = filename
    for att in attachments:
        if filename in att.get("url", ""):
            original_name = att.get("name", filename)
            break

    from fastapi.responses import FileResponse
    return FileResponse(file_path, filename=original_name)


@router.get("/stats/overview")
async def get_asset_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取资产统计概览"""
    total = db.query(Asset).count()
    in_use = db.query(Asset).filter(Asset.status == "in_use").count()
    in_stock = db.query(Asset).filter(Asset.status == "stock").count()
    in_repair = db.query(Asset).filter(Asset.status == "repair").count()
    scrapped = db.query(Asset).filter(Asset.status == "scrapped").count()

    # 按类型统计
    fixed = db.query(Asset).filter(Asset.asset_type == "fixed").count()
    consumable = db.query(Asset).filter(Asset.asset_type == "consumable").count()
    real_estate = db.query(Asset).filter(Asset.asset_type == "real_estate").count()

    # 总价值
    total_value = db.query(Asset).with_entities(
        func.sum(Asset.purchase_price)
    ).scalar() or 0

    return {
        "total": total,
        "in_use": in_use,
        "in_stock": in_stock,
        "in_repair": in_repair,
        "scrapped": scrapped,
        "fixed": fixed,
        "consumable": consumable,
        "real_estate": real_estate,
        "total_value": total_value
    }


@router.post("/import")
async def import_assets(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("asset", "create"))
):
    """
    批量导入资产

    接受 Excel 文件（.xlsx/.xls），解析后批量创建资产。

    返回:
    - total: 总行数
    - success: 成功导入数
    - failed: 失败数
    - errors: 错误详情列表 [{row, field, message, value}]
    - imported_assets: 成功导入的资产简报 [{id, asset_no, name}]
    """
    # 验证文件类型
    if not file.filename:
        raise HTTPException(status_code=400, detail="未提供文件名")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in (".xlsx", ".xls"):
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式: {ext}，请上传 .xlsx 或 .xls 文件",
        )

    # 读取文件内容
    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="上传文件为空")

    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="文件大小不能超过 10MB")

    # 解析 Excel
    from app.utils.excel_import import (
        parse_excel_file,
        validate_asset_row,
        AssetImportResult,
    )

    rows, parse_error = parse_excel_file(content)
    if parse_error:
        raise HTTPException(status_code=400, detail=parse_error)

    if not rows:
        raise HTTPException(status_code=400, detail="Excel 文件中没有数据行")

    # 验证并导入
    result = AssetImportResult(total=len(rows), success=0, failed=0)
    imported_asset_ids: List[int] = []

    for idx, row_data in enumerate(rows, start=1):
        validated, errors = validate_asset_row(row_data, idx, db)

        if errors:
            result.failed += 1
            result.errors.extend(errors)
            continue

        # 创建资产
        try:
            asset_no = generate_asset_no(validated["category_id"])
            asset = Asset(
                asset_no=asset_no,
                name=validated["name"],
                category_id=validated["category_id"],
                asset_type=validated["asset_type"],
                brand=validated.get("brand"),
                model=validated.get("model"),
                serial_no=validated.get("serial_no"),
                purchase_date=validated.get("purchase_date"),
                purchase_price=validated.get("purchase_price", 0.0),
                warranty_end=validated.get("warranty_end"),
                department_id=validated.get("department_id"),
                location=validated.get("location"),
                quantity=validated.get("quantity", 1),
                unit=validated.get("unit"),
                description=validated.get("description"),
                remarks=validated.get("remarks"),
                created_by=current_user.id,
                qr_code=generate_qr_code(asset_no, validated["name"]),
            )
            db.add(asset)
            db.flush()  # 获取资产 ID

            # 记录变动
            record = AssetRecord(
                asset_id=asset.id,
                action_type="create",
                after_data="批量导入创建",
                description=f"批量导入（文件名: {file.filename}）",
                operator_id=current_user.id,
            )
            db.add(record)

            result.success += 1
            result.imported_assets.append({
                "id": asset.id,
                "asset_no": asset.asset_no,
                "name": asset.name,
            })
            imported_asset_ids.append(asset.id)

        except Exception as e:
            result.failed += 1
            from app.utils.excel_import import ImportError as ImportErrorClass
            result.errors.append(ImportErrorClass(
                row=idx,
                field="system",
                message=f"创建资产失败: {str(e)}",
            ))

    # 统一提交
    db.commit()

    return result.to_dict()


@router.get("/import/template")
async def download_import_template(
    current_user: User = Depends(require_permission("asset", "create"))
):
    """
    下载资产导入模板 Excel 文件
    """
    from fastapi.responses import StreamingResponse
    from app.utils.excel_import import generate_import_template
    from io import BytesIO

    template_bytes = generate_import_template()
    buffer = BytesIO(template_bytes)
    buffer.seek(0)

    from urllib.parse import quote
    encoded_filename = quote("资产导入模板.xlsx")
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
        },
    )
