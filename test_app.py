import os
import tempfile
import unittest

import app as expense_app


class ExpenseTests(unittest.TestCase):
    def setUp(self):
        self.fd, self.path = tempfile.mkstemp()
        expense_app.app.config.update(DATABASE=self.path, TESTING=True)
        expense_app.init_db()
        self.client = expense_app.app.test_client()

    def tearDown(self):
        os.close(self.fd)
        os.unlink(self.path)

    def add(self, title="Lunch", amount="150", category="Food", date="2026-11-01"):
        return self.client.post("/add", data=dict(title=title, amount=amount, category=category,
                                                  spent_on=date), follow_redirects=True)

    def test_add_and_total(self):
        self.add(amount="100")
        r = self.add(title="Bus", amount="50", category="Travel")
        self.assertIn(b"Bus", r.data)
        self.assertIn(b"150.00", r.data)

    def test_invalid_amount_rejected(self):
        r = self.add(amount="-5")
        self.assertIn(b"valid title", r.data)

    def test_filter_by_category(self):
        self.add(title="Pizza", category="Food")
        self.add(title="Metro", category="Travel")
        r = self.client.get("/?category=Travel")
        self.assertIn(b"Metro", r.data)
        self.assertNotIn(b"Pizza", r.data)

    def test_delete(self):
        self.add(title="Temp")
        self.client.post("/delete/1", follow_redirects=True)
        self.assertNotIn(b"Temp", self.client.get("/").data)


if __name__ == "__main__":
    unittest.main()
