from django.test import TestCase
from .models import VigenciaPlan

class VigenciaPlanTests(TestCase):

    def setUp(self):
        self.vigencia_plan = VigenciaPlan.objects.create(
            # Add fields according to your model definition
            # Example:
            # nombre='Plan A',
            # valor=100.00,
            # descuento=10,
            # fecha_inicio='2023-01-01',
            # fecha_fin='2023-12-31',
            # etc.
        )

    def test_vigencia_plan_creation(self):
        self.assertEqual(self.vigencia_plan.nombre, 'Plan A')  # Adjust according to your fields

    def test_vigencia_plan_update(self):
        self.vigencia_plan.descuento = 20
        self.vigencia_plan.save()
        self.assertEqual(self.vigencia_plan.descuento, 20)

    def test_vigencia_plan_str(self):
        self.assertEqual(str(self.vigencia_plan), 'Plan A')  # Adjust according to your __str__ method

    def test_vigencia_plan_fields(self):
        self.assertTrue(hasattr(self.vigencia_plan, 'valor'))
        self.assertTrue(hasattr(self.vigencia_plan, 'descuento'))
        self.assertTrue(hasattr(self.vigencia_plan, 'fecha_inicio'))
        self.assertTrue(hasattr(self.vigencia_plan, 'fecha_fin'))