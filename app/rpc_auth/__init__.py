from flask import Blueprint

auth_rpc = Blueprint("auth_rpc", __name__)

from .rpc_handler import rpc_bp
auth_rpc.register_blueprint(rpc_bp, url_prefix="/rpc")
