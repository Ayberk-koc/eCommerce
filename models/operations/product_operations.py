from models.model_operations import parse_query_results
from sqlalchemy.orm import Session
from sqlalchemy import text

def get_products_info(db: Session):
    """die key "price" bekommst du als Decimal. Dies ist ein datentyp und du musst nicht konvertieren!"""
    product_query = text("SELECT * FROM products;")
    result = parse_query_results(db, product_query)

    return result

# hier fehelt noch eine methode, wie ich die items aus dem shop in meine db schreibe. Hierfür brauche ich die
# printiyf api














