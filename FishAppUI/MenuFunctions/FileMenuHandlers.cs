using Microsoft.Win32;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media.Imaging;

using FishAppUI;

namespace FishAppUI;

/*
<!-- File Menu -->
<MenuItem Header="File">
    <MenuItem Header="New"          Click="FileNew_Click"/> 
    <MenuItem Header="Open"         Click="FileOpen_Click"/>
    <MenuItem Header="Save"         Click="FileSave_Click"/>
    <MenuItem Header="Save As"      Click="FileSaveAs_Click"/>
    <Separator/>
    <MenuItem Header="Properties"   Click="FileProperties_Click"/>
    <Separator/>
    <MenuItem Header="Quit"         Click="FileQuit_Click"/>
</MenuItem>
*/
public partial class MainWindow
{


    // <MenuItem Header="New"          Click="FileNew_Click"/> 

    public async void FileNew_Click(object sender, RoutedEventArgs e)
    {
        var dialog = new NewImageDialog { Owner = this };

        if (dialog.ShowDialog() == true)
        {
            int width = dialog.ImageWidth;
            int height = dialog.ImageHeight;
            string imageType = dialog.ImageType;

            try
            {
                // Reuse MainWindow’s ApplyImageOperationAsync for backend call
                string endpoint = $"newImage?width={width}&height={height}&type={imageType}";
                await ApplyImageOperationAsync(endpoint);

                MessageBox.Show("New image created successfully!", "Success",
                    MessageBoxButton.OK, MessageBoxImage.Information);
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Failed to create new image:\n{ex.Message}",
                    "Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }
    }

    // <MenuItem Header = "Open"         Click="FileOpen_Click"/>

    public async void FileOpen_Click(object sender, RoutedEventArgs e)
    {
        OpenFileDialog openFileDialog = new OpenFileDialog();
        openFileDialog.Filter = "Image Files|*.jpg;*.jpeg;*.png;*.bmp;*.gif|All Files|*.*";
        if (openFileDialog.ShowDialog() == true)
        {
            await LoadImageFromFile(openFileDialog.FileName);
        }
    }

    // <MenuItem Header = "Save"         Click="FileSave_Click"/>
    public void FileSave_Click(object sender, RoutedEventArgs e)
    {
        if (string.IsNullOrEmpty(currentImagePath))
        {
            FileSaveAs_Click(sender, e);
        }
        else
        {
            SaveImageToFile(currentImagePath);
        }
    }

    // <MenuItem Header = "Save As"      Click="FileSaveAs_Click"/>
    public void FileSaveAs_Click(object sender, RoutedEventArgs e)
    {
        SaveFileDialog saveFileDialog = new SaveFileDialog();
        saveFileDialog.Filter = "PNG Image|*.png|JPEG Image|*.jpg|BMP Image|*.bmp|All Files|*.*";
        saveFileDialog.DefaultExt = "png";

        if (saveFileDialog.ShowDialog() == true)
        {
            currentImagePath = saveFileDialog.FileName;
            SaveImageToFile(currentImagePath);
        }
    }

    // <MenuItem Header = "Properties"   Click="FileProperties_Click"/>
    public void FileProperties_Click(object sender, RoutedEventArgs e)
    {
        if (Canvas.Source is WriteableBitmap bitmap)
        {
            var properties = $"Width: {bitmap.PixelWidth}px\n" +
                           $"Height: {bitmap.PixelHeight}px\n" +
                           $"DPI X: {bitmap.DpiX}\n" +
                           $"DPI Y: {bitmap.DpiY}\n" +
                           $"Format: {bitmap.Format}\n" +
                           $"Path: {currentImagePath ?? "Not saved"}";

            MessageBox.Show(properties, "Image Properties", MessageBoxButton.OK, MessageBoxImage.Information);
        }
        else
        {
            MessageBox.Show("No image loaded.", "Properties", MessageBoxButton.OK, MessageBoxImage.Warning);
        }
    }

    // <MenuItem Header = "Quit"         Click="FileQuit_Click"/>
    public void FileQuit_Click(object sender, RoutedEventArgs e)
    {
        Application.Current.Shutdown();
    }


}
