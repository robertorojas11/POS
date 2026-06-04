from app.models.user import User, UserType
from app.models.product import Category, Product
from app.models.inventory import InventoryLog
from app.models.sale import Sale, SaleItem, Discount
from app.models.customer import Customer
from app.models.shift import Shift

# All models listed for easy import by migrations / other files
__all__ = [
    'User',
    'UserType',
    'Category',
    'Product',
    'InventoryLog',
    'Sale',
    'SaleItem',
    'Discount',
    'Customer',
    'Shift'
]
