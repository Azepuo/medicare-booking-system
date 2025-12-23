# app/rdv/api.py
from flask import Blueprint, jsonify, request
from datetime import date
from app.rpc_medecin import rdv as rdv_module  # ⬅️ Renommez l'import

bp = Blueprint('rdv_api', __name__, url_prefix='/rpc/rdv')

@bp.route('/list_today', methods=['GET'])
def list_today():
    d = request.args.get('date')
    try:
        the_date = date.fromisoformat(d) if d else date.today()
    except Exception:
        return jsonify({'ok': False, 'error': 'Format date invalide (YYYY-MM-DD attendu)'}), 400
    try:
        data = rdv_module.list_rdv_for_date(the_date)  # ⬅️ Utilisez le nouveau nom
        return jsonify({'ok': True, 'data': data})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@bp.route('/get/<int:rdv_id>', methods=['GET'])
def api_get(rdv_id):
    try:
        r = rdv_module.get_rdv(rdv_id)  # ⬅️ Utilisez le nouveau nom
        return jsonify({'ok': True, 'data': r})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@bp.route('/create', methods=['POST'])
def api_create():
    payload = request.get_json(force=True)
    try:
        new_rdv = rdv_module.create_rdv(payload)  # ⬅️ Utilisez le nouveau nom
        return jsonify({'ok': True, 'data': new_rdv}), 201
    except ValueError as e:
        return jsonify({'ok': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@bp.route('/update/<int:rdv_id>', methods=['PUT','PATCH'])
def api_update(rdv_id):
    payload = request.get_json(force=True)
    try:
        r = rdv_module.update_rdv(rdv_id, payload)  # ⬅️ Utilisez le nouveau nom
        if r is None:
            return jsonify({'ok': False, 'error': 'Not found'}), 404
        return jsonify({'ok': True, 'data': r})
    except ValueError as e:
        return jsonify({'ok': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@bp.route('/delete/<int:rdv_id>', methods=['DELETE'])
def api_delete(rdv_id):
    try:
        ok = rdv_module.delete_rdv(rdv_id)  # ⬅️ Utilisez le nouveau nom
        if not ok:
            return jsonify({'ok': False, 'error': 'Not found'}), 404
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@bp.route('/patients', methods=['GET'])
def api_patients():
    try:
        data = rdv_module.list_patients()  # ⬅️ Utilisez le nouveau nom
        return jsonify({'ok': True, 'data': data})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@bp.route('/medecins', methods=['GET'])
def api_medecins():
    try:
        data = rdv_module.list_medecins()  # ⬅️ Utilisez le nouveau nom
        return jsonify({'ok': True, 'data': data})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500
    
