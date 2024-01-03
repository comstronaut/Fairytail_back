from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets
from product.models import *
from .serializer import *
from rest_framework.generics import *
from django.views.generic.list import BaseListView
from django.views.generic.detail import BaseDetailView
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import *
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.filters import OrderingFilter
import requests
from datetime import datetime
#from openai import OpenAI
#from google.cloud import speech
import io
from PIL import Image
from django.core.files.base import ContentFile
from io import BytesIO

from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter

class PostCustomPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100

class BookDetailCustomPagination(PageNumberPagination):
    page_size = 1
    max_page_size = 100

# 아래는 'dasomi' 가 추가
#client = OpenAI(api_key="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")
# Create your views here.


#chatGPT에게 채팅 요청 API
# def chatGPT(request):
    
#     completion = client.chat.completions.create(model="gpt-3.5-turbo",
#     messages=[{"role": "user", "content": "오늘의 날씨는?"}])
#     print(completion)
#     result = completion.choices[0].message.content
    
#     return HttpResponse(result)

# # Google STT API를 이용한 음성 파일 변환
# def transcribe_audio(request):
#     if request.method == 'POST':
#         audio_file = request.FILES['audio']
#         client = speech.SpeechClient()

#         audio_bytes = audio_file.read()
#         audio = speech.RecognitionAudio(content=audio_bytes)
#         config = speech.RecognitionConfig(
#             encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
#             language_code='ko-KR')

#         response = client.recognize(config=config, audio=audio)
#         transcripts = [result.alternatives[0].transcript for result in response.results]

#         return JsonResponse({'transcripts': transcripts})
#     else:
#         return JsonResponse({'error': 'Invalid request'}, status=400)
    
#     """
#     1. set GOOGLE_APPLICATION_CREDENTIALS=C:\Users\user\Desktop\speechto-text-409222-178e315d8f2c.json <- 바탕화면에 있는 키 json파일 설정

# 2. python manage.py shell 실행

# 3.from google.cloud import speech    <- shell에 입력
# import io

# # Google Cloud Speech 클라이언트 초기화
# client = speech.SpeechClient()

# # 음성 파일 불러오기
# file_path = 'C:\\Users\\user\\Desktop\\example.wav'
# with io.open(file_path, 'rb') as audio_file:
#     content = audio_file.read()

# audio = speech.RecognitionAudio(content=content)
# config = speech.RecognitionConfig(
#     encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
#     language_code='ko-KR'
# )

# # STT 요청 및 응답
# response = client.recognize(config=config, audio=audio)

# # 결과 출력
# for result in response.results:
#     print('Transcript:', result.alternatives[0].transcript) <- 입력 후 Enter 두번 텍스트로 변환되는거 확인가능.
    
#     """
    
# Create your views here.
# class BookViewSet(viewsets.ModelViewSet):
#     queryset = BookList.objects.all()
#     serializer_class = BookSerializer

class BookListView(ListCreateAPIView):
    queryset = BookList.objects.all()
    serializer_class = BookSerializer
    authentication_classes = [BasicAuthentication, SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

class BookListDetailView(CreateAPIView):
    queryset = BookDetail.objects.all()
    serializer_class = BookDetailSerializer
    authentication_classes = [BasicAuthentication, SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]   

class BookDetailView(ListCreateAPIView):

    def get_queryset(self):
        bookList = get_object_or_404(BookList, pk=self.kwargs['BookList_id'])
        queryset = BookDetail.objects.filter(BookList=bookList.id)
        return queryset
    
    serializer_class = BookDetailSerializer
    pagination_class = BookDetailCustomPagination
    authentication_classes = [BasicAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

class QuizListView(ListCreateAPIView):
    queryset = QuizList.objects.all()
    serializer_class = QuizListSerializer
    authentication_classes = [BasicAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

class WordListView(ListCreateAPIView):
    queryset = WordList.objects.all()
    serializer_class = WordListSerializer
    authentication_classes = [BasicAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

class AiAudioListView(ListCreateAPIView):
    queryset = AiAudioList.objects.all()
    serializer_class = AiAudioListSerializer
    authentication_classes = [BasicAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

class CreateUserView(ListCreateAPIView):
    queryset = User.objects.all()
    model = User
    serializer_class = UserSerializer

class GetUser(RetrieveAPIView):
    queryset = User.objects.all()
    model = User
    serializer_class = UserSerializer

class Postview(ListCreateAPIView):
    authentication_classes = [BasicAuthentication, SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Post.objects.all()
    serializer_class=PostSerializer
    pagination_class = PostCustomPagination
    filter_backends = [OrderingFilter, SearchFilter]
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    search_fields = ['title', 'content']
    
class postRetrieveview(APIView):
    authentication_classes = [BasicAuthentication, SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    def get_object(self, pk):
        try:
            return Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            raise Http404
    
    # 조회
    def get(self, request, pk, format=None):
        book = self.get_object(pk)
        serializer = PostSerializer(book)
        return Response(serializer.data)

    # # 등록
    # def post(self, request, pk, format=None):
    #     book = self.get_object(pk)
    #     serializer = BookSerializer(book, data=request.data) 
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data) 
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 수정
    def put(self, request, pk, format=None):
        book = self.get_object(pk)
        serializer = PostSerializer(book, data=request.data) 
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data) 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 삭제
    def delete(self, request, pk, format=None):
        book = self.get_object(pk)
        book.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)      
    
class commentuploadview(APIView):
    authentication_classes = [BasicAuthentication, SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    def get_object(self, pk):
        try:
            return comment.objects.get(pk=pk)
        except comment.DoesNotExist:
            raise Http404
    
    # 조회
    def get(self, request, pk, format=None):
        book = self.get_object(pk=pk)
        serializer = commentSerializer(book)
        return Response(serializer.data)

    # 등록
    def post(self, request, pk, format=None):
        book = self.get_object(pk)
        serializer = commentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 수정
    def put(self, request, pk, id, format=None):
        book = self.get_object(id)
        serializer = commentSerializer(book, data=request.data) 
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data) 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 삭제
    def delete(self, request, id, format=None):
        book = self.get_object(id)
        book.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class LearningStatusview(APIView):
    authentication_classes = [BasicAuthentication, SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    def get_object(self, pk):
        return LearningStatus.objects.filter(User=pk)
        
    def get(self, request, pk, format=None):
        learning_statuses = self.get_object(pk)
        serializer = LearningStatusSerializer(learning_statuses, many=True)
        wrong_list = [i for i in serializer.data if not i['is_right']]
        wrongpercentage = (len(wrong_list) / len(serializer.data)) * 100
        grouped_data={}
        for i in serializer.data:
            date_str=i['created_at']
            created_at = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%f')
            month = created_at.month
            if month in grouped_data:
                grouped_data[month]+=1
            else:
                grouped_data[month]=1
        groupdata=sorted(list(grouped_data.items()))
        grouped_data=[]
        month_data=[]
        for x,y in groupdata:
            grouped_data.append(str(x)+'월')
            month_data.append(y)
        numdata=len(serializer.data)
        return Response({'User' : pk, 'wrongpercentage' : wrongpercentage, 'numdata' : numdata, 'grouped_data': grouped_data ,'month_data' : month_data})
    
class ReadingStatusview(APIView):
    authentication_classes = [BasicAuthentication, SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    def get_object(self, pk):
        return ReadingStatus.objects.filter(User=pk)
        
        
    def get(self, request, pk, format=None):
        book=self.get_object(pk)
        serializer = ReadingStatusSerializer(book,many=True)
        read_list = [i for i in serializer.data]
        readbook = len(read_list)
        return Response({'User' : pk, 'readbook' : read_list, 'readbooknum' : readbook})
    
class CommentCreateView(CreateAPIView):
    authentication_classes = [BasicAuthentication, SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = comment.objects.all()
    model = comment
    serializer_class = commentSerializer

class PostMediaView(ListCreateAPIView):
    authentication_classes = [BasicAuthentication, SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Media.objects.all()
    serializer_class = MediaSerializer

    def resize_image(self, image, size=(300, 300)):
        """ 이미지 크기를 조절하는 함수 """
        img = Image.open(image)
        img.convert('RGB')
        img.thumbnail(size, Image.Resampling.LANCZOS)

        temp_file = BytesIO()
        img.save(temp_file, 'JPEG')
        temp_file.seek(0)

        return ContentFile(temp_file.read(), name=image.name)

    def perform_create(self, serializer):
        media_file = serializer.validated_data.get('media_path')
        if media_file and hasattr(media_file, 'content_type') and media_file.content_type.startswith('image/'):
            resized_image = self.resize_image(media_file)
            serializer.save(media_path=resized_image)
        else:
            serializer.save()