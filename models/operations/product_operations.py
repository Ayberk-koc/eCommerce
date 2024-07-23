from models.model_operations import parse_query_result_as_json
from sqlalchemy.orm import Session
from sqlalchemy import text

def get_products_info(db: Session):
    """die key "price" bekommst du als Decimal. Dies ist ein datentyp und du musst nicht konvertieren!"""

    product_query = text("""
    SELECT JSON_OBJECT(
    'id', products.id,
    'name', products.name,
    'description', products.description,
    'price', products.price,
    'stock', products.stock,
    'images', COALESCE(
        (SELECT
            JSON_OBJECT('first_image', product_images.first_image,
                        'second_image', product_images.second_image,
                        'third_image', product_images.third_image,
                        'forth_image', product_images.forth_image,
                        'fifth_image', product_images.fifth_image)
        FROM product_images
        WHERE product_images.product_id = products.id), JSON_OBJECT()
        )
    ) as products
    FROM products;
    """)

    result = parse_query_result_as_json(db, product_query)
    return result

# hier fehelt noch eine methode, wie ich die items aus dem shop in meine db schreibe. Hierfür brauche ich die
# printiyf api














