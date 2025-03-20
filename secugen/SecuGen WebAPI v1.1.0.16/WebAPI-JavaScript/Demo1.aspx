<%@ Page Title="Secugen-Demo1" Language="C#" MasterPageFile="~/Site.Master" AutoEventWireup="true" CodeFile="Demo1.aspx.cs" Inherits="Demo1" %>
<asp:Content ID="BodyContent" ContentPlaceHolderID="MainContent" runat="server">

<!DOCTYPE html>

<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>Demo1</title>
</head>
<body>
    <div class="row">
        <div class="row" style="text-indent: 50px;">
            <h1><b>WebAPI</b></h1>
        </div>
        <h3><b>Demonstration of Single Fingerprint Scanning</b></h3>
        <div class="col-md-10">
            <p>
                <b>This demo runs a single fingerprint scan.  You can easily retrieve the image data, template, serial number, NFIQ value and other relevant information in a single call.</b>
            </p>
            <div class="row">
                <table width="1012" border="0" align="center" cellpadding="0" cellspacing="0">
                    <tr align="center">
                        <td class="auto-style2" align="right" valign="top">
                            &nbsp;
                        </td>
                        <td class="style3">
                        <span class="download_href"> 
                            <img id="FPImage1" alt="Fingerpint Image" height=300 width=210 align="center" src=".\Images\PlaceFinger.bmp"> <br>
                            <input type="button" value="Click to Scan" onclick="captureFP()"><br>
                            <br>
                            <p id="result"/>.
                        </span>
                        </td>
                        <td>&nbsp;</td>
                    </tr>
                    <tr>
                        <td class="style2">&nbsp;</td>
                        <td class="style3">&nbsp;</td>
                        <td>&nbsp;</td>
                    </tr>
                </table>
            </div>
        </div>
    </div>

<script type="text/javascript">

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
    alert("Check if SGIBIOSRV is running; Status = " + status + ":");

}


function CallSGIFPGetData(successCall, failCall) {
    // 8.16.2017 - At this time, only SSL client will be supported.
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
    var params = "Timeout=" + "10000";
    params += "&Quality=" + "50";
    params += "&licstr=" + encodeURIComponent(secugen_lic);
    params += "&templateFormat=" + "ISO";
    params += "&imageWSQRate=" + "0.75";
    console.log
    xmlhttp.open("POST", uri, true);
    xmlhttp.send(params);

    xmlhttp.onerror = function () {
        failCall(xmlhttp.statusText);
    }
}


</script>
</body>
</html>
</asp:Content>