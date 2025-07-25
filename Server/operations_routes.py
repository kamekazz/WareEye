from flask import Blueprint, render_template

operations_bp = Blueprint('operations', __name__, url_prefix='/ops')


@operations_bp.route('/loading-dashboard')
def loading_dashboard():
    return render_template('operations/loading_dashboard.html')
