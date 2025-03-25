using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using SecuGen.FDxSDKPro.Windows;
using Microsoft.AspNetCore.Mvc;
using System;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddControllers();
var app = builder.Build();

app.UseRouting();
app.UseEndpoints(endpoints => endpoints.MapControllers());
app.Run();

[ApiController]
[Route("api")]
public class FingerprintController : ControllerBase
{
    private readonly SGFingerPrintManager _fpm;

    public FingerprintController()
    {
        _fpm = new SGFingerPrintManager();
        _fpm.Init(SGFPMDeviceName.DEV_AUTO);
        _fpm.OpenDevice((int)SGFPMPortAddr.USB_AUTO_DETECT);
    }

    [HttpPost("capture")]
    public IActionResult Capture()
    {
        try
        {
            byte[] imageBuffer = new byte[400 * 400];
            int error = _fpm.GetImage(imageBuffer);
            if (error != (int)SGFPMError.ERROR_NONE)
            {
                return BadRequest(new { error = "Error al capturar la huella" });
            }

            byte[] template = new byte[400];
            error = _fpm.CreateTemplate(null, imageBuffer, template);
            if (error != (int)SGFPMError.ERROR_NONE)
            {
                return BadRequest(new { error = "Error al crear la plantilla" });
            }

            return Ok(new { template = Convert.ToBase64String(template) });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { error = ex.Message });
        }
    }

    [HttpPost("match")]
    public IActionResult Match([FromBody] MatchRequest request)
    {
        try
        {
            byte[] template1 = Convert.FromBase64String(request.Template1);
            byte[] template2 = Convert.FromBase64String(request.Template2);
            bool matched = false;
            int score = 0;
            int error = _fpm.MatchTemplate(template1, template2, SGFPMSECURITYLEVEL.SL_NORMAL, ref matched, ref score);
            if (error != (int)SGFPMError.ERROR_NONE)
            {
                return BadRequest(new { error = "Error al comparar las plantillas" });
            }

            return Ok(new { matched, score });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { error = ex.Message });
        }
    }
}

public class MatchRequest
{
    public string Template1 { get; set; }
    public string Template2 { get; set; }
}