from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Session


def parse_query_results(db: Session, query: str, first=False) -> list[dict] | dict | None:
    """das ist eine funktion, um die ergebnisse der query in der form zu bekommen, in der ich sie möchte
    so wird jede row als object betrachtet (dictionary) und es werden die rows in einer liste ausgegeben, wie
    es bei einer json response auch ist"""
    query_result = db.execute(query)
    key = query_result.keys()
    rows = query_result.fetchall()

    result = [dict(zip(key, row)) for row in rows]

    if first:
        return result[0] if result else None
    else:
        return result


class ModelSerializer:
    @staticmethod
    def serialize(model):
        if not model:
            return None

        if isinstance(model, list):
            return [ModelSerializer.serialize(item) for item in model]

        # Get the model's columns
        columns = inspect(model).attrs.keys()

        # Create a dictionary of the model's attributes
        serialized_data = {}
        for column in columns:
            value = getattr(model, column)

            # Handle relationships
            if hasattr(value, '__table__'):
                # For single objects, just get the id
                serialized_data[column] = value.id
            elif isinstance(value, list):
                # For lists (like in many-to-many relationships), get a list of ids
                serialized_data[column] = [item.id for item in value]
            else:
                serialized_data[column] = value

        return serialized_data


class ProductSerializer(ModelSerializer):
    @staticmethod
    def serialize(product):
        base_serialized = ModelSerializer.serialize(product)
        # Add any product-specific serialization logic here
        return base_serialized


class OrderSerializer(ModelSerializer):
    @staticmethod
    def serialize(order):
        base_serialized = ModelSerializer.serialize(order)
        # Add any order-specific serialization logic here
        return base_serialized








