from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Event
from rest_framework.views import APIView
from .serializers import EventSerializer

# ✅ SAFE import (important)
try:
    from fastapi_app.tasks import process_event_invites
except Exception:
    process_event_invites = None


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_event(request):
    """
    API Endpoint to create an event.
    """

    title = request.data.get('title')
    description = request.data.get('description', '')
    date = request.data.get('date')

    if not title or not date:
        return Response(
            {"error": "Title and Date are required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # ✅ Save event
        new_event = Event.objects.create(
            title=title,
            description=description,
            date=date,
            creator=request.user
        )

        # ✅ Call Celery ONLY if available
        if process_event_invites:
            try:
                process_event_invites.delay(new_event.id, request.user.id)
            except Exception:
                pass  # Don't break app if Celery fails

        return Response(
            {
                "message": "Event created successfully!",
                "event_id": new_event.id
            },
            status=status.HTTP_201_CREATED
        )

    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class CreateEventAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = EventSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(creator=request.user)  # ✅ fixed field name
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
