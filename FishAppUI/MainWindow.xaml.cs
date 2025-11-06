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
using System.Windows.Media;
using System.Windows.Media.Imaging;


namespace FishAppUI
{
    public partial class MainWindow : Window
    {
        private string? selectedFilePath;
        private string? currentImagePath; // Path for save functionality
        private readonly HttpClient httpClient = new HttpClient { BaseAddress = new Uri("http://127.0.0.1:5000/") };
        private readonly Stack<byte[]> imageHistory = new Stack<byte[]>();
        private byte[]? originalProcessedImageBytes;

        public MainWindow()
        {
            InitializeComponent();
            InitializeButtonStates();
        }

        // Initialize button states on startup
        private async void InitializeButtonStates()
        {
            await UpdateButtonStates();
        }

        // Select an image from disk
        private async void SelectButton_Click(object sender, RoutedEventArgs e)
        {
            OpenFileDialog openFileDialog = new OpenFileDialog();
            openFileDialog.Filter = "Image Files|*.jpg;*.jpeg;*.png";
            if (openFileDialog.ShowDialog() == true)
            {
                selectedFilePath = openFileDialog.FileName;
                OriginalImage.Source = new BitmapImage(new Uri(selectedFilePath));
                await UpdateButtonStates();
            }
        }

        // Upload the selected image to backend
        private async void UploadButton_Click(object sender, RoutedEventArgs e)
        {
            if (string.IsNullOrEmpty(selectedFilePath))
            {
                MessageBox.Show("Please select an image first!");
                return;
            }

            var processedBitmap = await PostFileAndGetImage("upload-image", selectedFilePath);
            if (processedBitmap != null)
            {
                // Clear history and set original processed image bytes
                imageHistory.Clear();
                originalProcessedImageBytes = await GetImageBytesFromBitmap(processedBitmap);
                ProcessedImage.Source = processedBitmap;
                await UpdateButtonStates();
            }
        }

        // Rotate / Grayscale buttons

        private async void GrayscaleButton_Click(object sender, RoutedEventArgs e) => await ApplyOperation("grayscale");

        private async void OnnxButton_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                var response = await httpClient.GetAsync("ONNX");
                response.EnsureSuccessStatusCode();

                var json = await response.Content.ReadAsStringAsync();
                MessageBox.Show(json, "ONNX Result", MessageBoxButton.OK, MessageBoxImage.Information);
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error calling ONNX: {ex.Message}", "ONNX Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        // Helper to call backend endpoints for operations
        private async Task ApplyOperation(string endpoint)
        {
            try
            {
                // Save current state to history before applying operation
                if (ProcessedImage.Source is BitmapImage bitmap)
                {
                    var currentImageBytes = await GetImageBytesFromBitmap(bitmap);
                    imageHistory.Push(currentImageBytes);
                }

                var response = await httpClient.PostAsync(endpoint, null);
                response.EnsureSuccessStatusCode();

                var imageBytes = await response.Content.ReadAsByteArrayAsync();
                ProcessedImage.Source = LoadImageFromBytes(imageBytes);
                await UpdateButtonStates();
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error: {ex.Message}");
            }
        }

        // Helper to upload image file to backend
        private async Task<BitmapImage?> PostFileAndGetImage(string endpoint, string filePath)
        {
            try
            {
                using var form = new MultipartFormDataContent();
                using var fs = File.OpenRead(filePath);
                var streamContent = new StreamContent(fs);

                // Correct MIME type
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

                var response = await httpClient.PostAsync(endpoint, form);
                response.EnsureSuccessStatusCode();

                var imageBytes = await response.Content.ReadAsByteArrayAsync();
                return LoadImageFromBytes(imageBytes);
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error: {ex.Message}");
                return null;
            }
        }


        // Undo button click handler
        private async void UndoButton_Click(object sender, RoutedEventArgs e)
        {
            if (imageHistory.Count > 0)
            {
                var previousImageBytes = imageHistory.Pop();
                var restoredBitmap = await UploadImageBytesAndGetResult(previousImageBytes);
                if (restoredBitmap != null)
                {
                    ProcessedImage.Source = restoredBitmap;
                    await UpdateButtonStates();
                }
            }
        }

        // Reset button click handler
        private async void ResetButton_Click(object sender, RoutedEventArgs e)
        {
            if (originalProcessedImageBytes != null)
            {
                imageHistory.Clear();
                var resetBitmap = await UploadImageBytesAndGetResult(originalProcessedImageBytes);
                if (resetBitmap != null)
                {
                    ProcessedImage.Source = resetBitmap;
                    await UpdateButtonStates();
                }
            }
        }

        // Download button click handler
        private void DownloadButton_Click(object sender, RoutedEventArgs e)
        {
            if (ProcessedImage.Source is BitmapImage bitmap)
            {
                SaveFileDialog saveFileDialog = new SaveFileDialog();
                saveFileDialog.Filter = "PNG Image|*.png|JPEG Image|*.jpg|All Files|*.*";
                saveFileDialog.DefaultExt = "png";
                saveFileDialog.FileName = "processed_image";

                if (saveFileDialog.ShowDialog() == true)
                {
                    try
                    {
                        SaveBitmapImageToFile(bitmap, saveFileDialog.FileName);
                        MessageBox.Show("Image saved successfully!", "Download Complete", MessageBoxButton.OK, MessageBoxImage.Information);
                    }
                    catch (Exception ex)
                    {
                        MessageBox.Show($"Error saving image: {ex.Message}", "Download Error", MessageBoxButton.OK, MessageBoxImage.Error);
                    }
                }
            }
        }

        // Update button enabled states based on history
        private async Task UpdateButtonStates()
        {
            UploadButton.IsEnabled = !string.IsNullOrEmpty(selectedFilePath);
            UndoButton.IsEnabled = imageHistory.Count > 0;
            ResetButton.IsEnabled = originalProcessedImageBytes != null && !(await IsCurrentImageOriginal());
            DownloadButton.IsEnabled = ProcessedImage.Source != null;
        }

        // Check if current image is the original uploaded image
        private async Task<bool> IsCurrentImageOriginal()
        {
            if (originalProcessedImageBytes == null || ProcessedImage.Source is not BitmapImage bitmap)
                return true;

            var currentBytes = await GetImageBytesFromBitmap(bitmap);
            return currentBytes.SequenceEqual(originalProcessedImageBytes);
        }

        // Helper to convert BitmapImage to byte array
        private Task<byte[]> GetImageBytesFromBitmap(BitmapImage bitmap)
        {
            using var ms = new MemoryStream();
            var encoder = new PngBitmapEncoder();
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




        private async Task LoadImageFromFile(string filePath)
        {
            try
            {
                var bitmap = new BitmapImage();
                bitmap.BeginInit();
                bitmap.UriSource = new Uri(filePath);
                bitmap.CacheOption = BitmapCacheOption.OnLoad;
                bitmap.EndInit();
                bitmap.Freeze();

                ProcessedImage.Source = bitmap;
                currentImagePath = filePath;
                imageHistory.Clear();
                originalProcessedImageBytes = null;
                await UpdateButtonStates();
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error loading image: {ex.Message}", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        private void SaveImageToFile(string filePath)
        {
            if (ProcessedImage.Source is BitmapImage bitmap)
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


















    }
}
