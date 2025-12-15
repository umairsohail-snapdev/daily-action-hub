from typing import Any, Dict, Optional
from .base import ActionExecutor

class GmailExecutor(ActionExecutor):
    def execute(self, action_data: Dict[str, Any], user_token: Optional[str] = None) -> Dict[str, Any]:
        """
        Creates a draft email in Gmail.
        Returns the draft object including the link.
        """
        if not user_token:
            print("Error: No Google token provided for Gmail execution")
            return False

        import re
        
        description = action_data.get("description", "")
        
        # 1. Extract recipient from description if available
        recipient = action_data.get("recipient", "")
        if not recipient:
            email_match = re.search(r'[\w\.-]+@[\w\.-]+', description)
            if email_match:
                recipient = email_match.group(0)

        # 2. Format Body
        meeting_title = action_data.get("meeting_title", "our meeting")
        body = f"Hi,\n\nFollowing up on our meeting '{meeting_title}', I wanted to address this action item:\n\n{description}\n\nBest regards,"

        subject = action_data.get("subject", f"Follow up: {meeting_title}")
        
        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
            import base64
            from email.mime.text import MIMEText

            creds = Credentials(token=user_token)
            service = build('gmail', 'v1', credentials=creds)

            message = MIMEText(body)
            if recipient:
                message['To'] = recipient
            message['Subject'] = subject
            
            # Encode the message
            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            create_message = {
                'message': {
                    'raw': encoded_message
                }
            }
            
            draft = service.users().drafts().create(userId='me', body=create_message).execute()
            
            draft_id = draft.get('id')
            message_id = draft.get('message', {}).get('id')

            print(f"--- GMAIL EXECUTOR ---")
            print(f"Draft created: {draft_id}")
            print("----------------------")
            
            return {
                "success": True,
                "draft_id": draft_id,
                "link": f"https://mail.google.com/mail/u/0/#drafts?compose={message_id}"
            }
            
        except Exception as e:
            print(f"Error creating Gmail draft: {e}")
            # If 403 or 401 is encountered, it often means the token is invalid or scopes are missing
            if "403" in str(e) or "401" in str(e):
                raise Exception(f"AuthError: {str(e)}")
            return False