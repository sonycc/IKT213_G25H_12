using Microsoft.Win32;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Reflection.Emit;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using Line = System.Windows.Shapes.Line;



namespace FishAppUI;

public partial class MainWindow : Window
{
    public string? selectedFilePath;
    public string? currentImagePath; // Path for save functionality
    public readonly HttpClient httpClient = new HttpClient { BaseAddress = new Uri("http://127.0.0.1:5000/") };
    public readonly Stack<byte[]> imageHistory = new Stack<byte[]>();
    public byte[]? originalCanvasBytes;
    public bool imageChanged = false;
    public bool imageUploadedToBackend = false;
    private WriteableBitmap? writableBitmap;


    public BrushSize CurrentBrushSize { get; private set; } = BrushSize.Small;


    private bool isPanning = false;
    private Point lastPanPosition;
    private bool isDrawing = false;
    private Point lastDrawPoint;
    private double zoomScale = 1.0;

    private SolidColorBrush paintBrush = new SolidColorBrush(Colors.Red);
    private double brushSize => CurrentBrushSize switch
    {
        BrushSize.Small => 2.0,
        BrushSize.Medium => 5.0,
        BrushSize.Large => 10.0,
        _ => 3.0
    };

    private void PaintSurface_MouseDown(object sender, MouseButtonEventArgs e)
    {
        if (e.MiddleButton == MouseButtonState.Pressed)
        {
            // Start panning
            isPanning = true;
            lastPanPosition = e.GetPosition(this);
            Mouse.Capture(PaintSurface);
            return;
        }

        if (e.LeftButton == MouseButtonState.Pressed)
        {
            isDrawing = true;
            lastDrawPoint = e.GetPosition(PaintSurface);
        }
    }

    private void PaintSurface_MouseMove(object sender, MouseEventArgs e)
    {
        if (isPanning && e.MiddleButton == MouseButtonState.Pressed)
        {
            var currentPosition = e.GetPosition(this);
            var delta = currentPosition - lastPanPosition;

            CanvasTranslateTransform.X += delta.X;
            CanvasTranslateTransform.Y += delta.Y;

            lastPanPosition = currentPosition;

            ClampPanToImageBounds();
        }

        if (isDrawing && e.LeftButton == MouseButtonState.Pressed)
        {
            var currentPoint = e.GetPosition(PaintSurface);
            var line = new Line
            {
                Stroke = paintBrush,
                StrokeThickness = brushSize,
                X1 = lastDrawPoint.X,
                Y1 = lastDrawPoint.Y,
                X2 = currentPoint.X,
                Y2 = currentPoint.Y,
                StrokeStartLineCap = PenLineCap.Round,
                StrokeEndLineCap = PenLineCap.Round
            };
            PaintSurface.Children.Add(line);
            lastDrawPoint = currentPoint;
        }
    }

    private void PaintSurface_MouseUp(object sender, MouseButtonEventArgs e)
    {
        isPanning = false;
        isDrawing = false;
        Mouse.Capture(null);
    }


    private void CanvasScrollViewer_PreviewMouseWheel(object sender, MouseWheelEventArgs e)
    {
        double zoomStep = 0.1;
        double newZoom = zoomScale + (e.Delta > 0 ? zoomStep : -zoomStep);
        newZoom = Math.Max(0.5, Math.Min(5.0, newZoom)); // Clamp zoom
        double scaleRatio = newZoom / zoomScale;
        zoomScale = newZoom;

        CanvasScaleTransform.ScaleX = zoomScale;
        CanvasScaleTransform.ScaleY = zoomScale;

        ClampPanToImageBounds();
        e.Handled = true;
    }

    private void ClampPanToImageBounds()
    {
        if (Canvas.Source is not BitmapSource bitmap)
            return;

        double imgWidth = bitmap.PixelWidth * zoomScale;
        double imgHeight = bitmap.PixelHeight * zoomScale;

        double viewWidth = CanvasScrollViewer.ViewportWidth;
        double viewHeight = CanvasScrollViewer.ViewportHeight;

        double maxOffsetX = Math.Max(0, (imgWidth - viewWidth) / 2);
        double maxOffsetY = Math.Max(0, (imgHeight - viewHeight) / 2);

        CanvasTranslateTransform.X = Math.Clamp(CanvasTranslateTransform.X, -maxOffsetX, maxOffsetX);
        CanvasTranslateTransform.Y = Math.Clamp(CanvasTranslateTransform.Y, -maxOffsetY, maxOffsetY);
    }


    public void SetBrushSize(BrushSize size)
    {
        CurrentBrushSize = size;
        // TODOO update UI brush icon
    }

    public enum BrushSize
    {
        Small,
        Medium,
        Large
    }




    // Initialize button states on startup
    private async void InitializeButtonStates()
    {
        await UpdateButtonStates();
    }

    public void SaveImageToFile(string filePath)
    {
        if (Canvas.Source is BitmapImage bitmap)
        {
            try
            {
                SaveBitmapImageToFile(bitmap, filePath);
                MessageBox.Show("Image saved successfully!", "Save Complete", MessageBoxButton.OK, MessageBoxImage.Information);
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error saving image: {ex.Message}", "Save Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }
        else
        {
            MessageBox.Show("No image to save.", "Save Error", MessageBoxButton.OK, MessageBoxImage.Warning);
        }
    }





    // Combined helper to send image operations or uploads
    public async Task ApplyImageOperationAsync(string endpoint, string? filePath = null)
    {

        if (Canvas.Source is null)
        {
            MessageBox.Show("Error: No image loaded.");
            return;
        }

        if (!imageUploadedToBackend)
        {
            if (Canvas.Source is BitmapImage bitmap)
            {
                var currentImageBytes = await GetImageBytesFromBitmap(bitmap);
                var result = await UploadImageBytesAndGetResult(currentImageBytes);
                if (result != null)
                {
                    imageUploadedToBackend = true;
                }
            }
        }

        try
        {
            // Save current canvas state before applying operation
            if (Canvas.Source is BitmapImage bitmap)
            {
                var currentImageBytes = await GetImageBytesFromBitmap(bitmap);
                imageHistory.Push(currentImageBytes);
            }

            HttpResponseMessage response;

            // If a file path is provided, upload it
            if (!string.IsNullOrEmpty(filePath) && File.Exists(filePath))
            {
                using var form = new MultipartFormDataContent();
                using var fs = File.OpenRead(filePath);
                var streamContent = new StreamContent(fs);

                // Detect proper MIME type
                var fileExt = Path.GetExtension(filePath).ToLower();
                string contentType = fileExt switch
                {
                    ".png" => "image/png",
                    ".jpg" => "image/jpeg",
                    ".jpeg" => "image/jpeg",
                    _ => "application/octet-stream"
                };
                streamContent.Headers.ContentType = new MediaTypeHeaderValue(contentType);

                form.Add(streamContent, "file", Path.GetFileName(filePath));

                response = await httpClient.PostAsync(endpoint, form);
            }
            else
            {
                // Otherwise just call the endpoint directly
                response = await httpClient.PostAsync(endpoint, null);
            }

            response.EnsureSuccessStatusCode();

            // Load the resulting image
            var imageBytes = await response.Content.ReadAsByteArrayAsync();
            var newImage = LoadImageFromBytes(imageBytes);
            if (newImage != null)
            {
                Canvas.Source = newImage;
                await UpdateButtonStates();
            }
        }
        catch (Exception ex)
        {
            MessageBox.Show($"Error: {ex.Message}", "Operation Error", MessageBoxButton.OK, MessageBoxImage.Error);
        }
    }


    // Reset button click handler
    private async void ResetMenuItem_Click(object sender, RoutedEventArgs e)
    {
        await LoadImageFromFile(currentImagePath!);
    }


    // Update button enabled states based on history
    private async Task UpdateButtonStates()
    {
        UndoMenuItem.IsEnabled = imageHistory.Count > 0;
        ResetMenuItem.IsEnabled = !string.IsNullOrEmpty(currentImagePath);
    }


    // Helper to convert BitmapImage to byte array
    private Task<byte[]> GetImageBytesFromBitmap(BitmapImage bitmap)
    {
        using var ms = new MemoryStream();
        var encoder = new PngBitmapEncoder();
        encoder.Frames.Add(BitmapFrame.Create(bitmap));
        encoder.Save(ms);
        return Task.FromResult(ms.ToArray());
    }

    // Helper to save BitmapImage to file
    private void SaveBitmapImageToFile(BitmapImage bitmap, string filePath)
    {
        var fileExt = Path.GetExtension(filePath).ToLower();

        BitmapEncoder encoder = fileExt switch
        {
            ".jpg" or ".jpeg" => new JpegBitmapEncoder(),
            ".png" => new PngBitmapEncoder(),
            _ => new PngBitmapEncoder()
        };

        encoder.Frames.Add(BitmapFrame.Create(bitmap));

        using var fileStream = new FileStream(filePath, FileMode.Create);
        encoder.Save(fileStream);
    }

    // Helper to upload image bytes to backend and get processed result
    private async Task<BitmapImage?> UploadImageBytesAndGetResult(byte[] imageBytes)
    {
        try
        {
            using var form = new MultipartFormDataContent();
            using var ms = new MemoryStream(imageBytes);
            var streamContent = new StreamContent(ms);
            streamContent.Headers.ContentType = new MediaTypeHeaderValue("image/png");

            form.Add(streamContent, "file", "image.png");

            var response = await httpClient.PostAsync("upload-image", form);
            response.EnsureSuccessStatusCode();

            var resultBytes = await response.Content.ReadAsByteArrayAsync();
            return LoadImageFromBytes(resultBytes);
        }
        catch (Exception ex)
        {
            MessageBox.Show($"Error uploading image: {ex.Message}");
            return null;
        }
    }

    // Helper to convert byte[] to BitmapImage
    private BitmapImage LoadImageFromBytes(byte[] imageBytes)
    {
        using var ms = new MemoryStream(imageBytes);
        var bitmap = new BitmapImage();
        bitmap.BeginInit();
        bitmap.CacheOption = BitmapCacheOption.OnLoad;
        bitmap.StreamSource = ms;
        bitmap.EndInit();
        bitmap.Freeze();
        return bitmap;
    }




    public async Task LoadImageFromFile(string filePath)
    {
        try
        {
            var bitmap = new BitmapImage();
            bitmap.BeginInit();
            bitmap.UriSource = new Uri(filePath, UriKind.Absolute);
            bitmap.CacheOption = BitmapCacheOption.OnLoad;
            bitmap.EndInit();
            bitmap.Freeze();

            writableBitmap = new WriteableBitmap(bitmap);
            Canvas.Source = writableBitmap;

            Canvas.Source = bitmap;
            currentImagePath = filePath;
            imageHistory.Clear();
            originalCanvasBytes = null;
            await UpdateButtonStates();
        }
        catch (Exception ex)
        {
            MessageBox.Show($"Error loading image: {ex.Message}", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
        }
    }

    internal void OpenColorPalette()
    {
        throw new NotImplementedException();
    }
}
