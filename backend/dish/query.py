"""
查询相关函数
"""
from functools import reduce
from django.db.models import F, FilteredRelation, Q
from django.db import transaction
from dish.models import Dish, Tag
from searchitem.models import SearchItem, HistorySearch

class DishQueryFunctionSet:
    """
    DishQueryFunctionSet
    函数返回Queryset
    """
    @staticmethod
    def name(user_obj, keyword):
        """通过关键词查询菜品"""
        DishQueryFunctionSet.add_search_item(user_obj, "dd", "32")
        return Dish.objects.filter(name__contains=keyword).annotate(
            t=FilteredRelation('likedish', condition=Q(likedish__user=user_obj)) # likedish__user_id=user_obj.id
        ).annotate(user_like=F('t__like')).annotate(user_dislike=1-F('t__like')).order_by('id')

    @staticmethod
    def tag_ids(user_obj, tag_list):
        """通过标签id查询菜品"""
        return reduce(
            lambda x, y: x & y,
            [Tag.objects.get(pk=tag_id).dish_set.annotate(
                t=FilteredRelation('likedish', condition=Q(likedish__user=user_obj)) # likedish__user_id=user_obj.id
            ).annotate(user_like=F('t__like')).annotate(user_dislike=1-F('t__like')) for tag_id in tag_list]
        ).order_by('id')

    @staticmethod
    def calorie(user_obj, min_calorie, max_calorie):
        """通过最小最大值查询"""
        return Dish.objects.filter(
            calorie__gt=min_calorie, calorie__lt=max_calorie).annotate(
                t=FilteredRelation('likedish', condition=Q(likedish__user=user_obj)) # likedish__user_id=user_obj.id
            ).annotate(user_like=F('t__like')).annotate(user_dislike=1-F('t__like')).order_by('id')

    @staticmethod
    def tag(user_obj, keyword):
        """通过标签查询菜品"""
        return Dish.objects.all().prefetch_related("tag").filter(tag__name__contains=keyword).annotate(
            t=FilteredRelation('likedish', condition=Q(likedish__user=user_obj)) # likedish__user_id=user_obj.id
        ).annotate(user_like=F('t__like')).annotate(user_dislike=1-F('t__like')).order_by('id')

    @staticmethod
    @transaction.atomic()
    def add_search_item(user_obj, category, content):
        """向数据库添加search item"""
        search_obj, _ = SearchItem.objects.get_or_create(name=content, category=category)
        HistorySearch.objects.create(user=user_obj, searchitem=search_obj)
        search_obj.count = F('count') + 1