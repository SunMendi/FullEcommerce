from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from django.conf import settings

class FacebookWebhookView(APIView):
    # Pro tip: We will bypass authentication for this endpoint because Meta's servers are calling it!
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        """
        Handles the one-time Facebook Webhook handshake verification.
        """
        # 1. Extract query parameters from Facebook request
        mode = request.query_params.get('hub.mode')
        token = request.query_params.get('hub.verify_token')
        challenge = request.query_params.get('hub.challenge')

        # 2. Check if this is a verification request
        if mode == 'subscribe' and token:
            # 3. Compare the token sent by Facebook with our locally configured secret
            # We will define settings.FACEBOOK_VERIFY_TOKEN in settings.py!
            if token == getattr(settings, 'FACEBOOK_VERIFY_TOKEN', 'my_default_fallback_secret'):
                # 4. If matched, return the challenge as PLAIN TEXT (Status 200)
                # Note: We use Django's HttpResponse to prevent DRF from JSON-encoding the challenge
                return HttpResponse(challenge, content_type="text/plain", status=status.HTTP_200_OK)
            else:
                # 5. Token doesn't match! Return 403 Forbidden
                return Response(
                    {"error": "Verification token mismatch."}, 
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # 6. Invalid query format, return 400 Bad Request
        return Response(
            {"error": "Invalid verification parameters."}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    def post(self, request):
        """
        Receives real-time customer messages from Facebook and prints them to the terminal.
        """
        # 1. Extract the JSON data from the request
        data = request.data

        # 2. Verify that this is a page event subscription
        if data.get("object") == "page":
            try:
                # 3. Loop through entries (Facebook can batch multiple messages together)
                for entry in data.get("entry", []):
                    # 4. Loop through the messaging events in this entry
                    for messaging_event in entry.get("messaging", []):
                        # 5. Check if it's a standard message event
                        if "message" in messaging_event:
                            sender_psid = messaging_event["sender"]["id"]
                            recipient_page_id = messaging_event["recipient"]["id"]
                            message_text = messaging_event["message"].get("text")
                            message_id = messaging_event["message"].get("mid")

                            # 6. Print the message with vibrant formatting so we can see it live!
                            print("\n" + "="*50)
                            print("🚀 [FACEBOOK WEBHOOK] NEW MESSAGE RECEIVED!")
                            print("="*50)
                            print(f"👤 Sender (PSID)   : {sender_psid}")
                            print(f"📄 Page ID          : {recipient_page_id}")
                            print(f"💬 Message ID       : {message_id}")
                            print(f"📝 Text             : '{message_text}'")
                            print("="*50 + "\n")

                            # TODO: In Phase 3, we will save this to the DB and trigger our AI worker!

                # 7. Always return a 200 OK within 2 seconds so Facebook doesn't retry
                return Response({"status": "EVENT_RECEIVED"}, status=status.HTTP_200_OK)

            except Exception as e:
                # Catch any parsing errors and return 500
                return Response({"error": "Error parsing webhook event"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 8. Return 404 if the request is not a page object
        return Response(status=status.HTTP_404_NOT_FOUND)