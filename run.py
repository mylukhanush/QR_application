import qrcode
import os
import socket
from app import create_app

app = create_app()

def get_local_ip():
    """Attempts to get the local IP address of the machine"""
    try:
        # Connect to a public DNS server to determine the best local IP
        # This doesn't actually make a connection
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"

def generate_qr_codes():
    """Generates the two permanent QR codes"""
    local_ip = get_local_ip()
    base_url = f"http://{local_ip}:5000"
    
    print(f"Creating QR codes linked to: {base_url}")
    print("IMPORTANT: Your mobile and computer must be on the SAME WiFi network.")
    
    # 1. Registration QR
    reg_url = f"{base_url}/register"
    qr_reg = qrcode.make(reg_url)
    qr_reg.save("app/static/registration_qr.png")
    print(f"Generated Registration QR: app/static/registration_qr.png -> {reg_url}")
    
    # 2. Check-In QR
    checkin_url = f"{base_url}/checkin"
    qr_checkin = qrcode.make(checkin_url)
    qr_checkin.save("app/static/entry_qr.png")
    print(f"Generated Entry QR: app/static/entry_qr.png -> {checkin_url}")

if __name__ == "__main__":
    # Always regenerate QRs on startup to ensure IP is correct if network changed
    print("Generating QR Codes...")
    generate_qr_codes()
        
    print("Starting Flask Server...")
    # NOTE: Run with host='0.0.0.0' to allow access from other devices (like mobile phones)
    app.run(debug=True, host='0.0.0.0', port=5000)
