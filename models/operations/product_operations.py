from models.models import Product
from models.model_operations import ModelSerializer
from sqlalchemy.orm import Session



def get_products_info(db: Session):
    """die key "price" bekommst du als Decimal. Dies ist ein datentyp und du musst nicht konvertieren!"""
    products = db.query(Product).all()
    return ModelSerializer.serialize(products)


















