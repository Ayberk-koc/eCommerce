from sqlalchemy.orm import Session
from models.models import Cart, CartItem




def get_cart_info(db: Session, cart_id):
    """hier kommt die cart in dict form vor"""
    cart = db.query(Cart).filter(Cart.id == cart_id).first()
    if not cart:
        return None
    cart_items = db.query(CartItem).filter(CartItem.cart_id == cart_id)
    return {item.product_id: item.quantity for item in cart_items}      #hier anpassen, welche infos ich aus der cart haben will.


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





