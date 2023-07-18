from django.db.models import Sum
from django.shortcuts import get_object_or_404

from recipes.models import Recipe, RecipeComponent


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


def make(request, pk, serializer_class):
    user = request.user
    recipe = get_object_or_404(Recipe, pk=pk)
    data = {
        'user': user.id,
        'recipe': recipe.id,
    }
    serializer = serializer_class(data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return recipe
