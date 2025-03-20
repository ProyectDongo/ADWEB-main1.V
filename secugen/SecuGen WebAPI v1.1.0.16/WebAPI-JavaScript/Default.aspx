<%@ Page Title="SecuGen" Language="C#" MasterPageFile="~/Site.Master" AutoEventWireup="true" CodeFile="Default.aspx.cs" Inherits="_Default" %>
<asp:Content ID="BodyContent" ContentPlaceHolderID="MainContent" runat="server">

    <div class="row">
        <div class="row" style="text-indent: 50px;">
            <h1><b>WebAPI</b></h1>
        </div>
        <h3><b>How to Access a SecuGen Fingerprint Reader from a Browser-Based Application</b></h3>
        <div class="col-md-10">
            <p>
                The SecuGen WebAPI was designed to allow developers to easily add fingerprint functionality to their browser-based applications to help increase security and convenience for their users.
            </p>
            <p>
                In SecuGen WebAPI, JavaScript APIs are provided that are used to access the SecuGen fingerprint reader through most modern web browsers.
            </p>
            <p><b>
                Supported SecuGen Fingerprint Readers currently include:
            </b></p>
            <p style="margin-left:40px">
                Hamster Air (HU-AIR)<br>
                Hamster Pro (HUPx)<br>
                Hamster Pro 10 (HU10)<br>
                Hamster Pro 20 (HU20-A, HU20-AP, HU20-AL, HU20)<br>
                Hamster Pro 30 (HU30)<br>
                Hamster IV (HSDU04P)<br>
                Hamster Plus (HSDU03P)<br>
            </p>
            <p>
                This website provides simple demos that you use with your SecuGen fingerprint reader to perform Fingerprint Scanning and Fingerprint Matching through your web browser.
            </p>
            <p>
                Follow the <b><a href="#Instructions">instructions below </a></b>to get started.
            </p>
        </div>
    </div>

    <div class="row">
        <div class="col-md-20">
            <h5><b>ASP.NET page in Chrome</b></h5>
            <br />
            <img alt="" src="./Images/Chrome.jpg" />
        </div>
        <div class="col-md-20">
            <h5><b>ASP.NET page in MS Edge</b></h5>
            <br />
            <img alt="" src="./Images/MSEdge.jpg" />
        </div>
    </div>

    <div class="row">
        <p>
           <b>Instructions for how to run the web application demos</b>
        </p>
        <div class="col-md-10">
            <a name="Instructions"></a>
            <p>
                1.	You should have a Windows operating system (Windows 7 or later) running on your PC.
             </p>
            <p>
                2.	Connect a SecuGen fingerprint reader to your PC, and install the <b><a href="http://www.secugen.com/download/drivers.htm">driver</a></b> (you must have admin privileges).
             </p>
            <p>
                3.	Download and install one of the following Web API Clients (you must have admin privileges)
            </p>
            <p style="margin-left:40px">
                For Windows 64 bit machines <b><a href="./download/SGI_BWAPI_Win_64bit.exe">Click Here</a></b>
            </p>
            <p style="margin-left:40px">
                For Windows 32 bit machines <b><a href="./download/SGI_BWAPI_Win_32bit.exe">Click Here</a></b>
            </p>
            <p>
                4.	Click on a link below to run the demo
            </p>
            <br>
            <p>
                <b><a href="Demo1.aspx">Demo 1 </a></b>(single fingerprint scanning)
            </p>
            <p>
                <b><a href="Demo2.aspx">Demo 2 </a></b>(single fingerprint scanning with controls)
            </p>
            <p>
                <b><a href="Demo3.aspx">Demo 3 </a></b>(fingerprint matching)
            </p>
        </div>
    </div>

</asp:Content>
