from flask import Blueprint, request, jsonify
from ..models.models import db, FavoriteRoute
from .auth import token_required
import json
import datetime

routes_bp = Blueprint('routes_api', __name__, url_prefix='/api/routes')

@routes_bp.route('', methods=['POST'])
@token_required
def save_route(current_user):
    """
    收藏路线
    """
    data = request.get_json()
    
    if not data or not data.get('startName') or not data.get('endName'):
        return jsonify({"message": "起点和终点名称不能为空"}), 400
    
    if not data.get('distance') or not data.get('walkTime') or not data.get('bikeTime'):
        return jsonify({"message": "路线信息不完整"}), 400
    
    name = data.get('name') or f"{data['startName']} → {data['endName']}"
    
    start_position = json.dumps(data.get('startPosition')) if data.get('startPosition') else None
    end_position = json.dumps(data.get('endPosition')) if data.get('endPosition') else None
    
    existing = FavoriteRoute.query.filter_by(
        user_id=current_user.id,
        start_id=data.get('startId'),
        end_id=data.get('endId'),
        start_name=data['startName'],
        end_name=data['endName']
    ).first()
    
    if existing:
        return jsonify({
            "success": True,
            "message": "该路线已收藏",
            "routeId": existing.id
        }), 200
    
    new_route = FavoriteRoute(
        user_id=current_user.id,
        name=name,
        start_id=data.get('startId'),
        end_id=data.get('endId'),
        start_name=data['startName'],
        end_name=data['endName'],
        start_position=start_position,
        end_position=end_position,
        distance=data['distance'],
        walk_time=data['walkTime'],
        bike_time=data['bikeTime']
    )
    
    db.session.add(new_route)
    db.session.commit()
    
    return jsonify({
        "success": True,
        "message": "路线收藏成功",
        "routeId": new_route.id
    }), 201

@routes_bp.route('', methods=['GET'])
@token_required
def get_routes(current_user):
    """
    获取用户收藏的路线列表
    """
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 20, type=int)
    
    query = FavoriteRoute.query.filter_by(user_id=current_user.id).order_by(
        FavoriteRoute.created_at.desc()
    )
    
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)
    routes = pagination.items
    
    routes_data = []
    for route in routes:
        routes_data.append({
            "id": route.id,
            "name": route.name,
            "startId": route.start_id,
            "endId": route.end_id,
            "startName": route.start_name,
            "endName": route.end_name,
            "startPosition": json.loads(route.start_position) if route.start_position else None,
            "endPosition": json.loads(route.end_position) if route.end_position else None,
            "distance": route.distance,
            "walkTime": route.walk_time,
            "bikeTime": route.bike_time,
            "createdAt": route.created_at.isoformat() + 'Z'
        })
    
    return jsonify({
        "routes": routes_data,
        "total": pagination.total,
        "page": pagination.page,
        "pageSize": pagination.per_page,
        "pages": pagination.pages
    })

@routes_bp.route('/<int:route_id>', methods=['DELETE'])
@token_required
def delete_route(current_user, route_id):
    """
    删除收藏的路线
    """
    route = FavoriteRoute.query.filter_by(
        id=route_id,
        user_id=current_user.id
    ).first()
    
    if not route:
        return jsonify({"message": "路线不存在"}), 404
    
    db.session.delete(route)
    db.session.commit()
    
    return jsonify({
        "success": True,
        "message": "路线已删除"
    })

@routes_bp.route('/<int:route_id>', methods=['PUT'])
@token_required
def update_route(current_user, route_id):
    """
    更新路线名称
    """
    route = FavoriteRoute.query.filter_by(
        id=route_id,
        user_id=current_user.id
    ).first()
    
    if not route:
        return jsonify({"message": "路线不存在"}), 404
    
    data = request.get_json()
    if 'name' in data:
        route.name = data['name']
        route.updated_at = datetime.datetime.utcnow()
        db.session.commit()
    
    return jsonify({
        "success": True,
        "message": "路线名称已更新"
    })
