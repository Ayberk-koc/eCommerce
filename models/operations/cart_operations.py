from sqlalchemy.orm import Session
from models.models import Cart, CartItem
from models.model_operations import parse_query_result_as_json
from sqlalchemy import text


# könnte machen, dass alles über query auläuft, und ich die models nicht mehr brauche, dann ist aber
# die crud methoden richtig arsch
def get_cart_info(db: Session, cart_id):
    """hier kommt die cart in dict form mit den produkten als inhalt (ähnlich wie bei json response)"""
    cart = db.query(Cart).filter(Cart.id == cart_id).first()
    if not cart:
        return {}

    cart_items_query = text("""
    SELECT JSON_OBJECT(
    'id', products.id,
    'name', products.name,
    'description', products.description,
    'price', products.price,
    'quantity', cart_items.quantity,
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
    ) as cart_content
    FROM cart_items JOIN products ON cart_items.product_id = products.id
    WHERE cart_id = :cart_id;
    """).params(cart_id=cart_id)

    cart_content = parse_query_result_as_json(db, cart_items_query).get("cart_content", [])
    total_items = 0
    total_price = 0
    for item in cart_content:
        total_items += item.get("quantity", 0)
        total_price += item.get("quantity", 0) * item.get("price", 0)
    cart_data = {"cart_id": cart_id, "total_items": total_items, "total_price": total_price, "cart_contents": cart_content}

    return cart_data


def calc_price_list(cart_data):
    contents = cart_data.get("cart_contents", [])
    price_list = [elem.get("quantity", 0) * elem.get("price", 0) for elem in contents]
    return price_list


def add_to_cart(db: Session, cart_id, product_id, quantity):
    cart = db.query(Cart).filter(Cart.id == cart_id).first()
    if not cart:
        cart = Cart(id=cart_id)
        db.add(cart)

    item_to_add = db.query(CartItem).filter(CartItem.cart_id == cart_id, CartItem.product_id == product_id).first()
    if item_to_add:
        item_to_add.quantity += quantity
    else:
        item_to_add = CartItem(cart_id=cart_id, product_id=product_id, quantity=quantity)
        db.add(item_to_add)

    db.commit()


def remove_from_cart(db: Session, cart_id, product_id):
    cart = db.query(Cart).filter(Cart.id == cart_id).first()
    if not cart:
        return None

    item_to_remove = db.query(CartItem).filter(CartItem.cart_id == cart_id, CartItem.product_id == product_id).first()
    if not item_to_remove:
        return

    if item_to_remove.quantity == 1:
        db.delete(item_to_remove)
    else:
        item_to_remove.quantity -= 1

    db.commit()





