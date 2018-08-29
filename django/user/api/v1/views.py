from . import (
    viewsets, status, SignInForm, SignUpForm, jwt, Response
)


class SignInViewSet(viewsets.ViewSet):

    def create(self, request):
        form = SignInForm(request.data)
        if form.submit():
            token = jwt.encode_user(form.object)
            return Response({'token': token}, status=status.HTTP_200_OK)
        return Response({'errors': form.errors}, status=status.HTTP_400_BAD_REQUEST)


class SignUpViewSet(viewsets.ViewSet):

    def create(self, request):
        form = SignUpForm(request.data)
        if form.submit():
            token = jwt.encode_user(form.object)
            return Response({'token': token}, status=status.HTTP_200_OK)
        return Response({'errors': form.errors}, status=status.HTTP_400_BAD_REQUEST)
