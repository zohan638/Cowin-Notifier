
# Cowin-Notifier
 - Simply run main.exe(standalone executable), **NO NEED TO INSTALL PYTHON FOR THIS**! Just follow *How to Setup*.

 - This is a single Python3 file which will notify you regarding vaccine availability via E-mail as well as SMS!
   
 - Tested with other online services like Under45, it is definitely faster and much more reliable than that.

 - Added a main.exe file to run the script without running the main.py file!

> In my testing it notified for vaccine before it showed up on Cowin website!

  

# How to Setup:
 **Use this only if you want E-Mail and/or SMS Notifications. The actuall app WILL PRINT slot availability!**

 1. Install AirMore app on your smartphone: If you want SMS functionality [Andriod Play Store](https://play.google.com/store/apps/details?id=com.airmore).

	**Note: Your smartphone will be used to send SMS notification, carrier charges may apply.**

 3. Enter your ipaddress from AirMore app(3 dots -> Get IP) in **params.txt -> ipadress**, make sure phone and pc are on same WiFi network.

 4. Setup a dummy Gmail account: If you want E-Mail functionality. Turn on less secure apps on the Gmail account. [Link](https://support.google.com/accounts/answer/6010255?hl=en)
 
 5. Enter your Email ID in **params.txt -> gmail_user**.
 
 6. Enter your Password in **params.txt -> gmail_password**.
 
 7. Enter the number of days after which you want to check availability in **params.txt -> period**.
 
 8. Enter the amount of delay in seconds after which you want to check for update **params.txt -> speed.**

	 **Note: do not reduce under 3 seconds. 10 seconds is what I tested for.**

  

# How to run:
1. Make sure you have `python3` and `pip3` installed on your machine.

2. Run: `pip3 install -r requirements.txt`

3. Update **params.txt** file, Look at *Setup*.

4. Run: `python main.py` OR `Open main.exe`