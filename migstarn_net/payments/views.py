import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .services import PaymentService


@csrf_exempt
def daraja_callback(request):
    if request.method != "POST":
        return JsonResponse(
            {
                "ResultCode": 1,
                "ResultDesc": "Only POST requests are allowed.",
            },
            status=405,
        )

    try:
        payload = json.loads(request.body)

    except json.JSONDecodeError:
        return JsonResponse(
            {
                "ResultCode": 1,
                "ResultDesc": "Invalid JSON",
            },
            status=400,
        )

    print("\n========== DARAJA CALLBACK ==========")
    print(json.dumps(payload, indent=2))
    print("=====================================\n")

    try:
        payment = PaymentService.process_daraja_callback(
            payload
        )

        if payment is None:
            print(
                "WARNING: No payment found for "
                "CheckoutRequestID."
            )

            # Still acknowledge the callback so that
            # Safaricom does not keep retrying it.
            return JsonResponse(
                {
                    "ResultCode": 0,
                    "ResultDesc": "Accepted",
                }
            )

        print(
            f"Payment {payment.reference} processed: "
            f"{payment.status}"
        )

        return JsonResponse(
            {
                "ResultCode": 0,
                "ResultDesc": "Accepted",
            }
        )

    except Exception as exc:
        print(
            f"ERROR processing Daraja callback: {exc}"
        )

        return JsonResponse(
            {
                "ResultCode": 1,
                "ResultDesc": "Callback processing failed.",
            },
            status=500,
        )