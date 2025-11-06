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

namespace FishAppUI.MenuFunctions
{
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
    internal class FileMenuHandlers
    {

        public readonly MainWindow _mainWindow;

        public FileMenuHandlers(MainWindow mainWindow)
        {
            _mainWindow = mainWindow;
        }


        // <MenuItem Header="New"          Click="FileNew_Click"/> 

        public async void FileNew_Click(object sender, RoutedEventArgs e)
        {
            var dialog = new NewImageDialog();
            if (dialog.ShowDialog() == true)
            {
                await _mainWindow.CreateNewImage(dialog.Width, dialog.Height, dialog.ImageType);
            }
        }

        // <MenuItem Header = "Open"         Click="FileOpen_Click"/>

        public async void FileOpen_Click(object sender, RoutedEventArgs e)
        {
            OpenFileDialog openFileDialog = new OpenFileDialog();
            openFileDialog.Filter = "Image Files|*.jpg;*.jpeg;*.png;*.bmp;*.gif|All Files|*.*";
            if (openFileDialog.ShowDialog() == true)
            {
                await _mainWindow.LoadImageFromFile(openFileDialog.FileName);
            }
        }

        // <MenuItem Header = "Save"         Click="FileSave_Click"/>
        public void FileSave_Click(object sender, RoutedEventArgs e)
        {
            if (string.IsNullOrEmpty(_mainWindow.currentImagePath))
            {
                FileSaveAs_Click(sender, e);
            }
            else
            {
                _mainWindow.SaveImageToFile(_mainWindow.currentImagePath);
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
                _mainWindow.currentImagePath = saveFileDialog.FileName;
                _mainWindow.SaveImageToFile(_mainWindow.currentImagePath);
            }
        }

        // <MenuItem Header = "Properties"   Click="FileProperties_Click"/>
        public void FileProperties_Click(object sender, RoutedEventArgs e)
        {
            if (_mainWindow.ProcessedImage.Source is BitmapImage bitmap)
            {
                var properties = $"Width: {bitmap.PixelWidth}px\n" +
                               $"Height: {bitmap.PixelHeight}px\n" +
                               $"DPI X: {bitmap.DpiX}\n" +
                               $"DPI Y: {bitmap.DpiY}\n" +
                               $"Format: {bitmap.Format}\n" +
                               $"Path: {_mainWindow.currentImagePath ?? "Not saved"}";

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
}
