from django.db.models import Sum

from recipes.models import RecipeComponent


def get_shopping_cart(user):
    components = RecipeComponent.objects.filter(
        recipe__cart__user=user
    ).order_by(
        'component__name',
    ).values(
        'component__name',
        'component__unit__name',
    ).annotate(amount=Sum('amount'))
    data = []
    for component in components:
        data.append(
            f'{component["component__name"]} '
            f'({component["component__unit__name"]}) - '
            f'{component["amount"]}'
        )
    content = '\n'.join(data)
    return content
