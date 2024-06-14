from flask import Blueprint, current_app, session, redirect, url_for, send_file
import io

download_bp = Blueprint('download', __name__)

@download_bp.route('/admin/download/<int:homework_id>/<int:student_id>', methods=['GET'])
def download_homework_file(homework_id, student_id):
    current_user_id = session.get('user_id')
    if not current_user_id:
        return redirect(url_for('common.login'))

    with current_app.connection.cursor() as cursor:
        cursor.execute("""
            SELECT files, data_options FROM Solutions
            WHERE homework_id = %s AND student_id = %s
        """, (homework_id, student_id))
        result = cursor.fetchone()

    if result and result['files']:
        return send_file(
            io.BytesIO(result['files']),
            as_attachment=True,
            download_name=result['data_options']
        )
    return redirect(url_for('tables.view_solutions'))
