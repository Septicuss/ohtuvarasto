from flask import Flask, render_template, request, redirect, url_for
from varasto import Varasto


app = Flask(__name__)

# In-memory storage for warehouses - shared by all users
warehouses = {}
warehouse_id_counter = [0]


def get_next_id():
    warehouse_id_counter[0] += 1
    return warehouse_id_counter[0]


def parse_warehouse_form(form, fields):
    result = {}
    for field, default in fields.items():
        result[field] = form.get(field, default)
    return result


def handle_create_post():
    data = parse_warehouse_form(
        request.form, {'name': '', 'tilavuus': '0', 'alku_saldo': '0'}
    )
    name = data['name'].strip()

    try:
        tilavuus = float(data['tilavuus'])
        alku_saldo = float(data['alku_saldo'])
    except ValueError:
        return None, 'Invalid numeric values'

    if not name:
        return None, 'Name is required'

    warehouse_id = get_next_id()
    warehouses[warehouse_id] = {
        'name': name,
        'varasto': Varasto(tilavuus, alku_saldo)
    }
    return warehouse_id, None


@app.route('/')
def index():
    return render_template('index.html', warehouses=warehouses)


@app.route('/warehouse/create', methods=['GET', 'POST'])
def create_warehouse():
    if request.method == 'POST':
        _, error = handle_create_post()
        if error:
            return render_template('create_warehouse.html', error=error)
        return redirect(url_for('index'))
    return render_template('create_warehouse.html')

def handle_edit_post(warehouse):
    name = request.form.get('name', '').strip()
    tilavuus_str = request.form.get('tilavuus', '0')

    try:
        tilavuus = float(tilavuus_str)
    except ValueError:
        return 'Invalid capacity value'

    if not name:
        return 'Name is required'

    warehouse['name'] = name
    warehouse['varasto'] = Varasto(tilavuus, warehouse['varasto'].saldo)
    return None


@app.route('/warehouse/<int:warehouse_id>')
def view_warehouse(warehouse_id):
    if warehouse_id not in warehouses:
        return redirect(url_for('index'))
    return render_template(
        'view_warehouse.html',
        warehouse_id=warehouse_id,
        warehouse=warehouses[warehouse_id]
    )


@app.route('/warehouse/<int:warehouse_id>/edit', methods=['GET', 'POST'])
def edit_warehouse(warehouse_id):
    if warehouse_id not in warehouses:
        return redirect(url_for('index'))

    warehouse = warehouses[warehouse_id]

    if request.method == 'POST':
        error = handle_edit_post(warehouse)
        if error:
            return render_template(
                'edit_warehouse.html',
                warehouse_id=warehouse_id,
                warehouse=warehouse,
                error=error
            )
        return redirect(url_for('view_warehouse', warehouse_id=warehouse_id))

    return render_template(
        'edit_warehouse.html',
        warehouse_id=warehouse_id,
        warehouse=warehouse
    )


@app.route('/warehouse/<int:warehouse_id>/delete', methods=['POST'])
def delete_warehouse(warehouse_id):
    if warehouse_id in warehouses:
        del warehouses[warehouse_id]
    return redirect(url_for('index'))


@app.route('/warehouse/<int:warehouse_id>/add', methods=['POST'])
def add_to_warehouse(warehouse_id):
    if warehouse_id not in warehouses:
        return redirect(url_for('index'))

    maara_str = request.form.get('maara', '0')
    try:
        maara = float(maara_str)
    except ValueError:
        maara = 0

    warehouses[warehouse_id]['varasto'].lisaa_varastoon(maara)
    return redirect(url_for('view_warehouse', warehouse_id=warehouse_id))


@app.route('/warehouse/<int:warehouse_id>/remove', methods=['POST'])
def remove_from_warehouse(warehouse_id):
    if warehouse_id not in warehouses:
        return redirect(url_for('index'))

    maara_str = request.form.get('maara', '0')
    try:
        maara = float(maara_str)
    except ValueError:
        maara = 0

    warehouses[warehouse_id]['varasto'].ota_varastosta(maara)
    return redirect(url_for('view_warehouse', warehouse_id=warehouse_id))


if __name__ == '__main__':
    app.run(debug=True)
