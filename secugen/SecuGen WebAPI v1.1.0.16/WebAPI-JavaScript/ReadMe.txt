
SecuGen Web API


# Introduction 
SecuGen Web API Service {SgiBioSrv} is a web based product that provides fingerprint authentication to Web Applications.

IMPORTANT: Please enter any bugs or feature requests by clicking the (+) symbol to the right of "SW_WebAPI" in the column to the left of this page.

# Getting started
Refer to the following repository:
[SecuGen Web API] https://secugen.visualstudio.com/_git/SW_WebAPI

# Release Notes
# 3:13 PM 7/30/2024
# v1.1.0.16

# Major fixes that are included:
- Fix of build process to get WebAPI-Unity20 ->WebAPI_Config.exe<- that user can either run from that location, or use 
  installer to install on client system.


# Release Notes
# 8:43 AM 7/26/2024
# v1.1.0.15

# Major fixes that are included:
- Re-vert WebAPI demo site back to using framework v4.6.1

# Release Notes
# 4:35 PM 7/22/2024
# v1.1.0.14

# Major fixes that are included:
- Re-worked SPP configuration to be a command line parameter
- Re-worked WebAPI-Unity20.exe config tool to build proper registry key to reboot to allow proper start up parameters
- Updated FDxSDKPro to latest release, giving WebAPI U20-AL support.
- Added WIX installer code to WebAPI-Unity20.exe (x86/x64 installer)
- WebAPIDemo site -> Was forced to upgrade to framework 4.8.1, server side upgrade.
-- https://dotnet.microsoft.com/en-us/download/dotnet-framework/thank-you/net481-web-installer
- Working to get WebAPI-Unity20.exe moved out to Microsoft store for end user download
- Upgraded FDxSDKPro on WebAPI-Unity20
- WebAPI-Unity20; only display valid COM ports on the local system


# Release Notes
# 5:17 PM 6/6/2024
# v1.1.0.12

# Major fixes that are included:
- Added support for Unity 20 SPP -> C:\Program Files\Secugen\SgiBioSrv\Comport.txt
- Added WebAPI-Unity20.exe config tool to allow users to set comport.txt
- This changes are usable on WebAPI-Javascript/WebAPIPython/WebAPI-1-n.


# Release Notes
# 2:32 PM 5/23/2024
# v1.1.0.11

# Major fixes that are included:
- Python/Javascript:  Error handling to alert user to web api client not installed.
- Python/Javascript:  Fix text errors/mis-spellings web site.
- Python/Javascript:  Added deployment directions.


# Release Notes
# 11:32 AM 5/17/2024
# v1.1.0.10

# Major fixes that are included:
- Added Python/Javascript web site to bundle.  
- Added link on Javascript web page header to allow users to go to Python/Javascript web site.
- WebAPI is compiled with VS2022; Microsoft compiler v14.3

# Release Notes
# 3:53 PM 11/28/2023
# v1.1.0.08

# Major fixes that are included:
- Changed SgiBioSrv logging from DebugView to output to a file.  C:\Program Files\SecuGen\SgiBioSrv\Logs\trace-#####.txt
- Removal of SGIFPEnroll web method.  Didn't work correctly, and 28076 was wanting this web method removed.


# Release Notes
# 11:18 AM 11/11/2022
# v1.1.0.07

# Major fixes that are included:
- Clean up site.master.  Had an extra license string listed there, and it was active on demo site (shouldn't have been)
- Minor verion number fixes.
- Moved from v1.1.0.06 -> v1.1.0.07


# Release Notes
# 4:21 PM 11/7/2022
# v1.1.0.06


# Major fixes that are included:
- Upgraded FDxSDKPro from v4.8.0.0 to v4.8.2.1
- Fixed digital signage issue on the installs
- Dropped the NON SSL client installs and now no longer ship the port 8000 communications of WebAPI
- Slight visual changes to web site now that WebAPI-1-N are also coming up and online.
- Bump client installs from v1.1.0.04 to v1.1.0.06


# Release Notes
# 4:50 PM 8/6/2021
# v1.1.0.04

# Major fixes that are included:
- Added support for Hamster Air
- Increased image buffer because Ham Air requires the larger image
- Now retrieve HInstance on the fly, as opposed to using saved off tWinMain(...)
- Upgraded FDxSDKPro, v4800, that is also compiled with VS2015
- Upgraded SgFpAMX.dll to allow for fewer munutia points.


# Release Notes
# 12:43 PM 4/29/2021
# WebAPI v1.1.0.02

# Major fixes that are included:
- Support for Firefox browser (verified on v88)
- Altered the way on which SgiBioSrv.exe SSL certificate was built.
- Updated SgiBioSrv versions to v1.1.0.02

# Release Notes
# 12:52 PM 4/16/2021
# WebAPI v1.1.0.01


# Major fixes that are included:
- Build process now builds a SSL certificate with 35 yr lifespan.  Build date + 35 yrs; Currently expires Apr 2056
- System tray icon now has Warning and Error indicators when some issues are detectable.  (Currently SSL certificate expiring)
- Cleaned up some of the warnings during compile of SgiBioSrv.exe.
- Updated SgiBioSrv versions to v1.1.0.01


# Release Notes
# 10:55 AM 3/28/2021
# WebAPI v1.0.0.89

# Major fixes that are included:
- SgiBioSrv/WebAPI - Self signed certificate expired on 3/26/21.  Updated certificate to have an extended life span.
- Added Debug Levels 1 = fingerprint capture debugging
- Added Debug Levels 99 = Debug ALL mode
- Updated SgiBioSrv versions to v1.0.0.89.


# Release Notes
# 05:20 PM 7/27/2020
# WebAPI v1.0.0.83

# Major fixes that are included:
- SgiBioSrv/WebAPI - Updated OpenSSL to use TLS 1.2 at runtime {openssl.com}
- Chrome v84 was pushed out during week of 7/20/20, this warns users of limited support of TLS 1.0 and TLS 1.1.
- Inno installer compiler upgraded from v5 to v6.0.4u
- Updated SgiBioSrv versions to v1.0.0.83.


# Release Notes
# 10:16 AM 4/25/2020
# WebAPI v1.0.0.80

# Major fixes that are included:
- Upgraded SgFpLib.dll to v4.6
- Modified Demo2 page to allow new capture parameter, fakeDetection.
- Modified SgiBioSrv to accept input parameter, fakeDetection.
- Updated SgiBioSrv versions to v1.0.0.80.

# Release Notes
# 12:46 PM 2/19/2020
## Web API v1.0.0.78

# Major fixes that are included:
- Added support for WebAPI client software to allow IE11, that doesn't send the origin-header with requests to SgiBioSrv process.
- Bumped client installs to v1.0.0.78

# Release Notes
# 3:35 PM 5/10/2019
## Web API v1.0.0.72

# Major fixes that are included:
- Added libraries so that client install has no other dependencies.  (was dependent on vcruntime140.dll)
- Add command line -dl:7 - display license information to DbgView.exe
- Bumped client installs to v1.0.0.72
- Changed application version to v1.0.0.23

# Release Notes
# 2:10 PM 4/18/2019
## Web API v1.0.0.68

# Major fixes that are included:
- Changed NFIQ from Quality Image quality based score to calculated from NFIQ.dll
- Bumped client installs to v1.0.0.68
- Changed application version to v1.0.0.22

# Release Notes
# 2:22 PM 4/17/2019
## Web API v1.0.0.67

# Major fixes that are included:
- Now reading from Origin Header as opposed to reading from Referer Header
- Bumped client installs to v1.0.0.67
- Changed application version to v1.0.0.21

# Release Notes
# 11:00 PM 4/8/2019
## Web API v1.0.0.64

# Major fixes that are included:
- fixed version of sgfplib.dll
- Bumped client installs to v1.0.0.64
- Changed application version to v1.0.0.19


# Release Notes
# 11:23 AM 4/2/2019
## Web API v1.0.0.62

# Major fixes that are included:
- Updated documentation
- Bumped client installs to v1.0.0.62
- Chagned application version to v1.0.0.18

# Release Notes
# 4:49 PM 4/1/2019
## Web API v1.0.0.61

# Major fixes that are included:
- Added WSQ image compression on Demo1 - 0.75 = WSQ_BITRATE_15_TO_1
- Added WSQ image compression on Demo2 - 2.25 = WSQ_BITRATE_5_TO_1
- Bumped client installs to v1.0.0.61
- Changed application version of WebAPI to 1.0.0.17
- Visual Changes on web pages demo1 and demo2
- SgiBioSrv.exe changes to make EncodeWSQ API call into FdxSDKPro

# Release Notes
# 5:53 PM 3/25/2019
## Web API v1.0.0.56

# Major fixes that are included:
- Upgrade SgiBioSrv of FDxSDK Pro to v4.5.9.1
- Removal of the 'unreferenced local variable' warnings when compiling SgiBioSrv {win32, x64}
- Changed version of SgiBioSrv 1.0.0.15

version:  1.0.0.54

1:59 PM 12/14/2018
1.  Bugs were introduced with first code drop of SgiBioSrv, v1.0.0.41, this build fixes those.
2.  Compile warnings for sgibiosrv were not resolved, as future code drops will re-introduce those.
3.  SgiBioSrv did have SgFpLib.dll upgraded to keep the larger device support.


# Getting Started
* [SecuGen WebAPI Demo](https://webapi.secugen.com)
* [SecuGen WebAPI SDK Download](http://www.secugen.com)

# Release Notes
## WebAPI v1.0.0.51 Release (2018-10-25)

* Windows 64bit - FDU03, FDU04, U20, U20A, U10, U10AP, UPx, U20AP
* Windows 32bit - FDU03, FDU04, U20, U20A, U10, U10AP, UPx, U20AP


SecuGen Web API

version:  1.0.0.51
1:59 PM 11/05/2018
1.  Got SgiBioSrv source code drop from 8/30/18 from Roy.
2.  Build script does all steps of build from assembling the host web site, compiling the SgiBioSrv's, all 4, to then building single zip file to publish for sales and Azure host web site for Secugen demo's.
3.  Additional device support of U20A, U20AP, and U10AP.

SecuGen Web API

version:  1.0.0.40


1:50 PM 3/28/2018


List of current Issues:

1.  Opera browser is also currently not supported
- Opera 47.0.2631.55

2.  
List of known supported browsers:

- Google Chrome v65.0.3325.181 (64-bit)

- Microsoft Internet Explorer 11.540.15063.0

- Microsoft Edge 40.15063.0.0
- Firefox Quantum v60.0b7 (64-bit)

- Firefox Developer Edition v60.0b7 (64-bit)

For Firefox browser support, the SCI.com Certificate must be installed in the browser.


1.  Once Firefox browser is up, click the "Open Menu" button on right hand side.  This is the 3 horizontal bars button.

2.  Select Options.
3.  On the left hand side, click on Privacy & Security.

4.  On the bottom of the web page, click "View Certificates".

5.  Click on the Authorities Tab.

6.  Click on the Import button.
7.  Navigate to the application directory.  Usually "C:\Program Files\SecuGen\SgiBioSrv" or "C:\Program Files (x86)\SecuGen\SgiBioSrv".  Click on Sgica.crt.

Restart browser.



