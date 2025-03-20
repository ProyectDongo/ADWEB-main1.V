<%@ Page Title="Secugen-Demo2" Language="C#" MasterPageFile="~/Site.Master" AutoEventWireup="true" CodeFile="Demo2.aspx.cs" Inherits="Demo2" %>
<asp:Content ID="BodyContent" ContentPlaceHolderID="MainContent" runat="server">

<!DOCTYPE html>

<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>Demo2</title>
</head>
<body>
    <div class="row">
        <div class="row" style="text-indent: 50px;">
            <h1><b>WebAPI</b></h1>
        </div>
        <h3><b>Demonstration of Single Fingerprint Scanning with Controllable Parameters</b></h3>
        <div class="col-md-10">
            <p>
                <b>This demo runs a single fingerprint scan.  You can manage the capture process using the input parameters with the controls listed below.</b>
            </p>
            <table width="1012" border="0" align="center" cellpadding="0" cellspacing="0">
            <tr>
                <td class="auto-style2" align="right" valign="top">
               	    <b>Input parameters</b>
                    <br><br>
		                Timeout in milliseconds <input type='text' id=timeout size=10 value="10000"> <br><br>
                        Fake Finger Detection   <select id="tfakeDetect">
                                                    <option value="0">0=Disabled</option>
                                                    <option value="1">1=Touch Chip Only</option>
                                                    <option value="2">2=Touch Chip + Lowest Fake Threshold</option>
                                                    <option value="3">3=Touch Chip + Fake Threshold 2</option>
                                                    <option value="4">4=Touch Chip + Fake Threshold 3</option>
                                                    <option value="5">5=Touch Chip + Fake Threshold 4</option>
                                                    <option value="6">6=Touch Chip + Fake Threshold 5</option>
                                                    <option value="7">7=Touch Chip + Fake Threshold 6</option>
                                                    <option value="8">8=Touch Chip + Fake Threshold 7</option>
                                                    <option value="9">9=Touch Chip + Highest Fake Threshold</option>
                                                </select><br><br>
		                Quality desired         <input type='text' id=quality size=10 value="50"> <br><br>
		                Template Format 
                    <select id="tformat" > 
                        <option value="ISO">ISO-19794</option>
                        <option value="ANSI">ANSI</option>
                    </select>
                    <br><br>
                </td>
                <td class="style3" align="left">
                    <span class="download_href"> 
                    <center>
		                <img border="2" id="FPImage1" alt="Fingerpint Image" height=300 width=210 src=".\Images\PlaceFinger.bmp" > <br>
		                <input type="button" value="Click to Scan" onclick="captureFP()"> <br><br>
		                <div style=" color:black; padding:20px;">
		                    <p id="result"> </p>
		                </div>
		            </center>
                    </span>
                </td>
                <td>&nbsp;</td>
            </tr>
            <tr>
                <td class="auto-style2">&nbsp;</td>
                <td class="style3">&nbsp;</td>
                <td>&nbsp;</td>
            </tr>
        </table>
        </div>
    </div>
</body>
<script>
        function captureFP() {
            CallSGIFPGetData(SuccessFunc, ErrorFunc);
        }
        /* 
            This functions is called if the service sucessfully returns some data in JSON object
         */
        function SuccessFunc(result) {
            if (result.ErrorCode == 0) {
                /* 	Display BMP data in image tag
                    BMP data is in base 64 format 
                */
                if (result != null && result.BMPBase64.length > 0) {
                    document.getElementById("FPImage1").src = "data:image/bmp;base64," + result.BMPBase64;
                }
                var tbl = "<table border=1>";
                tbl += "<tr>";
                tbl += "<td> Serial Number of device </td>";
                tbl += "<td> <b>" + result.SerialNumber + "</b> </td>";
                tbl += "</tr>";
                tbl += "<tr>";
                tbl += "<td> Image Height</td>";
                tbl += "<td> <b>" + result.ImageHeight + "</b> </td>";
                tbl += "</tr>";
                tbl += "<tr>";
                tbl += "<td> Image Width</td>";
                tbl += "<td> <b>" + result.ImageWidth + "</b> </td>";
                tbl += "</tr>";
                tbl += "<tr>";
                tbl += "<td> Image Resolution</td>";
                tbl += "<td> <b>" + result.ImageDPI + "</b> </td>";
                tbl += "</tr>";
                tbl += "<tr>";
                tbl += "<td> Image Quality (1-100)</td>";
                tbl += "<td> <b>" + result.ImageQuality + "</b> </td>";
                tbl += "</tr>";
                tbl += "<tr>";
                tbl += "<td> NFIQ (1-5)</td>";
                tbl += "<td> <b>" + result.NFIQ + "</b> </td>";
                tbl += "</tr>";
                tbl += "<tr>";
                tbl += "<td> Template(base64)</td>";
                tbl += "<td> <b> <textarea rows=8 cols=50>" + result.TemplateBase64 + "</textarea></b> </td>";
                tbl += "</tr>";
                tbl += "<tr>";
                tbl += "<td> Image WSQ Size</td>";
                tbl += "<td> <b>" + result.WSQImageSize + "</b> </td>";
                tbl += "</tr>";
                tbl += "<tr>";
                tbl += "<td> EncodeWSQ(base64)</td>";
                tbl += "<td> <b> <textarea rows=8 cols=50>" + result.WSQImage + "</textarea></b> </td>";
                tbl += "</tr>";
                tbl += "</table>";
                document.getElementById('result').innerHTML = tbl;
            }
            else {
                alert("Fingerprint Capture Error Code:  " + result.ErrorCode + ".\nDescription:  " + ErrorCodeToString(result.ErrorCode) + ".");
            }
        }

        function ErrorFunc(status) {
            /* 	
                If you reach here, user is probabaly not running the 
                service. Redirect the user to a page where he can download the
                executable and install it. 
            */
            alert("Check if SGIBIOSRV is running; status = " + status + ":");
        }

        function CallSGIFPGetData(successCall, failCall) {
            var uri = "https://localhost:8443/SGIFPCapture"; 

            var xmlhttp = new XMLHttpRequest();
            xmlhttp.onreadystatechange = function () {
                if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
                    fpobject = JSON.parse(xmlhttp.responseText);
                    successCall(fpobject);
                }
                else if (xmlhttp.status == 404) {
                    failCall(xmlhttp.status)
                }
            }
            xmlhttp.onerror = function () {
                failCall(xmlhttp.status);
            }
            var params = "Timeout=" + document.getElementById("timeout").value;
            params += "&Quality=" + document.getElementById("quality").value;
            params += "&licstr=" + encodeURIComponent(secugen_lic);
            params += "&fakeDetection=" + document.getElementById("tfakeDetect").value;
            params += "&templateFormat=" + document.getElementById("tformat").value;
            params += "&imageWSQRate=" + "2.25";
            xmlhttp.open("POST", uri, true);
            xmlhttp.send(params);
        }

</script>
</html>
</asp:Content>
