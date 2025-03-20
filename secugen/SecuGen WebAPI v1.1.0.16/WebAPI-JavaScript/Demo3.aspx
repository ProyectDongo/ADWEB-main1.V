<%@ Page Title="Secugen-Demo3" Language="C#" MasterPageFile="~/Site.Master" AutoEventWireup="true" CodeFile="Demo3.aspx.cs" Inherits="Demo3" %>
<asp:Content ID="BodyContent" ContentPlaceHolderID="MainContent" runat="server">


<!DOCTYPE html>

<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>Demo3</title>
</head>
<body>
    <div class="row">
        <div class="row" style="text-indent: 50px;">
            <h1><b>WebAPI</b></h1>
        </div>
        <h3><b>Demonstration of Fingerprint Matching</b></h3>
        <div class="col-md-10">
            <p>
                <b>This demo scans 2 fingerprints for matching, compares them with each other, and returns a matching score.</b>
            </p>
            <table width="1012" border="0" align="center" cellpadding="0" cellspacing="0">
            <tr>
                <td class="auto-style2" align="right" valign="top">
               	    <b>Input parameters</b>
                    <br><br>
		             Match Score<input type='text' id=quality size=10 value="100"> <br><br>
                </td>
                <td class="style3" align="left">
                    <span class="download_href"> 
                    <center>
		                <img border="2" id="FPImage1" alt="Fingerpint Image" height=300 width=210 src=".\Images\PlaceFinger.bmp" > 
		                <img border="2" id="FPImage2" alt="Fingerpint Image" height=300 width=210 src=".\Images\PlaceFinger2.bmp" > <br>
		                <input type="button" value="Click to Scan" onclick="CallSGIFPGetData(SuccessFunc1, ErrorFunc)"> 
		                <input type="button" value="Click to Scan" onclick="CallSGIFPGetData(SuccessFunc2, ErrorFunc)"> <br><br>
		                <input type="button" value="Click to Match" onclick="matchScore(succMatch, failureFunc)"> <br><br>
		                <div style=" color:black; padding:20px;">
		                    <p id="result1"> </p>
		                    <p id="result2"> </p>
		                </div>
		            </center>
                    </span>
                </td>
                <td>&nbsp;</td>
            </tr>
            </table>
        </div>
    </div>
</body>
<script type="text/javascript">
    var template_1 = "";
    var template_2 = "";

    function SuccessFunc1(result) {
        if (result.ErrorCode == 0) {
            /* 	Display BMP data in image tag
                BMP data is in base 64 format 
            */
            if (result != null && result.BMPBase64.length > 0) {
                document.getElementById('FPImage1').src = "data:image/bmp;base64," + result.BMPBase64;
            }
            template_1 = result.TemplateBase64;
        }
        else {
            alert("Fingerprint Capture Error Code:  " + result.ErrorCode + ".\nDescription:  " + ErrorCodeToString(result.ErrorCode) + ".");
        }
    }

    function SuccessFunc2(result) {
        if (result.ErrorCode == 0) {
            /* 	Display BMP data in image tag
                BMP data is in base 64 format 
            */
            if (result != null && result.BMPBase64.length > 0) {
                document.getElementById('FPImage2').src = "data:image/bmp;base64," + result.BMPBase64;
            }
            template_2 = result.TemplateBase64;
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
        var params = "Timeout=" + "10000";
        params += "&Quality=" + "50";
        params += "&licstr=" + encodeURIComponent(secugen_lic);
        params += "&templateFormat=" + "ISO";
        xmlhttp.open("POST", uri, true);
        xmlhttp.send(params);
    }

    function matchScore(succFunction, failFunction) {
        if (template_1 == "" || template_2 == "") {
            alert("Please scan two fingers to verify!!");
            return;
        }
        var uri = "https://localhost:8443/SGIMatchScore";

        var xmlhttp = new XMLHttpRequest();
        xmlhttp.onreadystatechange = function () {
            if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
                fpobject = JSON.parse(xmlhttp.responseText);
                succFunction(fpobject);
            }
            else if (xmlhttp.status == 404) {
                failFunction(xmlhttp.status)
            }
        }

        xmlhttp.onerror = function () {
            failFunction(xmlhttp.status);
        }
        var params = "template1=" + encodeURIComponent(template_1);
        params += "&template2=" + encodeURIComponent(template_2);
        params += "&licstr=" + encodeURIComponent(secugen_lic);
        params += "&templateFormat=" + "ISO";
        xmlhttp.open("POST", uri, false);
        xmlhttp.send(params);
    }

    function succMatch(result) {
        var idQuality = document.getElementById("quality").value;
        if (result.ErrorCode == 0) {
            if (result.MatchingScore >= idQuality)
                alert("MATCHED ! (" + result.MatchingScore + ")");
            else
                alert("NOT MATCHED ! (" + result.MatchingScore + ")");
        }
        else {
            alert("Error Scanning Fingerprint ErrorCode = " + result.ErrorCode);
        }
    }

    function failureFunc(error) {
        alert ("On Match Process, failure has been called");
    }

</script>
</html>
</asp:Content>
