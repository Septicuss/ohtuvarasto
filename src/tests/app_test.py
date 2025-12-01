import unittest
from app import app, warehouses, warehouse_id_counter


class TestFlaskApp(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.app.testing = True
        self.client = self.app.test_client()
        warehouses.clear()
        warehouse_id_counter[0] = 0

    def test_index_page_loads(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Warehouse Management', response.data)

    def test_create_warehouse_page_loads(self):
        response = self.client.get('/warehouse/create')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Create New Warehouse', response.data)

    def test_create_warehouse_post(self):
        response = self.client.post(
            '/warehouse/create',
            data={'name': 'Test Warehouse', 'tilavuus': '100', 'alku_saldo': '50'},
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(warehouses), 1)
        warehouse = warehouses[1]
        self.assertEqual(warehouse['name'], 'Test Warehouse')
        self.assertEqual(warehouse['varasto'].tilavuus, 100.0)
        self.assertEqual(warehouse['varasto'].saldo, 50.0)

    def test_create_warehouse_without_name(self):
        response = self.client.post(
            '/warehouse/create',
            data={'name': '', 'tilavuus': '100', 'alku_saldo': '0'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Name is required', response.data)
        self.assertEqual(len(warehouses), 0)

    def test_create_warehouse_invalid_values(self):
        response = self.client.post(
            '/warehouse/create',
            data={'name': 'Test', 'tilavuus': 'invalid', 'alku_saldo': '0'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid numeric values', response.data)
        self.assertEqual(len(warehouses), 0)

    def test_view_warehouse(self):
        self.client.post(
            '/warehouse/create',
            data={'name': 'Test Warehouse', 'tilavuus': '100', 'alku_saldo': '50'}
        )
        response = self.client.get('/warehouse/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Warehouse', response.data)
        self.assertIn(b'100', response.data)
        self.assertIn(b'50', response.data)

    def test_view_nonexistent_warehouse(self):
        response = self.client.get('/warehouse/999', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Warehouse Management', response.data)

    def test_edit_warehouse_page_loads(self):
        self.client.post(
            '/warehouse/create',
            data={'name': 'Test Warehouse', 'tilavuus': '100', 'alku_saldo': '50'}
        )
        response = self.client.get('/warehouse/1/edit')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Edit', response.data)
        self.assertIn(b'Test Warehouse', response.data)

    def test_edit_warehouse_post(self):
        self.client.post(
            '/warehouse/create',
            data={'name': 'Test Warehouse', 'tilavuus': '100', 'alku_saldo': '50'}
        )
        response = self.client.post(
            '/warehouse/1/edit',
            data={'name': 'Updated Warehouse', 'tilavuus': '200'},
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        warehouse = warehouses[1]
        self.assertEqual(warehouse['name'], 'Updated Warehouse')
        self.assertEqual(warehouse['varasto'].tilavuus, 200.0)
        self.assertEqual(warehouse['varasto'].saldo, 50.0)

    def test_edit_warehouse_invalid_capacity(self):
        self.client.post(
            '/warehouse/create',
            data={'name': 'Test Warehouse', 'tilavuus': '100', 'alku_saldo': '50'}
        )
        response = self.client.post(
            '/warehouse/1/edit',
            data={'name': 'Updated', 'tilavuus': 'invalid'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid capacity value', response.data)

    def test_delete_warehouse(self):
        self.client.post(
            '/warehouse/create',
            data={'name': 'Test Warehouse', 'tilavuus': '100', 'alku_saldo': '50'}
        )
        self.assertEqual(len(warehouses), 1)
        response = self.client.post(
            '/warehouse/1/delete',
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(warehouses), 0)

    def test_add_to_warehouse(self):
        self.client.post(
            '/warehouse/create',
            data={'name': 'Test Warehouse', 'tilavuus': '100', 'alku_saldo': '0'}
        )
        response = self.client.post(
            '/warehouse/1/add',
            data={'maara': '25'},
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(warehouses[1]['varasto'].saldo, 25.0)

    def test_add_to_nonexistent_warehouse(self):
        response = self.client.post(
            '/warehouse/999/add',
            data={'maara': '25'},
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)

    def test_remove_from_warehouse(self):
        self.client.post(
            '/warehouse/create',
            data={'name': 'Test Warehouse', 'tilavuus': '100', 'alku_saldo': '50'}
        )
        response = self.client.post(
            '/warehouse/1/remove',
            data={'maara': '20'},
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(warehouses[1]['varasto'].saldo, 30.0)

    def test_remove_from_nonexistent_warehouse(self):
        response = self.client.post(
            '/warehouse/999/remove',
            data={'maara': '20'},
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)

    def test_multiple_warehouses(self):
        self.client.post(
            '/warehouse/create',
            data={'name': 'Warehouse 1', 'tilavuus': '100', 'alku_saldo': '0'}
        )
        self.client.post(
            '/warehouse/create',
            data={'name': 'Warehouse 2', 'tilavuus': '200', 'alku_saldo': '50'}
        )
        self.assertEqual(len(warehouses), 2)
        response = self.client.get('/')
        self.assertIn(b'Warehouse 1', response.data)
        self.assertIn(b'Warehouse 2', response.data)
