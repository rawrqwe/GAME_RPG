from .models import InventoryItem


class ShopError(Exception):
    """Błąd operacji sklepowej (np. za mało złota, za mało przedmiotów)."""
    pass


def buy_item(character, item, quantity=1):
    total_cost = item.buy_price * quantity

    if character.gold < total_cost:
        raise ShopError("Za mało złota, aby kupić ten przedmiot.")

    character.gold -= total_cost
    character.save()

    inventory_item, created = InventoryItem.objects.get_or_create(
        character=character,
        item=item,
        defaults={"quantity": 0}
    )
    inventory_item.quantity += quantity
    inventory_item.save()

    return inventory_item


def sell_item(character, item, quantity=1):
    try:
        inventory_item = InventoryItem.objects.get(character=character, item=item)
    except InventoryItem.DoesNotExist:
        raise ShopError("Nie posiadasz tego przedmiotu")

    if inventory_item.quantity < quantity:
        raise ShopError("Nie masz tylu sztuk tego przedmiotu")

    total_income = item.sell_price * quantity
    character.gold += total_income
    character.save()

    inventory_item.quantity -= quantity
    if inventory_item.quantity == 0:
        inventory_item.delete()
    else:
        inventory_item.save()

    return total_income