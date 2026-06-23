from flask import Flask, jsonify, request, render_template_string
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

DATABASE = 'yy_data.db'

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """初始化数据库和表结构"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ads_channel_daily_pay_df (
            dt TEXT,
            shop_id TEXT,
            shop_name TEXT,
            platformname TEXT,
            distributorname TEXT,
            fashion_code TEXT,
            main_picture TEXT,
            supplier_name TEXT,
            level1 TEXT,
            level2 TEXT,
            level3 TEXT,
            level4 TEXT,
            level5 TEXT,
            series_value TEXT,
            gmv_amt REAL,
            gmv_cnt INTEGER,
            send_amt REAL,
            send_cnt INTEGER,
            actual_amt REAL,
            actual_cnt INTEGER,
            only_refund_amt REAL,
            only_refund_cnt INTEGER,
            return_amt REAL,
            return_cnt INTEGER,
            service_fee_amount REAL,
            updated_at TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print("数据库初始化完成")

# HTML 模板
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>广告渠道日支付数据</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1400px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; }
        .filters { margin: 20px 0; padding: 15px; background: #f9f9f9; border-radius: 5px; }
        .filters label { margin-right: 15px; }
        .filters input, .filters select { padding: 5px 10px; margin-left: 5px; border: 1px solid #ddd; border-radius: 3px; }
        button { background: #007bff; color: white; border: none; padding: 8px 15px; border-radius: 3px; cursor: pointer; margin-left: 10px; }
        button:hover { background: #0056b3; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 12px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #007bff; color: white; position: sticky; top: 0; }
        tr:nth-child(even) { background-color: #f9f9f9; }
        tr:hover { background-color: #f1f1f1; }
        .pagination { margin: 20px 0; text-align: center; }
        .pagination a { margin: 0 5px; padding: 5px 10px; border: 1px solid #ddd; text-decoration: none; color: #007bff; }
        .pagination a.active { background: #007bff; color: white; }
        .stats { margin: 15px 0; padding: 10px; background: #e7f3ff; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>广告渠道日支付数据看板</h1>
        
        <div class="filters">
            <form method="GET" action="/">
                <label>日期：<input type="date" name="dt" value="{{ filters.dt }}"></label>
                <label>店铺 ID：<input type="text" name="shop_id" value="{{ filters.shop_id }}" placeholder="店铺 ID"></label>
                <label>店铺名称：<input type="text" name="shop_name" value="{{ filters.shop_name }}" placeholder="店铺名称"></label>
                <label>平台：<input type="text" name="platformname" value="{{ filters.platformname }}" placeholder="平台"></label>
                <button type="submit">查询</button>
                <button type="button" onclick="location.href='/'">重置</button>
            </form>
        </div>
        
        {% if stats %}
        <div class="stats">
            <strong>统计信息:</strong> 
            总记录数：{{ stats.total_count }} | 
            GMV 总额：{{ stats.total_gmv_amt }} | 
            实际支付总额：{{ stats.total_actual_amt }} | 
            退款总额：{{ stats.total_only_refund_amt }}
        </div>
        {% endif %}
        
        <table>
            <thead>
                <tr>
                    <th>日期</th>
                    <th>店铺 ID</th>
                    <th>店铺名称</th>
                    <th>平台</th>
                    <th>经销商</th>
                    <th>款号</th>
                    <th>供应商</th>
                    <th>一级分类</th>
                    <th>二级分类</th>
                    <th>三级分类</th>
                    <th>GMV 金额</th>
                    <th>GMV 数量</th>
                    <th>发货金额</th>
                    <th>实际支付金额</th>
                    <th>仅退款金额</th>
                    <th>退货金额</th>
                    <th>服务费</th>
                    <th>更新时间</th>
                </tr>
            </thead>
            <tbody>
                {% for row in data %}
                <tr>
                    <td>{{ row.dt }}</td>
                    <td>{{ row.shop_id }}</td>
                    <td>{{ row.shop_name }}</td>
                    <td>{{ row.platformname }}</td>
                    <td>{{ row.distributorname }}</td>
                    <td>{{ row.fashion_code }}</td>
                    <td>{{ row.supplier_name }}</td>
                    <td>{{ row.level1 }}</td>
                    <td>{{ row.level2 }}</td>
                    <td>{{ row.level3 }}</td>
                    <td>{{ "%.2f"|format(row.gmv_amt or 0) }}</td>
                    <td>{{ row.gmv_cnt or 0 }}</td>
                    <td>{{ "%.2f"|format(row.send_amt or 0) }}</td>
                    <td>{{ "%.2f"|format(row.actual_amt or 0) }}</td>
                    <td>{{ "%.2f"|format(row.only_refund_amt or 0) }}</td>
                    <td>{{ "%.2f"|format(row.return_amt or 0) }}</td>
                    <td>{{ "%.2f"|format(row.service_fee_amount or 0) }}</td>
                    <td>{{ row.updated_at }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        
        {% if pagination %}
        <div class="pagination">
            {% if pagination.has_prev %}
            <a href="?page={{ pagination.prev_page }}{% for k, v in filters.items() %}{% if v %}&{{ k }}={{ v }}{% endif %}{% endfor %}">上一页</a>
            {% endif %}
            
            <span style="margin: 0 10px;">第 {{ pagination.page }} / {{ pagination.pages }} 页</span>
            
            {% if pagination.has_next %}
            <a href="?page={{ pagination.next_page }}{% for k, v in filters.items() %}{% if v %}&{{ k }}={{ v }}{% endif %}{% endfor %}">下一页</a>
            {% endif %}
        </div>
        {% endif %}
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    """首页 - 数据展示和查询"""
    dt = request.args.get('dt', '')
    shop_id = request.args.get('shop_id', '')
    shop_name = request.args.get('shop_name', '')
    platformname = request.args.get('platformname', '')
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    conditions = []
    params = []
    
    if dt:
        conditions.append("dt = ?")
        params.append(dt)
    if shop_id:
        conditions.append("shop_id LIKE ?")
        params.append(f"%{shop_id}%")
    if shop_name:
        conditions.append("shop_name LIKE ?")
        params.append(f"%{shop_name}%")
    if platformname:
        conditions.append("platformname LIKE ?")
        params.append(f"%{platformname}%")
    
    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)
    
    conn = get_db_connection()
    
    stats_query = f"""
        SELECT 
            COUNT(*) as total_count,
            COALESCE(SUM(gmv_amt), 0) as total_gmv_amt,
            COALESCE(SUM(actual_amt), 0) as total_actual_amt,
            COALESCE(SUM(only_refund_amt), 0) as total_only_refund_amt
        FROM ads_channel_daily_pay_df {where_clause}
    """
    stats_row = conn.execute(stats_query, params).fetchone()
    stats = {
        'total_count': stats_row['total_count'],
        'total_gmv_amt': f"{stats_row['total_gmv_amt']:.2f}" if stats_row['total_gmv_amt'] else '0.00',
        'total_actual_amt': f"{stats_row['total_actual_amt']:.2f}" if stats_row['total_actual_amt'] else '0.00',
        'total_only_refund_amt': f"{stats_row['total_only_refund_amt']:.2f}" if stats_row['total_only_refund_amt'] else '0.00'
    }
    
    offset = (page - 1) * per_page
    query = f"""
        SELECT * FROM ads_channel_daily_pay_df 
        {where_clause}
        ORDER BY dt DESC, shop_id
        LIMIT ? OFFSET ?
    """
    rows = conn.execute(query, params + [per_page, offset]).fetchall()
    
    total_count = stats['total_count']
    total_pages = (total_count + per_page - 1) // per_page
    
    pagination = None
    if total_pages > 1:
        pagination = {
            'page': page,
            'pages': total_pages,
            'has_prev': page > 1,
            'prev_page': page - 1,
            'has_next': page < total_pages,
            'next_page': page + 1
        }
    
    conn.close()
    
    filters = {
        'dt': dt,
        'shop_id': shop_id,
        'shop_name': shop_name,
        'platformname': platformname
    }
    
    return render_template_string(HTML_TEMPLATE, data=rows, filters=filters, stats=stats, pagination=pagination)

@app.route('/api/data')
def api_data():
    """API 接口 - 返回 JSON 数据"""
    dt = request.args.get('dt', '')
    shop_id = request.args.get('shop_id', '')
    shop_name = request.args.get('shop_name', '')
    platformname = request.args.get('platformname', '')
    
    conditions = []
    params = []
    
    if dt:
        conditions.append("dt = ?")
        params.append(dt)
    if shop_id:
        conditions.append("shop_id LIKE ?")
        params.append(f"%{shop_id}%")
    if shop_name:
        conditions.append("shop_name LIKE ?")
        params.append(f"%{shop_name}%")
    if platformname:
        conditions.append("platformname LIKE ?")
        params.append(f"%{platformname}%")
    
    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)
    
    conn = get_db_connection()
    query = f"""
        SELECT * FROM ads_channel_daily_pay_df 
        {where_clause}
        ORDER BY dt DESC, shop_id
        LIMIT 1000
    """
    rows = conn.execute(query, params).fetchall()
    conn.close()
    
    result = []
    for row in rows:
        result.append({
            'dt': row['dt'],
            'shop_id': row['shop_id'],
            'shop_name': row['shop_name'],
            'platformname': row['platformname'],
            'distributorname': row['distributorname'],
            'fashion_code': row['fashion_code'],
            'main_picture': row['main_picture'],
            'supplier_name': row['supplier_name'],
            'level1': row['level1'],
            'level2': row['level2'],
            'level3': row['level3'],
            'level4': row['level4'],
            'level5': row['level5'],
            'series_value': row['series_value'],
            'gmv_amt': row['gmv_amt'],
            'gmv_cnt': row['gmv_cnt'],
            'send_amt': row['send_amt'],
            'send_cnt': row['send_cnt'],
            'actual_amt': row['actual_amt'],
            'actual_cnt': row['actual_cnt'],
            'only_refund_amt': row['only_refund_amt'],
            'only_refund_cnt': row['only_refund_cnt'],
            'return_amt': row['return_amt'],
            'return_cnt': row['return_cnt'],
            'service_fee_amount': row['service_fee_amount'],
            'updated_at': row['updated_at']
        })
    
    return jsonify({
        'code': 200,
        'data': result,
        'count': len(result)
    })

@app.route('/api/stats')
def api_stats():
    """API 接口 - 返回统计数据"""
    dt = request.args.get('dt', '')
    shop_id = request.args.get('shop_id', '')
    shop_name = request.args.get('shop_name', '')
    platformname = request.args.get('platformname', '')
    
    conditions = []
    params = []
    
    if dt:
        conditions.append("dt = ?")
        params.append(dt)
    if shop_id:
        conditions.append("shop_id LIKE ?")
        params.append(f"%{shop_id}%")
    if shop_name:
        conditions.append("shop_name LIKE ?")
        params.append(f"%{shop_name}%")
    if platformname:
        conditions.append("platformname LIKE ?")
        params.append(f"%{platformname}%")
    
    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)
    
    conn = get_db_connection()
    query = f"""
        SELECT 
            COUNT(*) as total_count,
            COALESCE(SUM(gmv_amt), 0) as total_gmv_amt,
            COALESCE(SUM(gmv_cnt), 0) as total_gmv_cnt,
            COALESCE(SUM(actual_amt), 0) as total_actual_amt,
            COALESCE(SUM(actual_cnt), 0) as total_actual_cnt,
            COALESCE(SUM(only_refund_amt), 0) as total_only_refund_amt,
            COALESCE(SUM(return_amt), 0) as total_return_amt,
            COALESCE(SUM(service_fee_amount), 0) as total_service_fee
        FROM ads_channel_daily_pay_df {where_clause}
    """
    row = conn.execute(query, params).fetchone()
    conn.close()
    
    return jsonify({
        'code': 200,
        'data': {
            'total_count': row['total_count'],
            'total_gmv_amt': row['total_gmv_amt'] or 0,
            'total_gmv_cnt': row['total_gmv_cnt'] or 0,
            'total_actual_amt': row['total_actual_amt'] or 0,
            'total_actual_cnt': row['total_actual_cnt'] or 0,
            'total_only_refund_amt': row['total_only_refund_amt'] or 0,
            'total_return_amt': row['total_return_amt'] or 0,
            'total_service_fee': row['total_service_fee'] or 0
        }
    })

if __name__ == '__main__':
    init_db()
    print("启动 Flask 服务...")
    print("访问地址：http://localhost:5000")
    print("局域网访问：http://<本机 IP>:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
