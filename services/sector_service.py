"""
板块分析服务
"""
import akshare as ak
import pandas as pd
from datetime import date, datetime, timedelta
from typing import List, Dict, Optional, Any
from sqlalchemy import desc, func, and_
from extensions import db
from models.sector_data import SectorData, SectorRanking
from services.base_service import BaseService
from error_handlers import ValidationError, ExternalAPIError


class SectorAnalysisService(BaseService):
    """板块分析服务"""
    
    model = SectorData
    
    @classmethod
    def refresh_sector_data(cls) -> Dict[str, Any]:
        """刷新板块数据，避免重复记录"""
        try:
            today = date.today()
            
            # 检查今日是否已有数据
            if SectorData.has_data_for_date(today):
                return {
                    "success": True,
                    "message": "今日数据已存在，无需重复获取",
                    "date": today.isoformat(),
                    "count": 0
                }
            
            # 获取AKShare板块数据
            try:
                sector_df = ak.stock_board_industry_name_em()
            except Exception as e:
                raise ExternalAPIError(f"获取板块数据失败: {str(e)}")
            
            if sector_df.empty:
                return {
                    "success": False,
                    "message": "未获取到板块数据",
                    "date": today.isoformat(),
                    "count": 0
                }
            
            # 批量插入数据
            sector_records = []
            ranking_data = []
            
            for idx, row in sector_df.iterrows():
                try:
                    # 创建板块数据记录
                    sector_data = SectorData(
                        sector_name=row.get('板块名称', ''),
                        sector_code=row.get('板块代码', ''),
                        change_percent=float(row.get('涨跌幅', 0)),
                        record_date=today,
                        rank_position=idx + 1,
                        volume=int(row.get('成交量', 0)) if pd.notna(row.get('成交量', 0)) else None,
                        market_cap=float(row.get('总市值', 0)) if pd.notna(row.get('总市值', 0)) else None
                    )
                    sector_records.append(sector_data)
                    
                    # 准备排名数据
                    ranking_data.append({
                        'rank': idx + 1,
                        'sector_name': row.get('板块名称', ''),
                        'change_percent': float(row.get('涨跌幅', 0)),
                        'volume': int(row.get('成交量', 0)) if pd.notna(row.get('成交量', 0)) else None,
                        'market_cap': float(row.get('总市值', 0)) if pd.notna(row.get('总市值', 0)) else None
                    })
                    
                except (ValueError, TypeError) as e:
                    # 跳过有问题的数据行
                    continue
            
            # 批量保存板块数据
            if sector_records:
                db.session.add_all(sector_records)
                db.session.commit()
                
                # 保存排名数据
                SectorRanking.create_or_update(today, ranking_data, len(sector_records))
                
                return {
                    "success": True,
                    "message": f"成功获取并保存{len(sector_records)}条板块数据",
                    "date": today.isoformat(),
                    "count": len(sector_records)
                }
            else:
                return {
                    "success": False,
                    "message": "没有有效的板块数据可保存",
                    "date": today.isoformat(),
                    "count": 0
                }
                
        except Exception as e:
            db.session.rollback()
            if isinstance(e, (ValidationError, ExternalAPIError)):
                raise e
            raise ExternalAPIError(f"刷新板块数据时发生错误: {str(e)}")
    
    @classmethod
    def get_sector_ranking(cls, target_date: Optional[date] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """获取板块涨幅排名"""
        try:
            if target_date is None:
                target_date = date.today()
            
            # 首先尝试从排名表获取
            ranking_record = SectorRanking.get_by_date(target_date)
            if ranking_record:
                ranking_list = ranking_record.ranking_list
                if limit:
                    ranking_list = ranking_list[:limit]
                return ranking_list
            
            # 如果排名表没有数据，从板块数据表获取
            query = SectorData.query.filter_by(record_date=target_date).order_by(SectorData.rank_position)
            if limit:
                query = query.limit(limit)
            
            sectors = query.all()
            return [sector.to_dict() for sector in sectors]
            
        except Exception as e:
            raise ValidationError(f"获取板块排名失败: {str(e)}")
    
    @classmethod
    def get_sector_history(cls, sector_name: str, days: int = 30) -> List[Dict[str, Any]]:
        """获取板块历史表现"""
        try:
            if not sector_name:
                raise ValidationError("板块名称不能为空", "sector_name")
            
            if days <= 0:
                raise ValidationError("查询天数必须大于0", "days")
            
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            sectors = SectorData.query.filter(
                SectorData.sector_name == sector_name,
                SectorData.record_date.between(start_date, end_date)
            ).order_by(SectorData.record_date.desc()).all()
            
            return [sector.to_dict() for sector in sectors]
            
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"获取板块历史失败: {str(e)}")
    
    @classmethod
    def get_top_performers(cls, days: int = 30, top_k: int = 10) -> List[Dict[str, Any]]:
        """获取最近N天TOPK板块统计"""
        try:
            if days <= 0:
                raise ValidationError("查询天数必须大于0", "days")
            
            if top_k <= 0:
                raise ValidationError("TOPK值必须大于0", "top_k")
            
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            # 查询指定时间范围内排名前K的板块
            result = db.session.query(
                SectorData.sector_name,
                func.count().label('appearances'),
                func.avg(SectorData.rank_position).label('avg_rank'),
                func.min(SectorData.rank_position).label('best_rank'),
                func.max(SectorData.record_date).label('latest_date'),
                func.avg(SectorData.change_percent).label('avg_change_percent')
            ).filter(
                SectorData.record_date.between(start_date, end_date),
                SectorData.rank_position <= top_k
            ).group_by(SectorData.sector_name).order_by(
                desc('appearances'), 'avg_rank'
            ).all()
            
            # 转换结果为字典列表
            top_performers = []
            for row in result:
                # 计算趋势
                trend = cls._calculate_trend(row.sector_name, days)
                
                top_performers.append({
                    'sector_name': row.sector_name,
                    'appearances': row.appearances,
                    'avg_rank': round(float(row.avg_rank), 2),
                    'best_rank': row.best_rank,
                    'latest_date': row.latest_date.isoformat(),
                    'avg_change_percent': round(float(row.avg_change_percent), 2),
                    'trend': trend,
                    'frequency_rate': round(row.appearances / days * 100, 2)  # 进入榜单频率
                })
            
            return top_performers
            
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"获取TOPK板块统计失败: {str(e)}")
    
    @classmethod
    def _calculate_trend(cls, sector_name: str, days: int) -> str:
        """计算板块趋势"""
        try:
            # 获取最近的排名数据
            recent_data = cls.get_sector_history(sector_name, min(days, 7))
            
            if len(recent_data) < 2:
                return 'stable'
            
            # 计算最近几天的平均排名变化
            recent_ranks = [data.get('rank_position', 999) for data in recent_data if data.get('rank_position')]
            
            if len(recent_ranks) < 2:
                return 'stable'
            
            # 简单的趋势判断：比较前半段和后半段的平均排名
            # recent_data是按日期倒序排列的，所以索引0是最新的数据
            mid = len(recent_ranks) // 2
            recent_avg = sum(recent_ranks[:mid]) / mid if mid > 0 else recent_ranks[0]  # 较新的数据
            early_avg = sum(recent_ranks[mid:]) / len(recent_ranks[mid:]) if len(recent_ranks[mid:]) > 0 else recent_ranks[-1]  # 较早的数据
            
            if recent_avg < early_avg - 2:  # 排名上升（数字变小）
                return 'up'
            elif recent_avg > early_avg + 2:  # 排名下降（数字变大）
                return 'down'
            else:
                return 'stable'
                
        except Exception:
            return 'stable'
    
    @classmethod
    def get_sector_analysis_summary(cls, days: int = 30) -> Dict[str, Any]:
        """获取板块分析汇总信息"""
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            # 统计基本信息
            total_records = SectorData.query.filter(
                SectorData.record_date.between(start_date, end_date)
            ).count()
            
            unique_sectors = db.session.query(
                func.count(func.distinct(SectorData.sector_name))
            ).filter(
                SectorData.record_date.between(start_date, end_date)
            ).scalar()
            
            unique_dates = db.session.query(
                func.count(func.distinct(SectorData.record_date))
            ).filter(
                SectorData.record_date.between(start_date, end_date)
            ).scalar()
            
            # 获取最新数据日期
            latest_date = db.session.query(
                func.max(SectorData.record_date)
            ).scalar()
            
            # 获取涨幅统计
            change_stats = db.session.query(
                func.avg(SectorData.change_percent).label('avg_change'),
                func.max(SectorData.change_percent).label('max_change'),
                func.min(SectorData.change_percent).label('min_change')
            ).filter(
                SectorData.record_date.between(start_date, end_date)
            ).first()
            
            return {
                'period_days': days,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'latest_data_date': latest_date.isoformat() if latest_date else None,
                'total_records': total_records,
                'unique_sectors': unique_sectors,
                'data_days': unique_dates,
                'avg_change_percent': round(float(change_stats.avg_change), 2) if change_stats.avg_change else 0,
                'max_change_percent': round(float(change_stats.max_change), 2) if change_stats.max_change else 0,
                'min_change_percent': round(float(change_stats.min_change), 2) if change_stats.min_change else 0,
                'data_completeness': round(unique_dates / days * 100, 2) if days > 0 else 0
            }
            
        except Exception as e:
            raise ValidationError(f"获取板块分析汇总失败: {str(e)}")
    
    @classmethod
    def get_available_dates(cls, limit: int = 30) -> List[str]:
        """获取可用的数据日期列表"""
        try:
            dates = db.session.query(
                func.distinct(SectorData.record_date)
            ).order_by(desc(SectorData.record_date)).limit(limit).all()
            
            return [date_tuple[0].isoformat() if hasattr(date_tuple[0], 'isoformat') else str(date_tuple[0]) for date_tuple in dates]
            
        except Exception as e:
            raise ValidationError(f"获取可用日期失败: {str(e)}")
    
    @classmethod
    def delete_sector_data(cls, target_date: date) -> Dict[str, Any]:
        """删除指定日期的板块数据"""
        try:
            # 删除板块数据
            deleted_count = SectorData.query.filter_by(record_date=target_date).delete()
            
            # 删除排名数据
            ranking_deleted = SectorRanking.query.filter_by(record_date=target_date).delete()
            
            db.session.commit()
            
            return {
                "success": True,
                "message": f"成功删除{target_date}的板块数据",
                "deleted_sectors": deleted_count,
                "deleted_rankings": ranking_deleted
            }
            
        except Exception as e:
            db.session.rollback()
            raise ValidationError(f"删除板块数据失败: {str(e)}")