using System;
using System.IO;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Threading.Tasks;
using System.Windows;
using Microsoft.Win32;
using System.Windows.Media.Imaging;

namespace FishAppUI
{
    public partial class MainWindow : Window
    {
        private string selectedFilePath;
        private readonly HttpClient httpClient = new HttpClient { BaseAddress = new Uri("http://127.0.0.1:5000/") };

        public MainWindow()
        {
            InitializeComponent();
        }

        // Select an image from disk
        private void SelectButton_Click(object sender, RoutedEventArgs e)
        {
            OpenFileDialog openFileDialog = new OpenFileDialog();
            openFileDialog.Filter = "Image Files|*.jpg;*.jpeg;*.png";
            if (openFileDialog.ShowDialog() == true)
            {
                selectedFilePath = openFileDialog.FileName;
                OriginalImage.Source = new BitmapImage(new Uri(selectedFilePath));
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
            if (processedBitmap != null) ProcessedImage.Source = processedBitmap;
        }

        // Rotate / Grayscale buttons
        private async void Rotate90Button_Click(object sender, RoutedEventArgs e) => await ApplyOperation("rotate?angle=90");
        private async void Rotate180Button_Click(object sender, RoutedEventArgs e) => await ApplyOperation("rotate?angle=180");
        private async void Rotate270Button_Click(object sender, RoutedEventArgs e) => await ApplyOperation("rotate?angle=270");
        private async void GrayscaleButton_Click(object sender, RoutedEventArgs e) => await ApplyOperation("grayscale");

        // Helper to call backend endpoints for operations
        private async Task ApplyOperation(string endpoint)
        {
            try
            {
                var response = await httpClient.PostAsync(endpoint, null);
                response.EnsureSuccessStatusCode();

                var imageBytes = await response.Content.ReadAsByteArrayAsync();
                ProcessedImage.Source = LoadImageFromBytes(imageBytes);
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error: {ex.Message}");
            }
        }

        // Helper to upload image file to backend
        private async Task<BitmapImage> PostFileAndGetImage(string endpoint, string filePath)
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
    }
}
