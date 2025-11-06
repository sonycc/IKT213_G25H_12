using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;

namespace FishAppUI.MenuFunctions
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
    internal class ToolsMenuHandlers
    {
        // <MenuItem Header ="Zoom In"                                  Click="ZoomIn_Click"/>
        private void ZoomIn_Click(object sender, RoutedEventArgs e) { /* TODO */ }      //Oscar
        
        // <MenuItem Header = "Zoom Out"                                 Click="ZoomOut_Click"/>
        private void ZoomOut_Click(object sender, RoutedEventArgs e) { /* TODO */ }      //Oscar
        
        // <MenuItem Header = "Eraser"                                   Click="Eraser_Click"/>
        private void Eraser_Click(object sender, RoutedEventArgs e) { /* TODO */ }      //sondre
        
        // <MenuItem Header = "Color Picker"                             Click="ColorPicker_Click"/>
        private void ColorPicker_Click(object sender, RoutedEventArgs e) { /* TODO */ }      //Oscar


        // <MenuItem Header = "Paint Brushes">
        // <MenuItem Header="Basic Brush"                          Click="BrushBasic_Click"/>
        private void BrushBasic_Click(object sender, RoutedEventArgs e) { /* TODO */ }      //sondre

        // <MenuItem Header = "Texture Brush"                        Click="BrushTexture_Click"/>
        private void BrushTexture_Click(object sender, RoutedEventArgs e) { /* TODO */ }      //sondre

        // <MenuItem Header = "Pattern Brush"                        Click="BrushPattern_Click"/>
        private void BrushPattern_Click(object sender, RoutedEventArgs e) { /* TODO */ }      //sondre


        // <MenuItem Header = "Text Tool"                                Click="TextTool_Click"/>
        private void TextTool_Click(object sender, RoutedEventArgs e) { /* TODO */ }      //Oscar

        // <MenuItem Header = "Gaussian Blur"                            Click="GaussianBlur_Click"/>
        private async void GaussianBlur_Click(object sender, RoutedEventArgs e) => await ApplyOperation("gaussian_blur?k_size=5");

        // <MenuItem Header = "Sobel Filter"                             Click="SobelFilter_Click"/>
        private async void SobelFilter_Click(object sender, RoutedEventArgs e) => await ApplyOperation("sobel?k_size=3");

        // <MenuItem Header = "Binary Filter (Histogram Thresholding)"   Click="BinaryFilter_Click"/>
        private async void BinaryFilter_Click(object sender, RoutedEventArgs e) => await ApplyOperation("binary");


    }
}
