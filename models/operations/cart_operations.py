from sqlalchemy.orm import Session
from models.models import Cart, CartItem
from models.model_operations import parse_query_results
from sqlalchemy import text

# könnte machen, dass alles über query auläuft, und ich die models nicht mehr brauche, dann ist aber
# die crud methoden richtig arsch
def get_cart_info(db: Session, cart_id):
    """hier kommt die cart in dict form mit den produkten als inhalt (ähnlich wie bei json response)"""
    cart = db.query(Cart).filter(Cart.id == cart_id).first()
    if not cart:
        return {}

    cart_items_query = text("SELECT product_id, name, description, price, stock, quantity "
                            "FROM cart_items "
                            "JOIN products ON cart_items.product_id = products.id "
                            "WHERE cart_id = :cart_id;").params(cart_id=cart_id)

    result = parse_query_results(db, cart_items_query)
    total_items = 0
    total_price = 0
    for res in result:
        total_items += res.get("quantity", 0)
        total_price += res.get("quantity", 0) * res.get("price", 0)
    cart_data = {"cart_id": cart_id, "total_items": total_items, "total_price": total_price, "cart_contents": result}

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





