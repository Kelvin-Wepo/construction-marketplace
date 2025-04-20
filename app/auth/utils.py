import os
import africastalking
import random

# Initialize Africa's Talking
username = os.environ.get('AT_USERNAME', 'sandbox')
api_key = os.environ.get('AT_API_KEY', 'your_api_key')

africastalking.initialize(username, api_key)
sms = africastalking.SMS

def send_otp(phone_number, otp):
    """Send OTP via Africa's Talking SMS API"""
    try:
        # Format the message
        message = f"Your Construction Marketplace verification code is: {otp}"
        
        # Send the message
        response = sms.send(message, [phone_number])
        return response
    except Exception as e:
        print(f"Error sending OTP: {e}")
        return None

def verify_otp(provided_otp, stored_otp):
    """Verify if the provided OTP matches the stored OTP"""
    return provided_otp == stored_otp
