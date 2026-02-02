from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([AllowAny])
def stub_timeline(request, employee_id, date):
    """
    Stub for /attendance/{id}/timeline/{date}/
    Returns empty blocks to prevent frontend crash.
    """
    return Response({
        "blocks": []
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def stub_explanation(request, employee_id, date):
    """
    Stub for /attendance/{id}/explanation/{date}/
    Returns empty analysis to prevent frontend crash.
    """
    return Response({
        "summary": "Data not available in DEV mode",
        "anomalies": [],
        "recommendations": []
    })
