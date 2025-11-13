using System.Windows;


namespace FishAppUI;

partial class MainWindow
{


    /*
    <!-- Tools Menu -->
    <MenuItem Header="_Tools">
        <MenuItem Header="Zoom In"                                  Click="ZoomIn_Click"/>
        <MenuItem Header="Zoom Out"                                 Click="ZoomOut_Click"/>
        <MenuItem Header="Eraser"                                   Click="Eraser_Click"/>
        <MenuItem Header="Color Picker"                             Click="ColorPicker_Click"/>
        <MenuItem Header="Paint Brushes">
            <MenuItem Header="Basic Brush"                          Click="BrushBasic_Click"/>
            <MenuItem Header="Texture Brush"                        Click="BrushTexture_Click"/>
            <MenuItem Header="Pattern Brush"                        Click="BrushPattern_Click"/>
        </MenuItem>
        <MenuItem Header="Text Tool"                                Click="TextTool_Click"/>
        <Separator/>
        <MenuItem Header="Gaussian Blur"                            Click="GaussianBlur_Click"/>
        <MenuItem Header="Sobel Filter"                             Click="SobelFilter_Click"/>
        <MenuItem Header="Binary Filter (Histogram Thresholding)"   Click="BinaryFilter_Click"/>
    </MenuItem>
    */


    // <MenuItem Header ="Zoom In"                                  Click="ZoomIn_Click"/>
    public async void ZoomIn_Click(object sender, RoutedEventArgs e) => await ApplyImageOperationAsync("zoom_in");      //Oscar

    // <MenuItem Header = "Zoom Out"                                 Click="ZoomOut_Click"/>
    public async void ZoomOut_Click(object sender, RoutedEventArgs e) => await ApplyImageOperationAsync("zoom_out");      //Oscar

    // <MenuItem Header = "Eraser"                                   Click="Eraser_Click"/>
    public void Eraser_Click(object sender, RoutedEventArgs e) { /* TODO */ }      //sondre

    // <MenuItem Header = "Color Picker"                             Click="ColorPicker_Click"/>
    public void ColorPicker_Click(object sender, RoutedEventArgs e) { /* TODO */ }      //Oscar


    // <MenuItem Header = "Paint Brushes">
    // <MenuItem Header="Basic Brush"                          Click="BrushBasic_Click"/>
    public void BrushBasic_Click(object sender, RoutedEventArgs e) { /* TODO */ }      //sondre

    // <MenuItem Header = "Texture Brush"                        Click="BrushTexture_Click"/>
    public void BrushTexture_Click(object sender, RoutedEventArgs e) { /* TODO */ }      //sondre

    // <MenuItem Header = "Pattern Brush"                        Click="BrushPattern_Click"/>
    public void BrushPattern_Click(object sender, RoutedEventArgs e) { /* TODO */ }      //sondre


    // <MenuItem Header = "Text Tool"                                Click="TextTool_Click"/>
    public void TextTool_Click(object sender, RoutedEventArgs e) { /* TODO */ }      //Oscar


    public async void Grayscale_Click(object sender, RoutedEventArgs e) => await ApplyImageOperationAsync("grayscale");
    public async void Onnx_Click(object sender, RoutedEventArgs e)
    {
        try
        {
            var response = await httpClient.GetAsync("ONNX");
            response.EnsureSuccessStatusCode();

            var json = await response.Content.ReadAsStringAsync();

            try
            {
                using var doc = System.Text.Json.JsonDocument.Parse(json);
                var preds = doc.RootElement
                    .GetProperty("onnx")
                    .GetProperty("predictions");

                var sb = new System.Text.StringBuilder();
                int rank = 1;
                foreach (var p in preds.EnumerateArray())
                {
                    var label = p.GetProperty("label").GetString();
                    var certainty = p.GetProperty("certainty").GetDouble();
                    sb.AppendLine($"#{rank} {label}: {certainty}%");
                    rank++;
                }

                OnnxResultText.Text = sb.ToString();
            }
            catch (Exception parseEx)
            {
                OnnxResultText.Text = $"Failed to parse ONNX response:\n{parseEx.Message}\n\nRaw:\n{json}";
            }
        }
        catch (Exception ex)
        {
            OnnxResultText.Text = $"Error calling ONNX:\n{ex.Message}";
        }
    }


    // <MenuItem Header = "Gaussian Blur"                            Click="GaussianBlur_Click"/>
    public async void GaussianBlur_Click(object sender, RoutedEventArgs e) => await ApplyImageOperationAsync("gaussian_blur?k_size=5");

    // <MenuItem Header = "Sobel Filter"                             Click="SobelFilter_Click"/>
    public async void SobelFilter_Click(object sender, RoutedEventArgs e) => await ApplyImageOperationAsync("sobel?k_size=3");

    // <MenuItem Header = "Binary Filter (Histogram Thresholding)"   Click="BinaryFilter_Click"/>
    public async void BinaryFilter_Click(object sender, RoutedEventArgs e) => await ApplyImageOperationAsync("binary");

}
