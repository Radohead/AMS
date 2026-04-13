#!/usr/bin/env python3
"""
更新所有资产的二维码URL
用于IP变更后同步二维码

用法:
    python scripts/update_qr_codes.py
"""
import sys
import os

# 添加 backend 目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.asset import Asset
from app.core.database import SessionLocal
from app.core.config import settings


def update_qr_codes():
    """更新所有资产的二维码"""
    db = SessionLocal()
    try:
        assets = db.query(Asset).all()
        frontend_url = settings.FRONTEND_URL.rstrip('/')

        for asset in assets:
            new_qr_code = f'{frontend_url}/mobile/assets/{asset.id}'
            asset.qr_code = new_qr_code
            print(f'资产 {asset.id}: {asset.name}')
            print(f'  旧: {asset.qr_code}')
            print(f'  新: {new_qr_code}')

        db.commit()
        print(f'\n✅ 共更新 {len(assets)} 个资产的二维码')
        print(f'FRONTEND_URL: {settings.FRONTEND_URL}')
    finally:
        db.close()


if __name__ == '__main__':
    print('=' * 50)
    print('资产二维码更新脚本')
    print('=' * 50)
    update_qr_codes()
