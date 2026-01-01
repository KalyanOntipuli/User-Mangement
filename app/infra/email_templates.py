def get_otp_template(username: str, otp: str, otp_purpose: str, otp_info: str) -> str:
    template = f"""<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge"> <!-- Ensures proper rendering in Internet Explorer -->
    <title>OTP Email</title>

    <!-- External stylesheet or inline styles can be used here, but for email, we prefer inline styles for compatibility -->
</head>

<body style="font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px 0; color: #333333;">
    <!-- Main email container: centered, with padding and shadow for better aesthetics -->
    <table align="center" width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; padding: 20px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); border-radius: 8px;">
        

        <!-- Main Image Section -->
        <tr>
            <td align="center" style="padding: 32px 0 38px 0; position: relative;">
                <!-- Main Image: Replace with your main image URL -->
            <img src="https://i.ibb.co/8WcQKV5/markwavelogo.png" alt="markwavelogo" border="0">

            </td>
        </tr>

        <!-- Body Content -->
        <tr>
            <td>
                <!-- Greeting and OTP Information -->
                <h1 style="color: #000; font-family: Inter, Arial, sans-serif; font-size: 24px; font-weight: 500; line-height: 32px; margin-bottom:32px;">
                    Dear {username},</h1>
                <p style="color: #333; margin-bottom:32px; font-family: Inter, Arial, sans-serif; font-size: 14px; line-height: 22px;">
                    {otp_info}.<br>
                    Below is your <strong>OTP</strong> for {otp_purpose}.
                </p>
            </td>
        </tr>

        <!-- OTP Display: Styled boxes for each digit -->
        <tr>
            <td align="center" style="padding: 20px 0;">
                <table cellspacing="15" cellpadding="0" border="0">
                    <tr>
                        <!-- Each OTP digit is displayed in a styled box for clarity and emphasis -->
                        {''.join([f'<td align="center" style="width: 55px; height: 55px; background: rgba(7, 95, 236, 0.05); border-radius: 5px; color: #10241B; font-size: 24px; font-family: Inter, Arial, sans-serif; font-weight: 600;">{otp[i]}</td>' for i in range(len(otp))])}
                    </tr>
                </table>
            </td>
        </tr>

        <!-- Instructions Section -->
        <tr>
            <td>
                <p style="color: #333; margin-bottom:32px; font-family: Inter, Arial, sans-serif; font-size: 14px; line-height: 22px;">
                    If you did not request this change or if you have any concerns, please contact our support team immediately.
                </p>
                <p style="color: #333; margin-bottom:32px; font-family: Inter, Arial, sans-serif; font-size: 14px; line-height: 22px;">
                    OTP will expire in <strong>5 minutes</strong>.
                </p>
                <p style="color: #333; font-family: Inter, Arial, sans-serif; font-size: 14px; line-height: 22px;">
                    Best Regards,<br>
                    <span style="color: #075FEC;">Markwave Team.</span>
                </p>
            </td>
        </tr>

        <!-- Footer Section: Social Media Links and Legal Information -->
        <tr>
            <td align="center" style="padding: 16 0 8px 0;">
                <!-- Social Media Links -->
                <div style="border-top: 1px solid #D9D9D9; margin:13px 0 10px 0; border-bottom: 1px solid #D9D9D9; height: 64px; width: 100%; text-align: center;">
                    <a href="https://markwave.ai/" target="_blank" style="text-decoration: none;">
                        <img src="https://resume-builder-be.maangtechnologies.com/images/facebook.png" style="margin-right: 10px; margin-top:18px" width="32px" alt="Facebook" class="social-icon">
                    </a>
                    <a href="https://markwave.ai/" target="_blank" style="text-decoration: none;">
                        <img src="https://resume-builder-be.maangtechnologies.com/images/instagram.png" style="margin-right: 10px;" width="32px" alt="Instagram" class="social-icon">
                    </a>
                    <a href="https://markwave.ai/" target="_blank" style="text-decoration: none;">
                        <img src="https://resume-builder-be.maangtechnologies.com/images/linkedin.png" style="margin-right: 10px;" width="32px" alt="LinkedIn" class="social-icon">
                    </a>
                </div>

                <!-- Footer Legal Information -->
                <div style="color: black; font-size: 10px; font-family: Inter, Arial, sans-serif; font-weight: 400; word-wrap: break-word; margin: 16px 0 32px 0;">
                    © 2024 <a href="https://markwave.ai/" target="_blank" style="text-decoration: none; color:black;">Markwave</a>. All rights reserved.
                </div>
                <div style="color: black; font-size: 10px; width:476px; height:36px; font-family: Inter, Arial, sans-serif; font-weight: 400; word-wrap: break-word; margin: 0 0 10px 0;">
                    You are receiving this email because you registered to join the Markwave platform as a user or a creator. By receiving this email, you agree to our Terms of Use and Privacy Policies. If you no longer wish to receive emails from us, click the unsubscribe link below to unsubscribe.
                </div>
            </td>
        </tr>

        <!-- Legal Links: Privacy, Terms of Service, etc. -->
        <tr>
            <td>
                <div style="text-align: center; font-size: 10px; color: #333333; font-family: Euclid Circular A, Arial, sans-serif; margin: 8px 0 20px 0;">
                    <div style="display: inline-block; margin: 0 5px;"><a href="#" style="color: #333;">Privacy policy</a></div>
                    <div style="display: inline-block; margin: 0 5px;"><a href="#" style="color: #333;">Terms of service</a></div>
                    <div style="display: inline-block; margin: 0 5px;"><a href="#" style="color: #333;">Help center</a></div>
                    <div style="display: inline-block; margin: 0 5px;"><a href="#" style="color: #333;">Unsubscribe</a></div>
                </div>
            </td>
        </tr>

    </table>
</body>

</html>
"""
    return template


def get_credentials_sending_template(
    username, notify_info1, notify_info2, email, password
):

    template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Login Credentials</title>
</head>
<body style="font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px 0;">
    <table align="center" width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; padding: 20px; box-shadow: 0 0 10px rgba(0,0,0,0.1); border-radius: 8px;">
        <tr>
            <td align="center" style="padding: 32px 0 38px;">
                <img src="https://i.ibb.co/8WcQKV5/markwavelogo.png" alt="markwavelogo" border="0">
            </td>
        </tr>
        <tr>
            <td>
                <h1 style="color: #000; font-size: 24px;">Dear {username},</h1>
                <p style="font-size: 14px; line-height: 22px;">{notify_info1}</p>
                <p style="font-size: 14px; line-height: 22px;">Here are your login credentials:</p>
                <p style="font-size: 14px; line-height: 22px;"><strong>Email:</strong> {email}</p>
                <p style="font-size: 14px; line-height: 22px;"><strong>Password:</strong> {password}</p>
                <p style="font-size: 14px; line-height: 22px;">Log in here: <a href="https://markwave.ai/index.html" style="color: #007bff;">Link</a></p>
                <p style="font-size: 14px; line-height: 22px;">{notify_info2}</p>
                <p style="font-size: 14px;">Best Regards,<br><span style="color: #075FEC;">Markwave Team</span></p>
            </td>
        </tr>
        <!-- Footer -->
        <tr>
            <td align="center">
                <div style="border-top: 1px solid #d9d9d9; margin: 20px 0;"></div>
                <a href="https://www.facebook.com/people/Maang_Technologies/100094655003149/" target="_blank"><img src="https://eds-be.maangtechnologies.com/images/facebook.png" width="32" alt="Facebook" style="margin: 0 5px;"></a>
                <a href="https://www.instagram.com/maang_technologies/" target="_blank"><img src="https://eds-be.maangtechnologies.com/images/instagram.png" width="32" alt="Instagram" style="margin: 0 5px;"></a>
                <a href="https://in.linkedin.com/company/maang-technologies-private-limited" target="_blank"><img src="https://eds-be.maangtechnologies.com/images/linkedin.png" width="32" alt="LinkedIn" style="margin: 0 5px;"></a>
                <div style="font-size: 10px; margin: 16px 0;">
                    © 2024 <a href="https://markwave.ai/index.html" target="_blank" style="color: black;">MARKWAVE</a>. All rights reserved.
                </div>
                <div style="font-size: 10px; color: black;">
                    You are receiving this email because you joined MARKWAVE as a user or creator. If you no longer want these messages, click unsubscribe.
                </div>
                <div style="font-size: 10px; color: #333; margin-top: 10px;">
                    <a href="#" style="color: #333; margin: 0 5px;">Privacy Policy</a> |
                    <a href="#" style="color: #333; margin: 0 5px;">Terms of Service</a> |
                    <a href="#" style="color: #333; margin: 0 5px;">Help Center</a> |
                    <a href="#" style="color: #333; margin: 0 5px;">Unsubscribe</a>
                </div>
            </td>
        </tr>
    </table>
</body>
</html>
"""
    return template
