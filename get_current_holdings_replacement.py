    @classmethod
    def get_current_holdings(cls, force_refresh_prices: bool = False) -> List[Dict[str, Any]]:
        """获取当前持仓列表（修复版：按持仓周期计算成本价）"""
        try:
            # 获取所有有交易记录的股票代码
            stock_codes = db.session.query(TradeRecord.stock_code).filter(
                TradeRecord.is_corrected == False
            ).distinct().all()
            
            holdings = []
            
            for (stock_code,) in stock_codes:
                period = cls._get_current_holding_period(stock_code)
                
                if period and period['current_quantity'] > 0:
                    # 获取最新复盘记录
                    latest_review = cls.get_latest_review_by_stock(stock_code)
                    
                    # 获取当前持仓的实际开始日期
                    current_holding_start_date = period['start_date']
                    
                    # 计算实际持仓交易日数
                    actual_holding_days = cls._calculate_actual_holding_days(
                        current_holding_start_date,
                        latest_review.holding_days if latest_review else None
                    )
                    
                    # 保持原有的持仓天数计算（兼容性）
                    holding_days = cls._calculate_holding_days(
                        current_holding_start_date,
                        latest_review.holding_days if latest_review else None
                    )
                    
                    # 获取当前价格
                    current_price = cls._get_current_price(stock_code, force_refresh_prices)
                    
                    holding = {
                        'stock_code': period['stock_code'],
                        'stock_name': period['stock_name'],
                        'current_quantity': period['current_quantity'],
                        'total_buy_quantity': period['total_buy_quantity'],
                        'total_sell_quantity': period['total_sell_quantity'],
                        'avg_buy_price': float(period['avg_buy_price']),
                        'avg_price': float(period['avg_buy_price']),  # 兼容字段
                        'current_price': current_price,
                        'first_buy_date': current_holding_start_date.isoformat(),
                        'last_buy_date': period['buy_trades'][-1].trade_date.isoformat() if period['buy_trades'] else current_holding_start_date.isoformat(),
                        'holding_days': holding_days,
                        'actual_holding_days': actual_holding_days,
                        'latest_review': latest_review.to_dict() if latest_review else None
                    }
                    holdings.append(holding)
            
            return holdings
            
        except Exception as e:
            raise DatabaseError(f"获取当前持仓失败: {str(e)}")