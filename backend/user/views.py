"""
详细文档在后期完善
user.view 描述和用户相关的API
"""
from copy import copy
from django.utils.datastructures import MultiValueDictKeyError

from rest_framework.views import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken import views as rest_auth

from calorie.api import APIView
from calorie.api import FieldException
from calorie.settings import DEBUG

from user.serializers import UserSerializer
class UserLoginAPI(rest_auth.ObtainAuthToken):
    """
    该API用于用户登录，继承自rfw的rest_auth.ObtainAuthToken，将用于认证身份的token发给前端
    """
    def post(self, request, *args, **kwargs):
        """
        Login API
        """
        # Add something for miniapp
        # Django just need two key-value -- username and password -- in request.data
        login_data = copy(request.data)
        try:
            assert login_data['code'] is not None
        except MultiValueDictKeyError as _:
            print('没有code')
            if DEBUG:
                return super().post(request, *args, **kwargs)
            return Response(data={'msg': '登录失败'}, status=status.HTTP_401_UNAUTHORIZED) # 401.1?
        else:
            print('有code')
            login_data['username'] = self.get_openid(login_data['code'])
            login_data['password'] = self.get_password(login_data['username'])
            serializer = self.serializer_class(data=login_data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})

    def get_openid(self, code):
        """
        向微信接口请求openid
        """
        # 注意可能超时和其他的异常
        return code

    def get_password(self, username):
        """
        得到登录密码
        """
        return username

class UserProfileAPI(APIView):
    """
    该API用于获取或者修改用户信息
    """
    def post(self, request):
        """
        修改用户信息
        """
        required_fields = ('name', 'weight')
        for required_field in required_fields:
            if required_field not in request.data:
                raise FieldException("没有字段%s"%required_field)
        user_obj = request.user
        user_obj.name = request.data['name']
        user_obj.weight = request.data['weight']
        user_obj.save()
        return self.success()
    def get(self, request):
        """
        获取用户信息
        """
        user_obj = request.user
        serializer = UserSerializer(user_obj)
        try:
            return self.success(data=serializer.data)
        except Exception as _:
            return self.error(err=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Create your views here.